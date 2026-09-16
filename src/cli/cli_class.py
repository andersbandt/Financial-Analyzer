
import questionary


def select_prompt(message, choices, **kwargs):
    """Wrapper around questionary.select that enables type-to-search filtering.

    Newer questionary versions support `use_search_filter` (type any substring to
    narrow the visible choices). Older ones raise TypeError on the unknown kwarg,
    so fall back to a plain select in that case.
    """
    try:
        return questionary.select(
            message,
            choices=choices,
            use_search_filter=True,
            use_jk_keys=False,  # required, otherwise j/k are swallowed as navigation
            **kwargs,
        ).ask()
    except TypeError:
        return questionary.select(message, choices=choices, **kwargs).ask()


class Action:
    def __init__(self, title, action):
        self.title = title
        self.action = action

    def run(self):
        self.action()


_QUIT = "[ Quit ]"


class SubMenu:
    def __init__(self, title, basefilepath, action_arr):
        self.title = title
        self.basefilepath = basefilepath
        self.action_arr = action_arr

    def run(self):
        while True:
            choices = [a.title for a in self.action_arr] + [_QUIT]
            selection = select_prompt(self.title, choices)

            if selection is None or selection == _QUIT:
                break

            ind = next(i for i, a in enumerate(self.action_arr) if a.title == selection)
            self.run_sub_action(ind + 1)

    def run_sub_action(self, num):
        ind = num - 1
        print("\n\nRUNNING: " + self.action_arr[ind].title)
        try:
            status = self.action_arr[ind].action()
        except KeyboardInterrupt:
            status = False
        print(f"\nCompleted executing ACTION:'{self.action_arr[ind].title}' with exit code: {status}\n")
        return status
