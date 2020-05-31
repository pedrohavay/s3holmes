import npyscreen, curses

class FileExplorerWidget(npyscreen.BoxTitle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.footer = "[^H] Help [^Q] Quit"

    def when_value_edited(self):
        if not self.get_value() == None:
            # Reload Objects
            self.parent.load_objects(self.get_values()[self.value])

            # Reset
            self.value = None
            
            # Beep
            curses.beep()

class AskAWSKeysWidget(npyscreen.TitleSelectOne):
    def __init__(self, *args, **kwargs):
        # Init parent class
        super().__init__(*args, **kwargs)

        # Init old value
        self.__old_value = bool(self.get_value()[0])

    def when_value_edited(self):
        # Current value
        current_value = bool(self.get_value()[0])

        # Check if has changes
        if self.__old_value != current_value:
            # Check option
            if current_value:
                # Render the text fields
                self.parent.aws_configure(True)
            else:
                # Destroy the text fields
                self.parent.aws_configure(False)