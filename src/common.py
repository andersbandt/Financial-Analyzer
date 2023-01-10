import os
import re

FILEPATH = "/finance/src"

all_currency_symbols = re.compile(r'\p{Sc}')