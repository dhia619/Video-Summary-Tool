from gui import *
from settings import *
from analyzer import Analyzer


class Application:
    def __init__(self):
        self.gui = APPGUI()
        self.analyzer = Analyzer(classes)
        self.gui.start_button.configure(command = lambda : self.analyzer.start(self.gui))
        self.gui.mainloop()

if __name__ == "__main__":
    app = Application()