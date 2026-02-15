# Plaid Integration Setup Guide

## 🚨 BEFORE YOU START - BACKUP YOUR DATABASE!

**CRITICAL: Backup your database before running the migration!**

```bash
# Navigate to your database location
cd C:/Users/ander/Documents/GitHub/Financial-Analyzer/src/db/

# Create a backup with timestamp
copy financials.db financials.db.backup-2026-02-10

# Or if you're in Linux/WSL:
cp financials.db financials.db.backup-$(date +%Y-%m-%d)
```

**Verify the backup exists and has a size > 0 before proceeding!**

---

## Step 1: Install Dependencies

The new dependencies are already added to `requirements.txt`:
- `plaid-python>=16.0.0` - Plaid API client
- `cryptography>=41.0.0` - For encrypting access tokens

```bash
# Activate your virtual environment first
source env/bin/activate  # Linux/Mac
# OR
env\Scripts\activate     # Windows

# Install new dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep plaid
pip list | grep cryptography
```

**Expected output:**
```
plaid-python    16.x.x
cryptography    41.x.x
```

---

## Step 2: Run the Application (Triggers Migration)

The database migration runs automatically on startup.

```bash
python src/main.py
```

**What will happen:**
1. Existing database tables are verified (no changes to existing data)
2. `migrate_plaid_schema()` runs and adds new columns to `account` and `transactions` tables
3. Main menu appears with new Tab 10: "Plaid Integration"

**Look for these messages in the console:**
- No error messages about database migration
- Main menu shows tabs 1-10 (including "Plaid Integration")

**If something goes wrong:**
- Press `0` to exit
- Restore your backup: `copy financials.db.backup-2026-02-10 financials.db`
- Check the error message and troubleshoot (see bottom of this doc)

---

## Step 3: Verify Migration Was Successful

Before configuring Plaid, verify the migration worked:

### Option A: Check via SQLite command line
```bash
# Open database
sqlite3 src/db/financials.db

# Check account table schema (should show new plaid_* columns)
.schema account

# Check transactions table schema (should show plaid_* columns)
.schema transactions

# Exit
.quit
```

**Expected: You should see columns like:**
- `account` table: `plaid_account_id`, `plaid_institution_id`, `access_token_encrypted`, `is_plaid_linked`
- `transactions` table: `plaid_transaction_id`, `transaction_source`, `plaid_synced_at`

### Option B: Check via Python (safer if not familiar with SQLite)
```bash
python src/main.py
# Navigate to Tab 10: "Plaid Integration"
# Select "4. View linked accounts"
# Should show: "No linked accounts found." (this is normal, you haven't linked any yet)
# If this works without errors, migration succeeded!
```

---

## Step 4: Get Plaid API Credentials

You need a Plaid account to use this feature.

### Sign up for Plaid (Free for Development)
1. Go to: https://dashboard.plaid.com/signup
2. Create an account (use your email)
3. Verify your email
4. Complete the onboarding flow

### Get Your Credentials
1. Log into Plaid Dashboard: https://dashboard.plaid.com
2. Go to: **Team Settings → Keys**
3. You'll see:
   - **client_id** (looks like: `5f9b...`)
   - **sandbox** secret (looks like: `abc123...`)
   - **development** secret (different from sandbox)

### Which Environment to Use?

**Sandbox** (Recommended for testing):
- Uses fake data
- No real bank connections
- Good for testing the integration
- Uses special test credentials: https://plaid.com/docs/sandbox/test-credentials/

**Development** (Real data, limited):
- Connects to real banks
- Limited to 100 linked accounts
- Free tier
- Use once you're confident the integration works

**Production** (Requires approval):
- Requires Plaid to approve your application
- Not needed unless you're deploying this for real

---

## Step 5: Configure Plaid in the App

```bash
python src/main.py
```

**In the main menu:**
1. Enter `10` (Plaid Integration tab)
2. Select `1. Configure Plaid credentials`
3. Follow the prompts:
   - Enter your `client_id`
   - Enter your `secret` (use sandbox secret for testing)
   - Select environment: `1` for Sandbox (recommended for first test)

