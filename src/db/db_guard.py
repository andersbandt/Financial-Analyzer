"""
@file db_guard.py
@brief Pre-flight safety checks for the OneDrive-synced SQLite database.

The DB lives in a OneDrive tree shared between two machines (see CLAUDE.md,
"Working Across Two Machines"). OneDrive cannot merge two SQLite writers, so a
collision silently produces a conflict-copy file and drops one machine's writes.
Nothing in SQLite protects against this because each machine operates on its own
locally-synced copy of the file.

This module adds a layered defense, run once at startup via
``guard_database_startup()``:

  1. scan_for_conflict_copies() - LOUD hard stop if OneDrive has already made a
     conflict copy of the DB (turns silent divergence into a visible error).
  2. wait_for_sync_settled()    - if the DB file looks like OneDrive is still
     writing it, warn and wait briefly, but never longer than a timeout.
  3. check_integrity()          - PRAGMA quick_check; hard stop on a corrupt image
     before the app writes more on top of it.
  4. backup_database()          - timestamped copy to a LOCAL (non-synced) folder
     so there is always a recovery point.
  5. DBLock                     - hostname / pid / heartbeat lock file next to the
     DB; warns (and, when interactive, blocks) if the app looks open on the other
     machine.

None of this is bulletproof - the lock file itself rides OneDrive and has the
same propagation lag - but together they catch the realistic failure mode:
"I left it open on the other machine and wandered over here."

Disable everything with the ``db_guard_on_startup`` app setting (CLI: Main Dash ->
"System configuration").
"""

import atexit
import datetime
import hashlib
import json
import os
import shutil
import socket
import sqlite3
import threading
import time


class DBGuardAbort(Exception):
    """Raised when a startup check determines the app must not continue."""


# --- tuning knobs -----------------------------------------------------------

_STALE_LOCK_SECONDS = 300        # foreign lock older than this -> assume abandoned
_HEARTBEAT_INTERVAL = 60         # how often the heartbeat thread rewrites the lock
_SYNC_QUIET_SECONDS = 8          # DB file untouched this long -> "settled"
_SYNC_DEFAULT_TIMEOUT = 15.0     # max seconds wait_for_sync_settled() will block
_MAX_LOCAL_BACKUPS = 20


# --- generic helpers ------------------------------------------------------------

def _parse_iso(s):
    if not s:
        return None
    try:
        dt = datetime.datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.astimezone()
        return dt
    except Exception:
        return None


def _now():
    return datetime.datetime.now().astimezone()


def _pid_running(pid):
    """Best-effort 'is this local pid alive'. Unknown -> True (safer: more warnings)."""
    try:
        pid = int(pid)
    except (TypeError, ValueError):
        return False
    if pid <= 0:
        return False
    try:
        if os.name == "nt":
            import ctypes
            PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
            handle = ctypes.windll.kernel32.OpenProcess(
                PROCESS_QUERY_LIMITED_INFORMATION, False, pid
            )
            if not handle:
                return False
            ctypes.windll.kernel32.CloseHandle(handle)
            return True
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except Exception:
        return True


# --- 1. conflict-copy scan ----------------------------------------------------

def scan_for_conflict_copies(db_path):
    """Return a list of filenames next to db_path that look like OneDrive conflict
    copies of the database (e.g. 'financials-DESKTOP-FOO.db', 'financials (1).db')."""
    directory = os.path.dirname(db_path) or "."
    base = os.path.basename(db_path)                 # financials.db
    stem, ext = os.path.splitext(base)               # financials, .db
    stem_l, ext_l = stem.lower(), ext.lower()
    hits = []
    try:
        names = os.listdir(directory)
    except OSError:
        return hits
    for name in names:
        if name == base:
            continue
        low = name.lower()
        if not low.endswith(ext_l):          # excludes .lock, .db-journal, .tmp*, .db.backup-*
            continue
        if not low.startswith(stem_l):
            continue
        hits.append(name)
    return sorted(hits)


def _print_conflict_banner(db_path, hits):
    line = "!" * 74
    print("\n" + line)
    print("!!!  DATABASE CONFLICT COPIES DETECTED  --  REFUSING TO START  !!!")
    print(line)
    print(f"\n  Database folder : {os.path.dirname(db_path)}")
    print(f"  Real database   : {os.path.basename(db_path)}")
    print(f"  Conflict copies : {len(hits)} file(s) found alongside it:")
    for h in hits:
        print(f"       - {h}")
    print(
        "\n  OneDrive created these because financials.db was changed on two\n"
        "  machines before syncing. Each copy may hold edits the others don't.\n"
        "  Nothing is lost YET, but you must reconcile by hand:\n\n"
        "    1. Close Financial-Analyzer on BOTH machines.\n"
        "    2. Work out which file has the edits you want -- compare file dates,\n"
        "       or open them with a SQLite browser.\n"
        "    3. Rename the good one to 'financials.db'. Move the others OUT of\n"
        "       this folder (keep them somewhere safe until you're certain).\n"
        "    4. Wait for OneDrive to finish syncing (green check) on both\n"
        "       machines before reopening the app.\n"
    )
    print(line + "\n")


