





def sum_transaction_total(transactions):
    sum = 0
    for transaction in transactions:
        sum += transaction.amount
    return sum