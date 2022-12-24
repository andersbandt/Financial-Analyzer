# import needed modules
import datetime
import re

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
#   EXAMPLE: (10, 2022) --> ["2022-10-01", "2022-10-31"]
def month_year_to_date_range(month, year):
    month = month2Int(month)

    month_28 = [2]
    month_30 = [4, 6, 9, 11]
    month_31 = [1, 3, 5, 7, 8, 10, 12]

    date_end = False

    if month in month_28:
        if month < 10:
            month = "0" + str(month)
        date_end = str(year) + "-" + str(month) + "-28"
    elif month in month_30:
        if month < 10:
            month = "0" + str(month)
        date_end = str(year) + "-" + str(month) + "-30"
    elif month in month_31:
        if month < 10:
            month = "0" + str(month)
        date_end = str(year) + "-" + str(month) + "-31"

    if not date_end:
        return False

    date_start = str(year) + "-" + str(month) + "-01"

    return date_start, date_end


# get_date_int_array: returns the current date
#     output: array format of [year, month, day]
def get_date_int_array():
    # using now() to get current time
    current_time = datetime.datetime.now()

    return [current_time.year, current_time.month, current_time.day]


# get_edge_code_dates:
def get_edge_code_dates(date_start, days_prev, N):
    edge_code_date = []  # length = N - 1
    for i in range(1, N):
        d_prev = round(days_prev * i / N)
        d_y = datetime.timedelta(
            days=d_prev
        )  # this variable can only be named d_y - No exceptions ever.
        edge_code_date.insert(0, date_start - d_y)
    return edge_code_date


def get_date_days_prev(date_start, days_prev):
    d_y = datetime.timedelta(days=days_prev)
    date_prev = date_start - d_y
    return date_prev