# --- 2. sync-settled check (Tier 3, always bounded) --------------------------

def wait_for_sync_settled(db_path, timeout=_SYNC_DEFAULT_TIMEOUT):
    """If the DB file looks like OneDrive is mid-write, wait for it to go quiet -
    but never block longer than `timeout` seconds. Purely advisory: never raises."""
    try:
        if not os.path.isfile(db_path):
            return
        deadline = time.monotonic() + max(0.0, timeout)
        warned = False
        while True:
            age = time.time() - os.path.getmtime(db_path)
            journal = os.path.exists(db_path + "-journal")
            if age >= _SYNC_QUIET_SECONDS and not journal:
                if warned:
                    print("  [db_guard] database looks settled -- continuing.")
                return
            if time.monotonic() >= deadline:
                extra = ", -journal file present" if journal else ""
                print(f"  [db_guard] WARNING: database still looks active after "
                      f"{timeout:.0f}s (last change {age:.0f}s ago{extra}).")
                print("  [db_guard] OneDrive may still be syncing. If you just used "
                      "the app on the other\n"
                      "             machine, quit now and wait for the green "
                      "checkmark. Continuing anyway.")
                return
            if not warned:
                print(f"  [db_guard] database changed {age:.0f}s ago -- waiting up "
                      f"to {timeout:.0f}s for OneDrive to settle...")
                warned = True
            time.sleep(1.5)
    except Exception as e:
        print(f"  [db_guard] sync-settle check skipped: {e}")


# --- 3. integrity check -----------------------------------------------------

def _print_integrity_banner(db_path, details):
    line = "!" * 74
    print("\n" + line)
    print("!!!  DATABASE FAILED INTEGRITY CHECK  --  REFUSING TO START  !!!")
    print(line)
    print(f"\n  Database : {db_path}")
    print("  PRAGMA quick_check reported:")
    for d in details[:10]:
        print(f"       {d}")
    print(
        "\n  The database image looks corrupt. Do NOT keep using it -- writes now\n"
        "  could make things worse. Restore the most recent good copy from the\n"
        "  local backup folder:\n"
        f"       {_backup_dir()}\n"
        "  (or a OneDrive version-history copy), then restart.\n"
    )
    print(line + "\n")


def check_integrity(db_path):
    if not os.path.isfile(db_path) or os.path.getsize(db_path) == 0:
        return  # brand-new / not-yet-created DB
    try:
        conn = sqlite3.connect(db_path)
        try:
            rows = conn.execute("PRAGMA quick_check").fetchall()
        finally:
            conn.close()
    except sqlite3.DatabaseError as e:
        _print_integrity_banner(db_path, [str(e)])
        raise DBGuardAbort("database failed integrity check")
    result = [str(r[0]) for r in rows]
    if result != ["ok"]:
        _print_integrity_banner(db_path, result)
        raise DBGuardAbort("database failed integrity check")


# --- database fingerprint (eyeball "are both machines on the same DB?") --------

