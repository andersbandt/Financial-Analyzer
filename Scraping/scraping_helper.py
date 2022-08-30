

import re


# format_date_string: converts a date from a certain format to YYYY-MM-DD (which is needed for SQl database insertion!!! Very important)
# tested input date formats: (MM/DD/YYYY, MM/DD/YY)
def format_date_string(date_string):
    slash_indexes = [i.start() for i in re.finditer("/", date_string)]

    if len(slash_indexes) is not 2:
        raise Exception("Uh oh, may have encountered an improperly formatted date for conversion")
        return None
    else:
        month = date_string[0:slash_indexes[0]]
        date = date_string[slash_indexes[0]+1:slash_indexes[1]]
        year = date_string[slash_indexes[1]+1:]

        # test for improperly sized dates (add leading 0's, change date to 4 numbers)
        if len(month) == 1:
            month = "0" + month
        if len(date) == 1:
            date = "0" + date
        if len(year) == 2:
            year = "20" + year

        date_formatted = year + "-" + month + "-" + date
        return date_formatted



### INVESTMENT SCRAPING STUFF
def get_investment_info(conn, account_id):
    return None