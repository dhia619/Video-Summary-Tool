from gui import *
from settings import *
from analyzer import Analyzer


class Application:
    def __init__(self,video_path,model_path):
        self.gui = APPGUI()
        self.classes = classes
        self.analyzer = Analyzer(video_path,model_path,self.classes)
        self.gui.start_button.configure(command = lambda : self.analyzer.start(self.gui))
        self.gui.mainloop()

if __name__ == "__main__":
    app = Application("../computer vision/assets/cars - Trim.mp4","../computer vision/models/yolov8n.pt")