


class Action:
    def __init__(self, title, action):
        self.title = title
        self.action = action

    def run(self):
        self.action()


class SubMenu:
    def __init__(self, title, basefilepath, action_arr):
        self.title = title
        self.basefilepath = basefilepath
        self.action_arr = action_arr

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
            if usr_inp > len(self.action_arr):
                print("ERROR: wrong number command (too high)")
                return

            self.run_sub_action(usr_inp)

    def run_sub_action(self, num):
        ind = num - 1  # take away 1 since menu starts at 1 but array starts at 0
        print("\n\nRUNNING: " + self.action_arr[ind].title)
        try:
            status = self.action_arr[ind].action()
        except KeyboardInterrupt:
            status = False
        print(f"\nCompleted executing ACTION:'{self.action_arr[ind].title}' with exit code: {status}\n")
        return status

    def print_menu_options(self):
        print("\n\n##### " + self.title + " #####")
        i = 1
        for action in self.action_arr:
            print(str(i) + ": " + action.title)
            i = i + 1

        # print quit option
        print("EXIT: press 'q' to QUIT")

    # TODO: evaluate usage of this and delete (overlap with CLI helper)
    def parse_input(self):
        usr_inp = input("Please enter your selection: ")
        return usr_inp
