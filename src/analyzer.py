from cv2 import VideoCapture, rectangle, CAP_PROP_FRAME_COUNT, CAP_PROP_FPS, CAP_PROP_POS_FRAMES, cvtColor, COLOR_BGR2RGB
from ultralytics import YOLO
from sort import Sort
import numpy as np
from time import time
from math import floor
from threading import Thread, Event
from PIL import Image
from settings import models,actual_models_names
from os import path, makedirs, chdir
from collections import defaultdict
from cvzone import putTextRect
from torch import cuda
from queue import Queue
from visualizer import *
class Entity:
    def __init__(self, cls, id_, t, conf):
        self.id = id_
        self.class_ = cls
        self.confidence = conf
        self.first_appeared_time = t

class Analyzer:
    def __init__(self, classes):
        self.all_classes = classes
        self.selected_classes = []
        self.tracker = Sort(max_age=60, min_hits=40, iou_threshold=0.1)

        self.batch_frames = []
        self.batch_size = 32
        self.frame_queue = Queue(maxsize=1000)  # Queue to store frames
        self.stop_event = Event()  # To safely stop the thread

        if not path.exists("history"):
            makedirs("history")
        chdir("history")

    def detect_entities(self, boxes, current_frame_index, current_frame):
        detections = np.empty((0, 5))
        temp_classes = []
        timestamps = []
        confidences = []
        self.critical_scenes = []
        registred_old_length = len(self.registered_entities)

        # Filter detected objects
        for bbox in boxes:
            class_ = self.all_classes[int(bbox.cls[0])]
            confidence = round(bbox.conf[0].item(), 2)
            if class_ in self.selected_classes and confidence > 0.5:
                x1, y1, x2, y2 = map(int, bbox.xyxy[0])
                detections = np.vstack((detections, np.array([x1, y1, x2, y2, confidence])))
                temp_classes.append(class_)
                confidences.append(confidence)
                timestamps.append(current_frame_index / self.frame_rate)

        # Track filtered objects
        tracking_results = self.tracker.update(dets=detections)
        for tracking_result, cls_, t, conf in zip(tracking_results, temp_classes, timestamps, confidences):
            x1, y1, x2, y2, id_ = map(int, tracking_result)
            if id_ not in self.registered_entities:
                self.registered_entities.append(id_)
                self.entities.append(Entity(cls_, id_, t, conf))
                rectangle(current_frame, (x1,y1),(x2,y2),(255,0,0))

        # If new objects showed , we save a screenshot
        if registred_old_length < len(self.registered_entities):
            putTextRect(current_frame, self.convert_time(t), (10,40))
            self.save_critical_scene(current_frame, self.convert_time(t).replace(":","-"))
        
    def save_critical_scene(self, frame, t):
        # Ensure the directory for saving frames exists
        if not path.exists(f"{self.target_dir_name}/critical_scenes"):
            makedirs(f"{self.target_dir_name}/critical_scenes")

        # Convert the frame to RGB
        frame_rgb = cvtColor(frame, COLOR_BGR2RGB)

        file_name = f"{self.target_dir_name}/critical_scenes/{t}.jpg"
        
        # Save the frame as an image
        Image.fromarray(frame_rgb).save(file_name)

    def read_frames(self):
        """Producer: Reads frames and puts them into the queue"""
        while not self.stop_event.is_set():
            success, frame = self.video.read()
            if not success:
                break
            self.frame_queue.put(frame)
        self.frame_queue.put(None)  # Signal that video reading is done

    def process_frames(self, gui):
        """Consumer: Processes frames from the queue in batches"""
        batch_frames = []
        start_time = time()

        while True:
            frame = self.frame_queue.get()
            if frame is None:
                break  # Stop when producer signals that reading is done

            batch_frames.append(frame)

            # Get current frame index
            current_frame = int(self.video.get(CAP_PROP_POS_FRAMES))

            if len(batch_frames) >= self.batch_size:
                results = self.model(batch_frames, verbose=False)
                for result in results:
                    boxes = result.boxes
                    self.detect_entities(boxes, current_frame, frame)

                batch_frames.clear()

            # Update progress bar
            gui.progress_bar['value'] = (current_frame / self.total_frames) * 100
            gui.progress_label.configure(text=f"{floor((current_frame / self.total_frames) * 100)} %")
            gui.update()
        
        # Process any remaining frames after the main loop
        if len(self.batch_frames) > 0:
            results = self.model(self.batch_frames, verbose=False)  # Run YOLO inference on the remaining frames
            for result in results:
                boxes = result.boxes
                self.detect_entities(boxes, current_frame, frame)

            self.batch_frames.clear()

        gui.progress_bar["value"] = 100
        gui.progress_label.configure(text="100 %")
        end_time = time()
        self.processing_time = end_time - start_time
        self.display_analysis_result(gui)

    def start(self, gui):

        gui.start_button.configure(state="disabled")

        try:
            gui.clear_text(gui.result_entry)
        except:pass

        self.stop()  # Stop any existing threads or processes
        self.frame_queue.queue.clear()  # Clear any remaining frames in the queue

        self.entities = []
        self.registered_entities = []
        self.critical_scenes = []
        self.batch_frames.clear() 
        self.tracker = Sort(max_age=60, min_hits=40, iou_threshold=0.1)

        self.processing_time = 0

        gui.progress_bar["value"] = 0
        gui.progress_label.configure(text="0 %")

        self.selected_classes = gui.get_selected_categories()
        model_path = gui.models_dropdown.get()
        model_path = actual_models_names[models.index(model_path)]

        device = 'cuda' if cuda.is_available() else 'cpu'

        if model_path:
            self.model = YOLO(f"../models/{model_path}").to(device)
        else:
            gui.show_alert_message("error", "Missing Model", "Please select a model")
            return False

        self.video_path = gui.video_file
        if not self.video_path:
            gui.show_alert_message("error", "Missing Video", "Please upload a video")
            return False 

        self.video = VideoCapture(self.video_path)
        self.total_frames = self.video.get(CAP_PROP_FRAME_COUNT)
        self.frame_rate = self.video.get(CAP_PROP_FPS)

        self.target_dir_name = self.video_path.split("/")[-1]
        if not path.exists(self.target_dir_name):
            makedirs(self.target_dir_name)

        if len(self.selected_classes) <= 0:
            gui.show_alert_message("error", "Class is missing", "You should choose one or multiple classes")
            return False
        else:
            self.stop_event.clear()

            # Start the producer thread (to read frames)
            self.read_thread = Thread(target=self.read_frames)
            self.read_thread.start()

            # Start the consumer thread (to process frames)
            self.process_thread = Thread(target=self.process_frames, args=(gui,))
            self.process_thread.start()

    def stop(self):
        self.stop_event.set()
        if hasattr(self, 'read_thread') and self.read_thread.is_alive():
            self.read_thread.join()
        if hasattr(self, 'process_thread') and self.process_thread.is_alive():
            self.process_thread.join()

    def display_analysis_result(self, gui):
        # Create a dictionary to group entities by time and class
        grouped_entities = defaultdict(lambda: defaultdict(int))
        with open(f"{self.target_dir_name}/log.txt", "w") as f:
            # Group entities by their class and appearance time
            for entity in self.entities:
                # Convert appearance time to a formatted string
                time_str = self.convert_time(entity.first_appeared_time)
                grouped_entities[time_str][entity.class_] += 1

            # Write the processing time
            f.write(f"Processing time: {self.convert_time(self.processing_time)}\n")
            
            # Write the grouped information to the log
            for time_str, classes in grouped_entities.items():
                for class_, count in classes.items():
                    f.write(f"> {count} {class_}(s) showed up at {time_str}\n")


            # Write a summary of the total count of each class
            classes_count = {class_name: 0 for class_name in self.all_classes}
            for entity in self.entities:
                classes_count[entity.class_] += 1

            for class_, count in classes_count.items():
                if count > 0:
                    f.write(f"{class_}: {count}\n")

        # Save the image of the plot showing the content of the log
        generate_graph(f"{self.target_dir_name}/log.txt",self.target_dir_name)

        # Show analysis completion message in the GUI
        gui.put_text(gui.result_entry, "> Analysis complete :D\n", "red")
        gui.result_entry.tag_config("red", foreground="red")
        gui.put_text(gui.result_entry, "> you will find the log and critical scenes under :\n","blue")
        gui.result_entry.tag_config("blue", foreground="blue")
        gui.put_text(gui.result_entry, "> history/", "green");gui.put_text(gui.result_entry, f"{self.target_dir_name}/", "brown")
        gui.result_entry.tag_config("green", foreground="green");gui.result_entry.tag_config("brown",foreground="brown")
        gui.show_alert_message('info', "Success", "Analysis Completed Successfully.")

        gui.start_button.configure(state="enabled")

    def convert_time(self, t):
        hours = int(t // 3600)
        minutes = int((t % 3600) // 60)
        seconds = int(t % 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"