def database_fingerprint(db_path):
    """Content hash of the DB file. Same code on two machines == identical DB
    contents. Returns a dict with 'code' / 'sha256' / 'size' / 'mtime', or
    {'error': ...}, or None if the file doesn't exist yet."""
    try:
        if not os.path.isfile(db_path):
            return None
        h = hashlib.sha256()
        size = 0
        with open(db_path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
                size += len(chunk)
        digest = h.hexdigest()
        short = digest[:12].upper()
        code = "-".join(short[i:i + 4] for i in range(0, 12, 4))
        # UTC so the line is identical on both machines regardless of their tz
        mtime = datetime.datetime.utcfromtimestamp(
            os.path.getmtime(db_path)
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
        return {"code": code, "sha256": digest, "size": size, "mtime": mtime}
    except Exception as e:
        return {"error": str(e)}


def print_database_fingerprint(db_path):
    fp = database_fingerprint(db_path)
    if fp is None:
        return
    if "error" in fp:
        print(f"  [db_guard] could not fingerprint the database: {fp['error']}")
        return
    bar = "=" * 52
    print("\n  " + bar)
    print(f"  DB FINGERPRINT :  {fp['code']}")
    print(f"  size | changed :  {fp['size']:,} bytes  |  {fp['mtime']}")
    print("  " + bar)
    print("  Start the app on the other machine and check this line -- a")
    print("  matching code means both machines see the same database.\n")


# --- 4. local backup ------------------------------------------------------------

def _backup_dir():
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    d = os.path.join(base, "Financial-Analyzer", "db-backups")
    try:
        os.makedirs(d, exist_ok=True)
    except OSError:
        pass
    return d


def _prune_backups(directory, stem):
    try:
        files = sorted(
            (os.path.join(directory, f) for f in os.listdir(directory)
             if f.startswith(stem + "-") and f.endswith(".db")),
            key=os.path.getmtime,
        )
    except OSError:
        return
    for old in files[:-_MAX_LOCAL_BACKUPS]:
        try:
            os.remove(old)
        except OSError:
            pass


def backup_database(db_path):
    """Copy the DB to a local, non-synced folder. Best-effort: never raises."""
    try:
        if not os.path.isfile(db_path) or os.path.getsize(db_path) == 0:
            return None
        directory = _backup_dir()
        stem = os.path.splitext(os.path.basename(db_path))[0]
        stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        dest = os.path.join(directory, f"{stem}-{stamp}.db")
        shutil.copy2(db_path, dest)
        _prune_backups(directory, stem)
        print(f"  [db_guard] startup backup -> {dest}")
        return dest
    except Exception as e:
        print(f"  [db_guard] WARNING: startup backup failed: {e}")
        return None


# --- 5. lock file -----------------------------------------------------------

class DBLock:
    """Advisory hostname/pid/heartbeat lock stored as '<db>.lock' next to the DB."""

    def __init__(self, db_path):
        self.db_path = db_path
        self.lock_path = db_path + ".lock"
        self.hostname = socket.gethostname()
        self.pid = os.getpid()
        self._started_at = None
        self._stop = threading.Event()
        self._thread = None
        self._held = False

    # -- io helpers --
    def _payload(self):
        now = _now().isoformat()
        return {
            "hostname": self.hostname,
            "pid": self.pid,
            "started_at": self._started_at or now,
            "heartbeat_at": now,
        }

    def _write(self):
        tmp = f"{self.lock_path}.tmp{self.pid}"
        with open(tmp, "w") as f:
            json.dump(self._payload(), f, indent=2)
        os.replace(tmp, self.lock_path)

    def _read(self):
        with open(self.lock_path) as f:
            return json.load(f)

    def _is_ours(self, data):
        return data.get("hostname") == self.hostname and data.get("pid") == self.pid

    # -- acquire / resolve --
    def acquire(self, interactive=True):
        """Returns True if the lock is held (or safely ignorable), False to abort."""
        if os.path.exists(self.lock_path):
            try:
                existing = self._read()
            except Exception:
                existing = None
            if not self._resolve_existing(existing, interactive):
                return False

        self._started_at = _now().isoformat()
        try:
            self._write()
        except Exception as e:
            print(f"  [db_guard] WARNING: could not create lock file ({e}); "
                  f"continuing without a lock.")
            return True

        self._held = True
        self._thread = threading.Thread(
            target=self._heartbeat, name="db_guard.heartbeat", daemon=True
        )
        self._thread.start()
        atexit.register(self.release)
        return True

    def _resolve_existing(self, existing, interactive):
        if not existing:
            print("  [db_guard] found an unreadable lock file -- assuming stale, "
                  "taking over.")
            return True

        host = existing.get("hostname", "?")
        pid = existing.get("pid", "?")
        hb = _parse_iso(existing.get("heartbeat_at"))
        age = (_now() - hb).total_seconds() if hb else None

        # same machine ------------------------------------------------------
        if host == self.hostname:
            if isinstance(pid, int) and pid != self.pid and _pid_running(pid):
                self._banner(
                    "ANOTHER FINANCIAL-ANALYZER LOOKS LIKE IT'S RUNNING ON THIS MACHINE",
                    host, pid, age,
                    "Close the other window first. Two instances writing the same\n"
                    "  DB at once can still corrupt it.")
                return self._maybe_override(interactive)
            print(f"  [db_guard] clearing a stale lock from a previous run on this "
                  f"machine (pid {pid}).")
            return True

        # other machine ---------------------------------------------------------
        if age is not None and age < _STALE_LOCK_SECONDS:
            self._banner(
                "THE APP LOOKS OPEN ON YOUR OTHER MACHINE RIGHT NOW",
                host, pid, age,
                f"If Financial-Analyzer is still open on '{host}':\n"
                f"    -> quit it there, wait for OneDrive to sync (green check),\n"
                f"       then start here.\n"
                f"  Running it on both machines at once makes OneDrive silently\n"
                f"  drop one machine's changes into a conflict-copy file.")
            return self._maybe_override(interactive)

        hb_txt = f"{age / 60:.0f} min ago" if age is not None else "unknown"
        print(f"  [db_guard] found a lock from '{host}' but its last heartbeat was "
              f"{hb_txt};\n             assuming it was left behind and taking over.")
        return True

    def _banner(self, headline, host, pid, age, body):
        line = "!" * 74
        age_txt = f"{age:.0f}s ago" if age is not None else "unknown"
        print("\n" + line)
        print(f"!!!  {headline}")
        print(line)
        print(f"  lock holder     : {host}  (pid {pid})")
        print(f"  last heartbeat  : {age_txt}")
        print(f"  this machine    : {self.hostname}  (pid {self.pid})")
        print("")
        for ln in body.splitlines():
            print("  " + ln)
        print(line)

    def _maybe_override(self, interactive):
        if not interactive:
            print("  [db_guard] non-interactive start -- refusing to continue. "
                  "Disable with the\n"
                  "             'db_guard_on_startup' app setting if you're sure.")
            return False
        try:
            ans = input("  Type 'yes' to start anyway (ONLY if the other machine is "
                        "closed): ").strip().lower()
        except EOFError:
            return False
        return ans == "yes"

    # -- heartbeat / release --
    def _heartbeat(self):
        while not self._stop.wait(_HEARTBEAT_INTERVAL):
            try:
                current = self._read()
            except Exception:
                current = None
            if current is not None and not self._is_ours(current):
                return  # someone else took the lock; stop touching it
            try:
                self._write()
            except Exception:
                return

    def release(self):
        if not self._held:
            return
        self._held = False
        self._stop.set()
        try:
            if os.path.exists(self.lock_path) and self._is_ours(self._read()):
                os.remove(self.lock_path)
        except Exception:
            pass


def _warn_if_foreign_lock(db_path):
    """Read-only callers (dashboard): surface, but don't block on, a live lock
    from the other machine."""
    lock_path = db_path + ".lock"
    if not os.path.exists(lock_path):
        return
    try:
        with open(lock_path) as f:
            data = json.load(f)
    except Exception:
        return
    host = data.get("hostname", "?")
    if host == socket.gethostname():
        return
    hb = _parse_iso(data.get("heartbeat_at"))
    age = (_now() - hb).total_seconds() if hb else None
    if age is not None and age < _STALE_LOCK_SECONDS:
        print(f"  [db_guard] NOTE: the CLI looks open on '{host}' right now. This "
              f"dashboard is\n"
              f"             read-only so it's safe, but the numbers may lag until "
              f"OneDrive syncs.")


# --- entry point ----------------------------------------------------------------

def guard_database_startup(db_path, *, role="cli", interactive=True,
                           sync_timeout=_SYNC_DEFAULT_TIMEOUT):
    """
    Run the startup safety checks in order. For role="cli" (a writer) also acquire
    a heartbeat lock and take a local backup.

    Returns a held DBLock (role="cli") or None. Raises DBGuardAbort if the app
    must not start.
    """
    try:
        from db import app_settings
        if not app_settings.get_setting("db_guard_on_startup"):
            return None
    except Exception:
        pass  # settings unavailable -> guard on anyway

    db_path = os.path.abspath(db_path)

    # 1. conflict copies -> loud hard stop
    hits = scan_for_conflict_copies(db_path)
    if hits:
        _print_conflict_banner(db_path, hits)
        raise DBGuardAbort(
            f"{len(hits)} OneDrive conflict-copy file(s) next to the database"
        )

    # 2. sync settle (bounded, advisory)
    wait_for_sync_settled(db_path, timeout=sync_timeout)

    # 3. integrity -> hard stop
    check_integrity(db_path)

    # fingerprint -> printed so two machines can be eyeball-compared
    print_database_fingerprint(db_path)

    # 4/5. writer-only: local backup + exclusive-ish lock
    if role == "cli":
        backup_database(db_path)
        lock = DBLock(db_path)
        if not lock.acquire(interactive=interactive):
            raise DBGuardAbort("another instance holds the database lock")
        return lock

    _warn_if_foreign_lock(db_path)
    return None
