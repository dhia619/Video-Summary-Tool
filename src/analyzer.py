import cv2
from ultralytics import YOLO
from sort import Sort
import numpy as np
from time import *
from math import floor
from threading import Thread, Event

class Entity:
    def __init__(self, cls, id_, t):
        self.id = id_
        self.class_ = cls
        self.first_appeared_time = t

class Analyzer:
    def __init__(self, video_path, path_to_model, classes):
        self.model = YOLO(path_to_model)
        self.video = cv2.VideoCapture(video_path)
        self.total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.frame_rate = self.video.get(cv2.CAP_PROP_FPS)
        self.all_classes = classes
        self.selected_classes = []
        self.entities = []
        self.registered_entities = []
        self.tracker = Sort(max_age=60, min_hits=40, iou_threshold=0.1)

        self.batch_size = 6
        self.batch_frames = []

        self.processing_time = 0
        self.stop_event = Event()  # To safely stop the thread

    def detect_entities(self, boxes, current_frame):
        detections = np.empty((0, 5))
        temp_classes = []
        timestamps = []
        for bbox in boxes:
            class_ = self.all_classes[int(bbox.cls[0])]
            confidence = round(bbox.conf[0].item(), 2)
            if class_ in self.selected_classes:
                x1, y1, x2, y2 = map(int, bbox.xyxy[0])
                detections = np.vstack((detections, np.array([x1, y1, x2, y2, confidence])))
                temp_classes.append(class_)
                timestamps.append(current_frame/self.frame_rate)

        tracking_results = self.tracker.update(dets=detections)
        for tracking_result, cls_, t in zip(tracking_results, temp_classes, timestamps):
            x1, y1, x2, y2, id_ = map(int, tracking_result)
            if id_ not in self.registered_entities:
                self.registered_entities.append(id_)
                self.entities.append(Entity(cls_, id_, t))

    def worker(self, gui):
        start_time = time()
        gui.progress_bar["value"] = 0

        while not self.stop_event.is_set():  # Continue until stop event is set
            success, frame = self.video.read()
            if not success:
                break

            self.batch_frames.append(frame)

            current_frame = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))

            # Update progress bar
            gui.progress_bar['value'] = (current_frame / self.total_frames) * 100
            gui.progress_label.configure(text=f"{floor((current_frame / self.total_frames) * 100)} %")
            gui.update()

            if len(self.batch_frames) >= self.batch_size:
                results = self.model(self.batch_frames, verbose=False)  # Run YOLO inference on the batch
                for result in results:
                    boxes = result.boxes
                    self.detect_entities(boxes, current_frame)

                self.batch_frames.clear()

        gui.progress_bar["value"] = 100
        gui.progress_label.configure(text="100 %")
        end_time = time()
        self.processing_time = end_time - start_time
        self.display_analysis_result(gui)

    def start(self, gui):
        selected_classes_indices = gui.categories_listbox.curselection()
        if len(selected_classes_indices) <= 0:
            gui.show_alert_message("error", "Class is missing", "You should choose one or multiple classes")
            return False
        else:
            self.selected_classes = [self.all_classes[i] for i in selected_classes_indices]
            self.stop_event.clear()
            # Start a worker thread for processing
            self.thread = Thread(target=self.worker, args=(gui,))
            self.thread.start()

    def stop(self):
        # Stop the worker thread safely
        self.stop_event.set()
        if self.thread.is_alive():
            self.thread.join()

    def display_analysis_result(self, gui):
        classes_count = {class_name: 0 for class_name in self.all_classes}
        f = open("log.txt","w")
        for e in self.entities:
            classes_count[e.class_] = classes_count[e.class_] + 1
            f.write(f"> A {e.class_} showed up at {self.convert_time(e.first_appeared_time)}\n")
        f.write(f"Processing time :{self.convert_time(self.processing_time)}\n")
        for cls,count in classes_count.items():
            if count > 0:
                f.write(f"{cls} : {count}\n")
        f.close()

        gui.result_entry.configure(text_color = "red")
        gui.put_text(gui.result_entry,"> Analysis complete , check the log file")

    def convert_time(self, t):
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
