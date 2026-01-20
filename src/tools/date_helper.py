"""
@file date_helper.py
@brief toolsset for all things DATE related

"""


# import needed modules
from datetime import *
import re

# import logger
from loguru import logger


# iterate_dates: shit man ChatGPT wrote this guy. I use it in `balance_helper.py`
def iterate_dates(start_date_str, end_date_str):
    # Convert the input strings to datetime objects
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

    # Iterate over each date in the range
    current_date = start_date
    while current_date <= end_date:
        yield current_date.strftime("%Y-%m-%d")
        current_date += timedelta(days=1)


##############################################################################
####      DATE VERIFICATION FUNCTIONS        #################################
##############################################################################

# return True if date1 is before date2, False otherwise
def date_order(date1, date2):
    if date1 < date2:
        return True
    else:
        return False


# date_between: returns True if date is in range, false otherwise (INCLUSIVE OF RANGE)
def date_between(date_start, date_end, date_interest):
    if date_start <= date_interest:
        if date_end >= date_interest:
            return True
    return False


# check_sql_date_format: checks if a date is properly formatted in YYYY-MM-DD string format
def check_sql_date_format(date_string):
    char = "-"
    indices = [i.start() for i in re.finditer(char, date_string)]

    if indices[0] != 4 or indices[1] != 7:
        print("Date string locations of '-' don't match")
        raise Exception("ERROR: improperly formatted date string: ", date_string)
    return True


# TODO: this is currently dependent on how many monthly statement year folders I have on my local filesystem
def get_valid_years():
    current_year = datetime.now().year
    return list(range(2020, current_year + 1))  # tag:hardcode


##############################################################################
####      DATE CONVERSION FUNCTIONS        ###################################
##############################################################################

# conv_two_digit_date: converts a two digit date representation with separators (MM/DD/YY) into
#   the format needed for SQL storage (YYYY-MM-DD)
def conv_two_digit_date(date_str):
    char = "/"
    ind = [i.start() for i in re.finditer(char, date_str)]

    if len(ind) != 2:
        print(
            "ERROR: may be passing in a poorly formatted date into: load_helper - conv_two_digit_date()"
        )
        raise Exception("Can't convert date into YYYY-MM-DD format")

    month = date_str[0: ind[0]]
    if int(month) < 10:
        month = "0" + month

    day = date_str[ind[0] + 1: ind[1]]
    if int(day) < 10:
        day = "0" + day

    year = (
            str(20) + date_str[ind[1] + 1:]
    )  # prepend '20' to year (only will work for years 2000-2099)

    formatted_date = year + "-" + month + "-" + day

    if not check_sql_date_format(formatted_date):
        raise Exception("ERROR: something went wrong with formatting date")
        return False

    return formatted_date


# month_year_to_date_range: converts a string representation of a month and int of year
#   into the format needed for SQL storage (YYYY-MM-DD)
#   EXAMPLE: (2022, 10) --> ["2022-10-01", "2022-10-31"]
def month_year_to_date_range(year, month):
    # Check if the month is valid
    if not (1 <= month <= 12):
        raise ValueError(f"Invalid month: {month}")

    # Calculate the last day of the month
    last_day_of_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day

    # Format the start and end dates
    date_start = f"{year}-{month:02d}-01"
    date_end = f"{year}-{month:02d}-{last_day_of_month}"

    return date_start, date_end


##############################################################################
####      DATE GETTER FUNCTIONS            ###################################
##############################################################################

def get_cur_date():
    return datetime.now()
    # return datetime.now().date()

def get_cur_str_date():
    return datetime.now().strftime('%Y-%m-%d')


def get_date_previous(d_prev):
    date_start = datetime.now()

    d_y = timedelta(
        days=d_prev
    )  # this variable can only be named d_y - No exceptions ever.

    prev_date = (date_start - d_y).strftime('%Y-%m-%d')
    return prev_date



# get_date_days_prev: gets the date a previous relative to a different date
def get_date_days_prev(date_start, days_prev):
    d_y = timedelta(days=days_prev)
    date_prev = date_start - d_y
    return date_prev


# get_date_int_array: returns the current date
#     output: array format of [year, month, day]
def get_date_int_array():
    # using now() to get current time
    current_time = datetime.now()

    return [current_time.year, current_time.month, current_time.day]



def get_previous_month(year: int, month: int):
    """
    Returns (prev_year, prev_month) for a given year/month.
    """
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1



# get_edge_code_dates:
# @param    date_start  datetime object
# @param    days_prev   integer the number of days since 'date_start'
# @param    N           number of bins to form
def get_edge_code_dates(date_start, days_prev, N):
    edge_code_date = []  # length = N + 1

    # NOTE: perhaps at some point audit this is performing my desired function
    for i in range(0, N+ 1):
        d_prev = round(days_prev * i / (N + 1))
        d_y = timedelta(
            days=d_prev
        )  # this variable can only be named d_y - No exceptions ever.
        edge_code_date.append(
            (date_start - d_y).strftime('%Y-%m-%d')
        )

    edge_code_date.reverse()

    return edge_code_date
