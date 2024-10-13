from gui import *
from settings import *
from analyzer import Analyzer


class Application:
    def __init__(self,video_path,model_path):
        self.gui = APPGUI()
        self.analyzer = Analyzer(video_path,model_path,classes)
        self.gui.start_button.configure(command = lambda : self.analyzer.start(self.gui))
        self.gui.mainloop()

if __name__ == "__main__":
    app = Application("videos/cars.mp4","../computer vision/models/yolov8n.pt")