"""
keyword_miner: mines new category-keyword suggestions from already-categorized
transactions.

The idea: if a merchant string ("CUBS FOODS", "RAISING CANES") shows up many
times and is (almost) always filed under the same category, but is NOT yet
covered by any keyword in the keywords table, it's a great keyword candidate.
Accepting these suggestions moves work from ML/manual categorization into the
deterministic keyword pass.

Candidates are literal UPPERCASE substrings of raw descriptions (single tokens
and adjacent token pairs), because that's exactly how
Transaction.categorizeTransactionAutomatic matches keywords. Compound (&&)
keywords are not mined -- single substrings generalize better.
"""

# import needed modules
from collections import defaultdict

# import user defined modules
import db.helpers as dbh


# tokens that are common in bank descriptions but useless as keywords
STOPWORDS = {
    "PAYMENT", "PURCHASE", "AUTHORIZED", "ONLINE", "CARD", "DEBIT", "CREDIT",
    "RECURRING", "CHECK", "TRANSFER", "TRANSACTION", "WITHDRAWAL", "DEPOSIT",
    "WWW", "COM", "INC", "LLC", "MINNEAPOLIS", "SAINT", "PAUL", "SHOREVIEW",
}


def _valid_token(token):
    """Keyword-worthy token: 4+ chars, letters only (digits are store #s / refs)."""
    return len(token) >= 4 and token.isalpha() and token not in STOPWORDS


def mine_keyword_suggestions(transactions, min_count=5, min_purity=0.9,
                             min_new=3, max_suggestions=25):
    """Return keyword suggestions mined from categorized transactions.

    transactions: list of Transaction objects (typically the full ledger).
    min_count:    candidate must match at least this many categorized transactions
    min_purity:   fraction of matches that must share one category
    min_new:      candidate must cover at least this many transactions that no
                  existing keyword already matches
    Returns a list of dicts sorted by new coverage:
      {keyword, category_id, matches, purity, new_matches}
    """
    existing_keywords = [row[2].upper() for row in dbh.keywords.get_keyword_ledger_data()]

    # candidate -> {category_id: count}, candidate -> set of txn indices,
    # candidate -> set of txn indices not already keyword-covered
    cand_cats = defaultdict(lambda: defaultdict(int))
    cand_txns = defaultdict(set)
    cand_new = defaultdict(set)

    for i, t in enumerate(transactions):
        if t.category_id is None or t.category_id == 0 or not t.description:
            continue
        desc_u = t.description.upper()
        already_covered = any(kw in desc_u for kw in existing_keywords)

        tokens = desc_u.split()
        candidates = {tok for tok in tokens if _valid_token(tok)}
        # adjacent pairs -- only if the joined form is a literal substring of the
        # raw description (so keyword matching will actually hit it later)
        for a, b in zip(tokens, tokens[1:]):
            if _valid_token(a) and _valid_token(b) and f"{a} {b}" in desc_u:
                candidates.add(f"{a} {b}")

        for cand in candidates:
            cand_cats[cand][t.category_id] += 1
            cand_txns[cand].add(i)
            if not already_covered:
                cand_new[cand].add(i)

    # filter candidates on count / purity / new coverage
    scored = []
    for cand, cats in cand_cats.items():
        total = sum(cats.values())
        if total < min_count:
            continue
        top_cat, top_count = max(cats.items(), key=lambda kv: kv[1])
        purity = top_count / total
        if purity < min_purity:
            continue
        if len(cand_new[cand]) < min_new:
            continue
        scored.append({
            "keyword": cand,
            "category_id": top_cat,
            "matches": total,
            "purity": purity,
            "new_matches": len(cand_new[cand]),
        })

    # greedy dedupe: many candidates cover the same merchant ("CUBS", "CUBS FOODS",
    # "FOODS QUARRY"). Prefer higher new coverage, then shorter/more general
    # keywords; skip candidates whose new transactions are already covered by an
    # accepted suggestion.
    scored.sort(key=lambda s: (-s["new_matches"], len(s["keyword"])))
    accepted = []
    covered = set()
    for s in scored:
        fresh = cand_new[s["keyword"]] - covered
        if len(fresh) < min_new:
            continue
        covered |= cand_new[s["keyword"]]
        accepted.append(s)
        if len(accepted) >= max_suggestions:
            break

    return accepted
