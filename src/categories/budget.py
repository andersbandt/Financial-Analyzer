# import needed modules
from db import db_helper
import categories


class BudgetCategory(categories.Category):
    def __init__(self, category_id):
        super(categories.Category, self).__init__()
        #self.category_id = category_id


        self.cd = db_helper.get_bcat_cd()


