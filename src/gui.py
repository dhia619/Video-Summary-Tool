import customtkinter as ctk
from tkinter import Listbox
from tkinter import ttk
from tkinter import messagebox
from settings import *

class APPGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Window settings
        ctk.set_appearance_mode("light")
        self.title("Analyze Video Tool")
        self.geometry("850x500")
        self.minsize(800,400)
        self.configure(fg_color="white")


        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=6)

        # left frame for settings 
        self.left_frame = ctk.CTkFrame(self, fg_color="white")
        self.left_frame.grid(row=0, column=0, sticky="nsw")

        self.setting_label = ctk.CTkLabel(self.left_frame, text="Settings", font=("courier", 22, "bold"), fg_color="white", text_color="orange")
        self.setting_label.pack(pady=10)

        self.models_label = ctk.CTkLabel(self.left_frame, text="Model", font=("courier", 18, "bold"))
        self.models_label.pack(padx=15, anchor="w")

        self.models_dropdown = ctk.CTkComboBox(self.left_frame, values=models, font=("courier",18))
        self.models_dropdown.pack(padx=15, pady=5, anchor="w", fill = ctk.X)

        self.categories_label = ctk.CTkLabel(self.left_frame, text="Categories", font=("courier", 18, "bold"))
        self.categories_label.pack(padx=15, pady=5, anchor="w")

        # Frame to hold Listbox and Scrollbar together
        self.categories_frame = ctk.CTkFrame(self.left_frame, fg_color="white")
        self.categories_frame.pack(padx=15, pady=5, anchor="w", fill=ctk.BOTH, expand=True)

        # Listbox and Scrollbar
        self.categories_listbox = Listbox(self.categories_frame, selectmode="multiple", font=("courier", 20), relief="flat")
        self.categories_listbox.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)

        self.categories_listbox_scrollbar = ttk.Scrollbar(self.categories_frame)
        self.categories_listbox_scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)


        # Configure scrollbar with the Listbox
        self.categories_listbox.config(yscrollcommand=self.categories_listbox_scrollbar.set)
        self.categories_listbox_scrollbar.configure(command=self.categories_listbox.yview)

        # Insert class names into the Listbox
        for cls in classes:
            self.categories_listbox.insert(ctk.END, cls)

        # Right frame for processing
        self.right_frame = ctk.CTkFrame(self, fg_color="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.processing_label = ctk.CTkLabel(self.right_frame, text = "Analyser", font=("courier", 22, "bold"), fg_color="white", text_color="orange")
        self.processing_label.pack(pady = 20)
        self.start_button = ctk.CTkButton(self.right_frame, text = "Start", font = ("courier",20))
        self.start_button.pack(pady = 10)
        self.progress_bar = ttk.Progressbar(self.right_frame, orient="horizontal", mode="determinate", length=350)
        self.progress_bar.pack(padx = 60, pady = 30, fill = ctk.X)
        self.progress_label = ctk.CTkLabel(self.right_frame, text = "0 %", font = ("courier",20))
        self.progress_label.pack()

        self.result_entry = ctk.CTkTextbox(self.right_frame, font = ("courier",20))
        self.result_entry.pack(padx = 60, pady = 10, fill = ctk.X)


    def put_text(self,widget,text):
        widget.insert(ctk.END,text)

    def show_alert_message(self,alert_type,title,msg):
        if alert_type == "error":
            messagebox.showerror(title,msg)
        elif alert_type == "warning":
            messagebox.showwarning(title,msg)
        elif alert_type == "info":
            messagebox.showinfo(title,msg)