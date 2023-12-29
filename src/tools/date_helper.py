


# import needed modules
from datetime import datetime, timedelta
import re

# import logger
from loguru import logger
from utils import logfn

##############################################################################
####      DATE VERIFICATION FUNCTIONS        #################################
##############################################################################

# return True if date1 is before date2, False otherwise
def date_order(date1, date2):
    if date1 < date2:
        return True
    else:
        return False


# check_sql_date_format: checks if a date is properly formatted in YYYY-MM-DD string format
def check_sql_date_format(date_string):
    char = "-"
    indices = [i.start() for i in re.finditer(char, date_string)]

    if indices[0] != 4 or indices[1] != 7:
        print("Date string locations of '-' don't match")
        raise Exception("ERROR: improperly formatted date string: ", date_string)
    return True


##############################################################################
####      DATE CONVERSION FUNCTIONS        ###################################
##############################################################################

# monthToInt: converts a month string to an integer
# TODO: I bet this function actually is not used anywhere since switching to a CLI
def month2Int(month):
    if month == "January":
        return 1
    elif month == "February":
        return 2
    elif month == "March":
        return 3
    elif month == "April":
        return 4
    elif month == "May":
        return 5
    elif month == "June":
        return 6
    elif month == "July":
        return 7
    elif month == "August":
        return 8
    elif month == "September":
        return 9
    elif month == "October":
        return 10
    elif month == "November":
        return 11
    elif month == "December":
        return 12
    else:
        return -1


# conv_two_digit_date: converts a two digit date representation with separators (MM/DD/YY) into
#   the format needed for SQL storage (YYYY-MM-DD)
def conv_two_digit_date(date):
    char = "/"
    ind = [i.start() for i in re.finditer(char, date)]

    if len(ind) != 2:
        print(
            "ERROR: may be passing in a poorly formatted date into: load_helper - conv_two_digit_date()"
        )
        raise Exception("Can't convert date into YYYY-MM-DD format")

    month = date[0 : ind[0]]
    if int(month) < 10:
        month = "0" + month

    day = date[ind[0] + 1 : ind[1]]
    if int(day) < 10:
        day = "0" + day

    year = (
        str(20) + date[ind[1] + 1 :]
    )  # prepend '20' to year (only will work for years 2000-2099)

    formatted_date = year + "-" + month + "-" + day

    if not check_sql_date_format(formatted_date):
        raise Exception("ERROR: something went wrong with formatting date")
        return False

    return formatted_date


# month_year_to_date_range: converts a string representation of a month and int of year
#   into the format needed for SQL storage (YYYY-MM-DD)
#   EXAMPLE: (2022, 10) --> ["2022-10-01", "2022-10-31"]
@logfn
def month_year_to_date_range(year, month):
    # Check if the month is valid
    if not (1 <= month <= 12):
        raise ValueError("Invalid month")

    # Calculate the last day of the month
    last_day_of_month = (datetime(year, month % 12 + 1, 1) - timedelta(days=1)).day

    # Format the start and end dates
    date_start = f"{year}-{month:02d}-01"
    date_end = f"{year}-{month:02d}-{last_day_of_month}"

    return date_start, date_end



##############################################################################
####      DATE GETTER FUNCTIONS            ###################################
##############################################################################

# TODO: for the below functions I should really audit other places I'm using date and make sure I'm using these functions!!!

def get_date_previous(d_prev):
    date_start = datetime.datetime.now()

    d_y = datetime.timedelta(
        days=d_prev
    )  # this variable can only be named d_y - No exceptions ever.

    prev_date = (date_start - d_y).strftime('%Y-%m-%d')
    return prev_date

# TODO: audit usage and possible combine with previous function
def get_date_days_prev(date_start, days_prev):
    d_y = datetime.timedelta(days=days_prev)
    date_prev = date_start - d_y
    return date_prev


# get_date_int_array: returns the current date
#     output: array format of [year, month, day]
def get_date_int_array():
    # using now() to get current time
    current_time = datetime.now()

    return [current_time.year, current_time.month, current_time.day]


# get_edge_code_dates:
# @param    date_start  datetime object
# @param    days_prev   integer the number of days since 'date_start'
# @param    N           number of bins to form
def get_edge_code_dates(date_start, days_prev, N):
    edge_code_date = []  # length = N + 1

    # NOTE: perhaps at some point audit this is performing my desired function
    for i in range(0, N+1):
        d_prev = round(days_prev * i / (N+1))
        d_y = datetime.timedelta(
            days=d_prev
        )  # this variable can only be named d_y - No exceptions ever.
        edge_code_date.append(
            (date_start - d_y).strftime('%Y-%m-%d')
        )

    edge_code_date.reverse()

    return edge_code_date



