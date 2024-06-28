"""

"""



class Action:
    def __init__(self, title, action):
        # set ledger variables
        self.title = title
        self.action = action

    def run(self):
        self.action()

    def get_title(self):
        return self.title


class SubMenu():
    def __init__(self, title, basefilepath, action_arr):
        self.title = title
        self.basefilepath = basefilepath

        self.actions = action_arr


    ##############################################################################
    ####      "FLOW" FUNCTIONS           #########################################
    ##############################################################################

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
                    print("\n\nUh oh, was that a number ?!?")
                    continue

            # handle user action
            if usr_inp > len(self.actions):
                print("ERROR: wrong number command (too high)")
                return

            self.run_sub_action(usr_inp)


    def run_sub_action(self, num):
        ind = num - 1 # take away 1 since menu starts at 1 but array starts at 0
        action_title = self.actions[ind].get_title()
        print(f"\n\nRUNNING: {action_title}")
        status = self.actions[ind].run()
        print(f"\nCompleted executing {action_title} with exit code: {status}\n")
        return status


    ##############################################################################
    ####      MENU PRINTING FUNCTIONS    #########################################
    ##############################################################################

    def print_menu_options(self):
        print("\n\n##### " + self.title + " #####")
        i = 1
        for action in self.actions:
            print(str(i) + ": " + action.get_title())
            i = i + 1

        # print quit option
        print("EXIT: press 'q' to QUIT")


    ##############################################################################
    ####      INTERACTION FUNCTIONS    ###########################################
    ##############################################################################

    def parse_input(self):
        usr_inp = input("Please enter your selection: ")
        return usr_inp




