

# import needed modules

# import user defined modules
from cli import cli_helper


class SubMenu():
    def __init__(self, title, basefilepath, action_strings, action_funcs):
        self.title = title
        self.basefilepath = basefilepath
        self.action_strings = action_strings
        self.action_funcs = action_funcs


    ##############################################################################
    ####      "FLOW" FUNCTIONS           #########################################
    ##############################################################################

# TODO: I think that when I typed in "Wells Credit" as a run response it got past my initial exception check
    def run(self):
        print("\n\n")
        print("##############################")
        print("##### " + self.title + " #####")
        print("###############################")

        status = True
        while status:
            self.print_menu_options()

            # handle user input
            usr_inp = self.parse_input()

            # if user wants to quit
            if usr_inp == "q":
                status = False
                break
            else:
                try:
                    usr_inp = int(usr_inp)
                except ValueError:
                    print("Uh oh, was that a number?")

            # handle user action
            if usr_inp > len(self.action_funcs):
                print("ERROR: wrong number command (too high)")

            self.run_sub_action(usr_inp)


    def run_sub_action(self, num):
        ind = num - 1 # take away 1 since menu starts at 1 but array starts at 0
        print("\n\nRunning: " + self.action_strings[ind])
        self.action_funcs[ind]()


    ##############################################################################
    ####      MENU PRINTING FUNCTIONS    #########################################
    ##############################################################################

    def print_menu_options(self):
        print("\n\n##### " + self.title + " #####")
        i = 1
        for action in self.action_strings:
            print(str(i) + ": " + action)
            i = i + 1

        # print quit option
        print("EXIT: press 'q' to QUIT")



    ##############################################################################
    ####      INTERACTION FUNCTIONS    ###########################################
    ##############################################################################


    def parse_input(self):
        usr_inp = input("Please enter your selection: ")
        return usr_inp