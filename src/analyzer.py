import cv2
from ultralytics import YOLO
from sort import Sort
import numpy as np
from time import time

class Entity:
    def __init__(self, cls, id_):
        self.id = id_
        self.class_ = cls
        self.first_appeared_time = time()

class Analyzer:
    def __init__(self, video_path, path_to_model, classes):
        self.model = YOLO(path_to_model)
        self.video = cv2.VideoCapture(video_path)
        self.total_frames = self.video.get(cv2.CAP_PROP_FRAME_COUNT)
        self.all_classes = classes
        self.selected_classes = []
        self.entities = []
        self.registered_entities = []
        self.tracker = Sort(max_age=20, min_hits=10, iou_threshold=0.7)

        self.batch_size = 6
        self.batch_frames = []

        self.processing_time = 0

    def detect_entities(self, boxes):
        detections = np.empty((0, 5))
        temp_classes = []
        for bbox in boxes:
            class_ = self.all_classes[int(bbox.cls[0])]
            confidence = round(bbox.conf[0].item(), 2)
            if class_ in self.selected_classes and confidence > 0.4:
                x1, y1, x2, y2 = map(int, bbox.xyxy[0])
                detections = np.vstack((detections, np.array([x1, y1, x2, y2, confidence])))
                temp_classes.append(class_)

        tracking_results = self.tracker.update(dets=detections)
        for tracking_result, cls_ in zip(tracking_results,temp_classes):
            x1, y1, x2, y2, id_ = map(int, tracking_result)
            if id_ not in self.registered_entities:
                self.registered_entities.append(id_)
                self.entities.append(Entity(cls_, id_))

    def start(self, gui):
        
        start_time = time()
        gui.progress_bar["value"] = 0

        selected_classes_indices = gui.categories_listbox.curselection()
        if len(selected_classes_indices) <= 0:
            gui.show_alert_message("error","Class is missing","You should choose one or multiple classes")
            return False
        else:
            self.selected_classes = [self.all_classes[i] for i in selected_classes_indices]
            while True:
                
                success, frame = self.video.read()
                if not success:
                    break
                self.batch_frames.append(frame)  # Add frame to batch
                
                # Update progress bar
                current_frame = int(self.video.get(cv2.CAP_PROP_POS_FRAMES))
                gui.progress_bar['value'] = (current_frame / self.total_frames) * 100
                gui.update()

                if len(self.batch_frames) >= self.batch_size:
                    results = self.model(self.batch_frames, verbose=False)  # Run YOLO inference on the batch
                    for result in results:
                        boxes = result.boxes
                        self.detect_entities(boxes)

                    self.batch_frames.clear()
            
            end_time = time()
            self.processing_time = end_time - start_time

            self.display_analysis_result(gui)
                
    def display_analysis_result(self,gui):
        classes_count = {class_name: 0 for class_name in self.all_classes}
        for e in self.entities:
            classes_count[e.class_] = classes_count[e.class_] + 1
        gui.put_text(gui.result_entry,f"Processing time :{self.processing_time:.2} seconds\n")
        for cls,count in classes_count.items():
            if count > 0:
                gui.put_text(gui.result_entry,f"{cls} : {count}\n")