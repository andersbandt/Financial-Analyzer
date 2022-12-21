
# import needed modules
from categories import Category
from db import db_helper


class BudgetCategory(Category.Category):
    def __init__(self, category_id):
        super(Category.Category, self).__init__()
        #self.category_id = category_id


        self.cd = db_helper.get_bcat_cd()


