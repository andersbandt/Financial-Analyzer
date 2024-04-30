from statement_types import Ledger
from statement_types import Statement
from statement_types import csvStatement

from statement_types import WellsChecking
from statement_types import WellsCredit
from statement_types import WellsSaving

from statement_types import AppleCard
from statement_types import ChaseCard

from statement_types import Marcus
from statement_types import Venmo

from statement_types import Robinhood
from statement_types import VanguardBrokerage
from statement_types import VanguardRoth

from dataclasses import dataclass
import datetime


# below code is from `nathan-hello` on Github from a branch I deleted. Preserving it here in case it becomes useful later

@dataclass
class Transaction:
    date: datetime.datetime
    description: str
    amount: int
    cashback: int


@dataclass
class Payment:
    date: datetime.datetime
    description: str
    amount: int


@dataclass
class ExtractedDocument:
    payments: list[Payment]
    transactions: list[Transaction]
    name: str
    email: str
    date_start: datetime.datetime
    date_end: datetime.datetime
    interest_ytd: int
    apr: int
    cashback: str

    def __repr__(self):
        return f"""ExtractedDocument(
    len(payments={len(self.payments)}),
    len(transactions={len(self.transactions)}),
    name="{self.name}",
    email="{self.email}",
    date_start=datetime.datetime({self.date_start}),
    date_end=datetime.datetime({self.date_end}),
    interest_ytd={self.interest_ytd},
    apr={self.apr},
    cashback={self.cashback})
    """


@dataclass
class Investment:
    account_number: str
    date: str
    description: str
    display_name: str
    value: int
    history: dict[str, str]
    note: str
    ticker: str


@dataclass
class Account:
    visibility: str
    display_name: str
    account_type: str
    balance: int
    algorithm: str
    balance_updated_date: str
    institution_name: str
    savings_goal: int
    rewards: int
    interest_rate: int
