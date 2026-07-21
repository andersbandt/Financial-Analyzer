"""
Class: VenmoCredit

Parser for Venmo Credit Card (Synchrony Bank) monthly PDF statements.

Statement layout notes:
- PDF text extraction runs transaction rows together on long lines, so rows are
  pulled out with a regex rather than line-by-line parsing.
- Each transaction row looks like:
      MM/DD <reference#> <description> $123.45
  where <reference#> is a long uppercase alphanumeric token (e.g. 2442733GPM83X54GA).
  Payments and refunds have a negative amount: -$8.22
- Transaction dates have no year. The year is inferred from the billing cycle
  line ("30 day billing cycle from 05/12/2026 to 06/10/2026"), which handles
  statements that span a December -> January year boundary.
- Sign convention: the PDF shows purchases as positive and payments as negative.
  Amounts are inverted on load so purchases are stored as negative (spending)
  and payments/refunds as positive, matching the rest of the ledger.
"""

import re

from PyPDF2 import PdfReader

import statement_types.Statement as Statement
import statement_types.Transaction as Transaction

# MM/DD + reference # + description + amount
TRANSACTION_RE = re.compile(
    r"(\d{2})/(\d{2}) ([A-Z0-9]{12,20}) (.+?) (-?)\$([\d,]+\.\d{2})"
)

# "30 day billing cycle from 05/12/2026 to 06/10/2026"
CYCLE_RE = re.compile(
    r"billing cycle from (\d{2})/\d{2}/(\d{4}) to (\d{2})/\d{2}/(\d{4})"
)


class VenmoCredit(Statement.Statement):
    def load_statement_data(self):
        try:
            reader = PdfReader(self.filepath)
        except FileNotFoundError:
            print("Uh oh, error in data loading")
            print("Missing data! You might be missing your Venmo credit .pdf file")
            return False

        full_text = "\n".join(page.extract_text() or "" for page in reader.pages)

        # determine billing cycle for year inference
        cycle = CYCLE_RE.search(full_text)
        if cycle:
            start_month, start_year = int(cycle.group(1)), int(cycle.group(2))
            end_year = int(cycle.group(4))
        else:
            print("WARNING: couldn't find billing cycle in Venmo credit statement. "
                  "Falling back to statement year for all transactions.")
            start_month, start_year, end_year = None, int(self.year), int(self.year)

        transactions = []
        for match in TRANSACTION_RE.finditer(full_text):
            month, day, _reference, description, neg_sign, amount_str = match.groups()

            # infer year from billing cycle (handles Dec -> Jan statements)
            year = start_year if int(month) == start_month else end_year
            date = f"{year}-{month}-{day}"

            # invert sign: purchases (positive in PDF) -> negative spending
            amount = float(amount_str.replace(",", ""))
            if neg_sign != "-":
                amount = -amount

            transactions.append(
                Transaction.Transaction(
                    date,
                    self.account_id,
                    None,  # category (assigned later by categorization)
                    amount,
                    description,
                )
            )

        if len(transactions) == 0:
            print("WARNING: no transactions found in Venmo credit statement: " + self.filepath)

        # set and return transactions
        self.transactions = transactions
        return transactions