**What happens:**
- Credentials saved to: `~/.financial-analyzer/plaid_config.json`
- The app tests the connection
- You should see: ✅ Connection successful!

**If connection fails:**
- Double-check you copied the correct client_id and secret
- Verify you selected the correct environment (sandbox vs development)
- Make sure you're using the sandbox secret if you selected sandbox environment

---

## Step 6: Link a Test Account (Sandbox Mode)

**Important:** In sandbox mode, you don't connect to a real bank. You use test credentials.

```bash
# Still in Tab 10
Select: 2. Link bank account
```

**The Link Flow:**
1. App creates a Link token
2. You'll see a Link token printed (long string)
3. **For CLI testing, you need to manually complete Plaid Link**

### How to Complete Plaid Link (Sandbox)

**Option A: Use Plaid's Link Demo (Recommended for first test)**
1. Go to: https://plaid.com/docs/link/
2. Click "Try Link" button
3. Use test credentials:
   - Institution: "Chase"
   - Username: `user_good`
   - Password: `pass_good`
4. Complete the flow
5. You'll get a `public_token` - copy it
6. Paste into the CLI when prompted

**Option B: Skip Link for now**
- This integration works best with a web interface for Link
- For CLI testing, you might need to implement a workaround or use Plaid's API directly
- See "Known Limitations" section below

---

## Step 7: Sync Transactions

Once an account is linked:

```bash
# In Tab 10
Select: 3. Sync transactions
```

**Follow the prompts:**
1. Select the linked account
2. Choose date range (default: last 30 days)
3. App fetches transactions from Plaid
4. Transactions are displayed for review
5. **Automatic categorization runs** (uses existing keyword/ML system)
6. Manually categorize any remaining uncategorized transactions
7. Save to database

**What happens:**
- Plaid transactions are converted to your Transaction objects
- Duplicate checking prevents re-importing (via `plaid_transaction_id`)
- Transactions flow through same categorization pipeline as CSV files
- Saved to database with `transaction_source = 'PLAID'`

---

## Step 8: Verify Everything Works

### Check transactions were imported
```bash
# In main menu
Select: 5. Analyze Spending History
# Look for transactions from your Plaid sync

# OR check directly in database
sqlite3 src/db/financials.db
SELECT COUNT(*) FROM transactions WHERE transaction_source = 'PLAID';
.quit
```

### View linked accounts status
```bash
# In Tab 10
Select: 4. View linked accounts
```

Should show:
- Account name
- Last synced timestamp
- Transaction count
- Sync status

---

## Known Limitations & Workarounds

### 1. CLI Link Flow is Awkward
**Problem:** Plaid Link is designed for web/mobile, not CLI

**Workarounds:**
- Use Plaid's sandbox test mode with direct API calls
- Create a simple local web server to handle Link flow
- Use the `plaid_service.py` functions directly in Python console

### 2. Testing Without Link
If you want to test the integration without completing Link:

**Option: Manually insert test data**
```python
# In Python console
from plaid_integration import plaid_adapter
from datetime import date

# Create fake Plaid transaction
fake_plaid_trans = {
    'transaction_id': 'test_123',
    'account_id': 'plaid_account_456',
    'date': '2026-02-01',
    'amount': 50.00,
    'name': 'TEST MERCHANT'
}

# Convert to Transaction object
trans = plaid_adapter.plaid_transaction_to_transaction(
    fake_plaid_trans,
    account_id=2000000001  # Your account ID
)

# Save to database
import db.helpers as dbh
dbh.transactions.insert_transaction(trans)
```

### 3. First Time Sync Takes Time
- Plaid rate limits apply
- Large date ranges may timeout
- Start with small date ranges (7-30 days)

---

## Troubleshooting

### Error: "No Plaid credentials found"
**Fix:** Run Tab 10 → Configure Plaid credentials first

### Error: "Failed to initialize Plaid client"
**Causes:**
- Wrong client_id or secret
- Wrong environment selected
- Network issues

**Fix:**
- Verify credentials in Plaid Dashboard
- Delete `~/.financial-analyzer/plaid_config.json` and reconfigure
- Check your internet connection

### Error: "Failed to encrypt token"
**Cause:** Encryption key issue

