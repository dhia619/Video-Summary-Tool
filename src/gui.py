import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from settings import *

class APPGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window settings
        ctk.set_appearance_mode("light")
        self.title("Video Summary Tool")
        self.geometry("850x500")
        self.minsize(800,400)
        self.configure(fg_color="white")

        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=6)

        self.video_file = ""

        # Left frame for settings 
        self.left_frame = ctk.CTkFrame(self, fg_color="white")
        self.left_frame.grid(row=0, column=0, sticky="nsw")

        self.setting_label = ctk.CTkLabel(self.left_frame, text="Settings", font=("Segoe UI", 22, "bold"), fg_color="white", text_color="orange")
        self.setting_label.pack(pady=10)

        self.models_label = ctk.CTkLabel(self.left_frame, text="Model", font=("Segoe UI", 18, "bold"))
        self.models_label.pack(padx=15, anchor="w")

        self.models_dropdown = ctk.CTkComboBox(self.left_frame, values=models, font=("Segoe UI",18))
        self.models_dropdown.pack(padx=15, pady=5, anchor="w", fill=ctk.X)

        self.categories_label = ctk.CTkLabel(self.left_frame, text="Categories", font=("Segoe UI", 18, "bold"))
        self.categories_label.pack(padx=15, pady=5, anchor="w")

        # Frame to hold the scrollable checkboxes
        self.scrollable_frame = ctk.CTkScrollableFrame(self.left_frame, fg_color="white", height=200)
        self.scrollable_frame.pack(padx=15, pady=5, anchor="w", fill=ctk.BOTH, expand=True)

        # Create a variable to store the states of the checkboxes
        self.checkbox_vars = {}

        # Add "All" checkbox
        self.all_var = ctk.BooleanVar()  # Variable for the "All" checkbox
        self.all_checkbox = ctk.CTkCheckBox(self.scrollable_frame, text="All", variable=self.all_var, command=self.toggle_all_checkboxes, font=("Segoe UI", 20))
        self.all_checkbox.pack(anchor="w", padx=5, pady=5)

        # Add checkboxes for each class in the `classes` list
        for cls in classes:
            var = ctk.BooleanVar()  # Each checkbox needs its own variable
            checkbox = ctk.CTkCheckBox(self.scrollable_frame, text=cls, variable=var, command=self.update_all_checkbox, font=("Segoe UI", 20))
            checkbox.pack(anchor="w", padx=5, pady=5)
            self.checkbox_vars[cls] = var  # Store the variable associated with each class

        # Right frame for processing
        self.right_frame = ctk.CTkFrame(self, fg_color="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")
        
        self.upload_button = ctk.CTkButton(self.right_frame, text="Upload Video", command=self.upload_video, font=("Segoe UI", 20))
        self.upload_button.pack(pady=20)
        
        self.selected_file_label = ctk.CTkLabel(self.right_frame, text="No file selected", font=("Segoe UI", 16))
        self.selected_file_label.pack(pady=10)

        self.start_button = ctk.CTkButton(self.right_frame, text = "Start", font = ("Segoe UI",20))
        self.start_button.pack(pady = 10)

        self.preview_label = ctk.CTkLabel(self.right_frame, text="")
        self.preview_label.pack(pady = 10)
        
        self.progress_bar = ttk.Progressbar(self.right_frame, orient="horizontal", mode="determinate", length=350)
        self.progress_bar.pack(padx = 60, pady = 30, fill = ctk.X)
        
        self.progress_label = ctk.CTkLabel(self.right_frame, text = "0 %", font = ("Segoe UI",20))
        self.progress_label.pack()

        self.result_entry = ctk.CTkTextbox(self.right_frame, font = ("Segoe UI",20))
        self.result_entry.pack(padx = 60, pady = 10, fill = ctk.BOTH)

    def put_text(self, widget, text, color = "black"):
        widget.insert(ctk.END, text, color)

    def clear_text(self, widget):
        widget.delete("1.0", ctk.END)

    def show_alert_message(self, alert_type, title, msg):
        if alert_type == "error":
            messagebox.showerror(title, msg)
        elif alert_type == "warning":
            messagebox.showwarning(title, msg)
        elif alert_type == "info":
            messagebox.showinfo(title, msg)

    # Function to get the selected categories (checked checkboxes)
    def get_selected_categories(self):
        selected_classes = [cls for cls, var in self.checkbox_vars.items() if var.get()]
        return selected_classes
    
    def upload_video(self):
        # Open file dialog to select video file
        self.video_file = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=(("Video Files", "*.mp4 *.avi *.mov"), ("All Files", "*.*"))
        )
        if self.video_file:
            # Update label with selected file path
            self.selected_file_label.configure(text=f"Selected: {self.video_file.split('/')[-1]}")
        else:
            self.selected_file_label.configure(text="No file selected")

    def toggle_all_checkboxes(self):
        # Check or uncheck all checkboxes based on the "All" checkbox state
        state = self.all_var.get()
        for var in self.checkbox_vars.values():
            var.set(state)

    def update_all_checkbox(self):
        # If any checkbox is unchecked, also uncheck the "All" checkbox
        all_checked = all(var.get() for var in self.checkbox_vars.values())
        self.all_var.set(all_checked)
