

# import user CLI stuff
from cli.cli_class import SubMenu
from cli.cli_class import Action

# import user defined modules
import db.helpers as dbh
from categories import categories_helper as cath


class tabBudgeting(SubMenu):
    def __init__(self, title, basefilepath):
        # initialize information about sub menu options
        action_arr = [Action("Print budget", self.a01_print_uncategorized),
                                 Action("Categorize uncategorized", self.a02_categorize_NA)]


        # call parent class __init__ method
        super().__init__(title, basefilepath, action_arr)

