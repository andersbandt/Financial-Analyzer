# import needed modules
import categories
import db.helpers as dbh


class BudgetCategory(categories.Category):
    def __init__(self, category_id):
        super(categories.Category, self).__init__()
        # self.category_id = category_id

        self.cd = dbh.budget.get_bcat_cd()
