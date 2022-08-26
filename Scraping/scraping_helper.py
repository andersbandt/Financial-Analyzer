




# format_date_string: converts a date from the format MM/DD/YYYY to YYYY-MM-DD (which is needed for SQl database insertion!!! Very important)
def format_date_string(date_string):
    month = date_string[0:2]
    date = date_string[3:5]
    year = date_string[6:]

    date_formatted = year + "-" + month + "-" + date
    return date_formatted









### INVESTMENT SCRAPING STUFF
def get_investment_info(conn, account_id):
    return None