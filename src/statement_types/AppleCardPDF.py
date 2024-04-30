from PyPDF2 import PdfReader
import re
from dateutil import parser
import datetime
from statement_types import ExtractedDocument, Transaction, Payment


class AppleCard:
    """
    param: source: str = path to the PDF file

    This class is used to extract data from the Apple Card PDF statements.
    To use, instantiate the class with the path to the PDF file and then the
    process_document() method.
    Exmample:
    obj = AppleCard(filepath_to_pdf)
    doc = obj.process_document()
    This will return an ExtractedDocument object.

    Alternatively, you can run
    doc = AppleCard(filepath_to_pdf).process_document()

    """

    def __init__(self, source):
        self.source = source

    def convert_pages_to_dict(self):
        reader = PdfReader(self.source)
        relevant_page_nums: int = range(reader.getNumPages())[1:-1]  # break off first and last page
        self.page_text = {}

        for index in relevant_page_nums:
            """
            For every page, extract the text and split it by newline.
            It so happens that every separate column has a newline. This means
            we have a list of each block of text. This is oppposed to each list
            item being a single word.
            page_text = {page_number: ['block_of_text1', 'block_of_text2', ...]}
            """

            page = reader.getPage(index)
            self.page_text[index] = page.extractText().split('\n')

    def extract_payments(self) -> list[list[datetime.datetime | str]]:
        payments = []
        for page in self.page_text.values():
            for word in page:
                if re.match(re.compile(r"^-[$]{0,1}[0-9]+(\.[0-9]{2})?\s$"), word):
                    """
                    From left to right, the regex is looking for a '-', '$', some series of digits,
                    a decimal with digits after, and a trailing space. The amounts in this document
                    always have a trailing space. Once we find a negative money value, we know
                    that this is the end of a payment row.
                    """
                    idx = page.index(word)
                    payments.append(page[idx - 2: idx + 1])
        payments.pop(-1)  # remove the last item because it's the total amount of payments
        return payments

    def extract_transactions(self) -> list[list[datetime.datetime | str | float]]:
        transactions = []
        page_copy = self.page_text.copy()
        for page in page_copy.values():  # we will be removing items from the dict, so we need a copy
            try:
                """Cut off everything before "Transactions"."""
                page = page[page.index("Transactions"):]
            except ValueError:
                pass

            for word in page:
                if re.match(re.compile(r'^\d{2}/\d{2}/\d{4}$'), word):
                    """
                    Search for a date. This is the start of a row.
                    Once we have the date, the last item in each transaction row is 
                    five indicies after that. In order, that is:
                    Date, Description, Cashback Percentage, Cashback Amount, and Amount.
                    Cashback Percentage is different rewards percentages.
                    The values between Date (idx) and Amount (idx+5) are combined into a list which
                    is then appended to the transactions list.
                    """
                    idx = page.index(word)

                    entry = page[idx:idx + 5]

                    date = parser.parse(entry[0])  # convert date in string form to datetime obj
                    description = entry[1]
                    cashback_percentage = float(entry[2][:-1])  # remove the % from the cashback percentage
                    cashback_amount = float(entry[3][1:].rstrip())  # remove the $ and trailing space
                    amount = float(entry[4][1:].rstrip())  # remove the $ and trailing space

                    transactions.append([date, description, cashback_percentage, cashback_amount, amount])
                    page.remove(
                        word)  # remove the date from the list so we don't find it again on the next .index() lookup
        return transactions

    def extract_misc_data(self) -> dict[str, str | datetime.datetime | float]:
        """
        Grab the second to last page of the pdf. This is where interest charges are listed.
        The list indicies are hardcoded. We use negative indicies because going from the top-down
        there could be more data in the rows of interest charges.
        However, this requires testing with statements which have lines under "Interest Charged".
        """
        page = list(self.page_text.values())[-1]  # this page has all the basic info and info about interest charges

        name_and_email = page[-6]
        name = name_and_email.split(', ')[0]
        email = name_and_email.split(', ')[1]

        date_end_string = page[-2]
        date_start_string = f"{page[-4]}{date_end_string[-4:]}"  # page[-4] has the MMM DD format, so we need to add the YYYY, which is already in date_end
        date_start = parser.parse(date_start_string)  # convert strings into datetime objects
        date_end = parser.parse(date_end_string)

        interest_ytd = page[-21].rstrip()  # remove the trailing space
        interest_ytd = float(interest_ytd[1:])  # remove the $ sign

        apr = page[-18].rstrip(" %")
        apr = float(apr)

        cashback = page[-10].rstrip()
        cashback = float(cashback[1:])  # remove the $ sign

        misc_data = {
            'name': name,
            'email': email,
            'date_start': date_start,
            'date_end': date_end,
            'interest_ytd': interest_ytd,
            'apr': apr,
            'cashback': cashback,

        }
        return misc_data

    def process_document(self) -> ExtractedDocument:

        self.convert_pages_to_dict()
        payments = self.extract_payments()
        transactions = self.extract_transactions()
        misc = self.extract_misc_data()

        payment_objs = []
        for payment in payments:
            payment_objs.append(
                Payment(
                    date=payment[0],
                    description=payment[1],
                    amount=payment[2]
                )
            )

        transaction_objs = []
        for transaction in transactions:
            transaction_objs.append(
                Transaction(
                    date=transaction[0],
                    description=transaction[1],
                    cashback=transaction[3],
                    amount=transaction[4],
                )
            )

        return ExtractedDocument(
            payments=payment_objs,
            transactions=transaction_objs,
            name=misc['name'],
            email=misc['email'],
            date_start=misc['date_start'],
            date_end=misc['date_end'],
            interest_ytd=misc['interest_ytd'],
            apr=misc['apr'],
            cashback=misc['cashback']
        )


if __name__ == '__main__':
    file = AppleCard('/finance/apple.pdf')
    print(file.process_document())