**Fix:**
```bash
# Remove encryption key and let it regenerate
rm ~/.financial-analyzer/plaid_encryption.key
# Restart app, it will create a new key
```

### Error: Database migration fails
**Symptoms:** App crashes on startup with SQLite errors

**Fix:**
1. Restore backup: `copy financials.db.backup-2026-02-10 financials.db`
2. Check database isn't corrupted: `sqlite3 financials.db "PRAGMA integrity_check;"`
3. If corrupted, you'll need to restore from an older backup
4. Report the error message for debugging

### Migration ran but columns missing
**Check:**
```bash
sqlite3 src/db/financials.db ".schema account" | grep plaid
```

**If no results:** Migration didn't run. Check console output for errors.

### Duplicate transactions appearing
**Cause:** Plaid transaction IDs not being stored correctly

**Check:**
```sql
SELECT plaid_transaction_id, COUNT(*)
FROM transactions
WHERE plaid_transaction_id IS NOT NULL
GROUP BY plaid_transaction_id
HAVING COUNT(*) > 1;
```

**Fix:** Delete duplicates manually or re-sync with correct date range

---

## Files to Check If Things Go Wrong

### Config files (should be created automatically):
```
~/.financial-analyzer/plaid_config.json        # API credentials
~/.financial-analyzer/plaid_encryption.key     # Encryption key
```

### Database location:
```
C:/Users/ander/Documents/GitHub/Financial-Analyzer/src/db/financials.db
```

### Logs:
- Look at console output (loguru logs everything)
- Plaid-related logs have `[plaid_*]` module names

---

## Quick Reference Commands

```bash
# Backup database
cp src/db/financials.db src/db/financials.db.backup-$(date +%Y-%m-%d)

# Install dependencies
pip install -r requirements.txt

# Run app
python src/main.py

# Check database schema
sqlite3 src/db/financials.db ".schema account"

# Count Plaid transactions
sqlite3 src/db/financials.db "SELECT COUNT(*) FROM transactions WHERE transaction_source = 'PLAID';"

# View config file
cat ~/.financial-analyzer/plaid_config.json

# Remove config (to reconfigure)
rm ~/.financial-analyzer/plaid_config.json

# Remove encryption key (will regenerate)
rm ~/.financial-analyzer/plaid_encryption.key
```

---

## Success Checklist

- [ ] Database backed up
- [ ] Dependencies installed (`plaid-python`, `cryptography`)
- [ ] App starts without errors
- [ ] Tab 10 appears in main menu
- [ ] Migration completed (new columns exist in database)
- [ ] Plaid credentials configured
- [ ] Connection test passes
- [ ] (Optional) Test account linked
- [ ] (Optional) Transactions synced successfully
- [ ] (Optional) Transactions appear in database with `transaction_source = 'PLAID'`

---

## Need Help?

**Before asking for help, gather this info:**
1. Full error message from console
2. Output of: `pip list | grep plaid`
3. Output of: `sqlite3 src/db/financials.db ".schema account" | grep plaid`
4. Which step failed?
5. What environment are you using? (sandbox/development)

**Common issues and their fixes are in the Troubleshooting section above.**

---

## Next Development Steps (Future Work)

Once basic integration is working:

1. **Improve Link Flow for CLI**
   - Create simple Flask web server to handle Link redirects
   - Or use Plaid's Link token in a browser-based flow

2. **Automatic Sync**
   - Add scheduled sync (daily/weekly)
   - Use Plaid's webhook system for real-time updates

3. **Better Duplicate Detection**
   - Use Plaid's `pending_transaction_id` for pending transactions
   - Handle transaction updates (pending → posted)

4. **Balance Sync**
   - Auto-update account balances from Plaid
   - Track balance history

5. **Investment Support**
   - Plaid supports investment accounts
   - Sync holdings and transactions

---

## Summary

This integration adds Plaid API support while keeping the existing CSV system fully functional. Both systems share the same transaction processing pipeline, so categorization and analysis work identically.

**The key insight:** Plaid is just another data source. Once transactions are converted to your `Transaction` objects, everything downstream is identical.

Good luck! Take your time testing, and remember: **that backup is your safety net!** 🛡️
