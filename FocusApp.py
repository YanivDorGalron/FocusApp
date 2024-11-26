import datetime
import json
import threading

import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from playsound import playsound

from utils import add_focus_session_to_calendar, get_resource_path
from consts import COLORS

class FocusApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Focus Tracker 2024")
        self.geometry("600x800")  # Increased height to accommodate new widgets
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.is_focus_running = False
        self.is_break_running = False
        self.is_paused = False
        self.focus_duration = 0
        self.elapsed_time = 0
        self.start_time = None
        self.task = ""
        self.total_focus_time = 0
        self.sessions_completed = 0
        self.daily_focus_times = {}

        self.load_stats()
        self.create_widgets()
        self.after(1000, self.update_timers)
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        if self.is_focus_running:
            if messagebox.askyesno("Quit", "Do you really want to quit?"):
                destroy = True
                self.save_stats()  # Save stats before closing
        else:
            destroy = True
        
        if destroy:
            self.quit()
            self.destroy()


    def create_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)

        # Timer Frame
        timer_frame = ctk.CTkFrame(main_frame, fg_color="#2a2d2e", corner_radius=15)
        timer_frame.grid(row=0, column=0, pady=(0, 10), sticky="ew")
        timer_frame.grid_columnconfigure(0, weight=1)

        self.focus_timer_label = ctk.CTkLabel(timer_frame, text="00:00",
                                              font=ctk.CTkFont(size=40, weight="bold"),
                                              text_color="#4CAF50")
        self.focus_timer_label.grid(row=0, column=0, pady=(10, 10))

        self.break_timer_label = ctk.CTkLabel(timer_frame, text="00:00",
                                              font=ctk.CTkFont(size=40, weight="bold"),
                                              text_color="#4CAF50")
        self.break_timer_label.grid(row=0, column=0, pady=(10, 10))

        self.task_label = ctk.CTkLabel(timer_frame, text="Current Task: None",
                                       font=ctk.CTkFont(size=16))
        self.task_label.grid(row=1, column=0, pady=(0, 10))

        self.setted_focus_time_label = ctk.CTkLabel(timer_frame, text="Setted Focus Time: 0 min",
                                       font=ctk.CTkFont(size=16))
        self.setted_focus_time_label.grid(row=2, column=0, pady=(0, 10))

        plus_minus_frame = ctk.CTkFrame(timer_frame)
        plus_minus_frame.grid(row=3, column=0, padx=5, pady=5)

        self.plus_5min_button = ctk.CTkButton(plus_minus_frame, text="+5 min", command=self.add_5_minutes, font=ctk.CTkFont(size=12),width =10)
        self.plus_5min_button.grid(row=0, column=1, pady=(0, 10),padx=10)
        self.minus_5min_button = ctk.CTkButton(plus_minus_frame, text="-5 min", command=self.minus_5_minutes, font=ctk.CTkFont(size=12),width =10)
        self.minus_5min_button.grid(row=0, column=0, pady=(0, 10),padx=10)

        # Input Frame
        input_frame = ctk.CTkFrame(main_frame)
        input_frame.grid(row=1, column=0, pady=(0, 10), sticky="ew")
        input_frame.grid_columnconfigure(1, weight=1)

        # Task Entry
        ctk.CTkLabel(input_frame, text="Task:").grid(row=0, column=0, padx=(10, 5), pady=5, sticky="w")
        self.task_entry = ctk.CTkEntry(input_frame, width=300)
        self.task_entry.grid(row=0, column=1, padx=(0, 10), pady=5, sticky="ew")

        # Focus Duration Entry
        ctk.CTkLabel(input_frame, text="Duration (min):").grid(row=1, column=0, padx=(10, 5), pady=5, sticky="w")
        self.focus_entry = ctk.CTkEntry(input_frame, width=100)
        self.focus_entry.grid(row=1, column=1, padx=(0, 10), pady=5, sticky="w")

        # CC Email Entry
        ctk.CTkLabel(input_frame, text="CC Email:").grid(row=2, column=0, padx=(10, 5), pady=5, sticky="w")
        self.cc_email_entry = ctk.CTkEntry(input_frame, width=300, placeholder_text="Optional")
        self.cc_email_entry.grid(row=2, column=1, padx=(0, 10), pady=5, sticky="ew")

        # Buttons
        button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        button_frame.grid(row=2, column=0, pady=(0, 20), sticky="ew")
        button_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.start_focus_button = ctk.CTkButton(button_frame, text="Start Focus", command=self.start_focus_session,
                                                fg_color="#4CAF50", hover_color="#45a049")
        self.start_focus_button.grid(row=0, column=0, padx=5)

        self.pause_button = ctk.CTkButton(button_frame, text="Pause", command=self.pause_focus_session,
                                          state="disabled", fg_color="#FFA500", hover_color="#FF8C00")
        self.pause_button.grid(row=0, column=1, padx=5)

        self.stop_button = ctk.CTkButton(button_frame, text="Stop", command=self.stop_focus_session,
                                         state="disabled", fg_color="#F44336", hover_color="#D32F2F")
        self.stop_button.grid(row=0, column=2, padx=5)

        # Statistics Frame
        stats_frame = ctk.CTkFrame(main_frame)
        stats_frame.grid(row=3, column=0, pady=(0, 20), sticky="ew")
        stats_frame.grid_columnconfigure(0, weight=1)

        self.total_focus_label = ctk.CTkLabel(stats_frame,
                                              text=f"Total Focus Time: {self.format_time(self.total_focus_time)}",
                                              font=ctk.CTkFont(size=14, weight="bold"))
        self.total_focus_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.sessions_label = ctk.CTkLabel(stats_frame, text=f"Sessions Completed: {self.sessions_completed}",
                                           font=ctk.CTkFont(size=14, weight="bold"))
        self.sessions_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        # Options Frame
        options_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        options_frame.grid(row=4, column=0, pady=(0, 20), sticky="ew")
        options_frame.grid_columnconfigure((0, 1), weight=1)

        self.reset_stats_button = ctk.CTkButton(options_frame, text="Reset Statistics", command=self.reset_stats,
                                                fg_color="#607D8B", hover_color="#455A64")
        self.reset_stats_button.grid(row=0, column=0, padx=5)

        self.freq_sound_var = tk.BooleanVar(value=True)
        self.freq_sound_toggle = ctk.CTkSwitch(options_frame, text="Enable Frequent Sounds", variable=self.freq_sound_var)
        self.freq_sound_toggle.grid(row=0, column=2, padx=5)
        
        self.sound_var = tk.BooleanVar(value=True)
        self.sound_toggle = ctk.CTkSwitch(options_frame, text="Enable Sounds", variable=self.sound_var)
        self.sound_toggle.grid(row=0, column=1, padx=5)

        # Productivity Graph
        self.fig, self.ax = plt.subplots(figsize=(5, 3))
        self.canvas = FigureCanvasTkAgg(self.fig, master=main_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.grid(row=5, column=0, pady=(0, 20), sticky="ew")

        self.update_productivity_graph()

        # Dropdown label
        label = ctk.CTkLabel(input_frame, text="Color:", font=("Arial", 14))
        label.grid(row=3, column=0, padx=(10, 5), pady=5, sticky="w")

        # Dropdown menu for selecting colors
        self.color_var = ctk.StringVar(value="1: Light Blue")  # Default selection
        self.selected_color_id = 1
        color_info = COLORS[self.selected_color_id]

        self.color_dropdown = ctk.CTkOptionMenu(
            input_frame,
            variable=self.color_var,
            values=[f"{color_id}: {color_info['name']}" for color_id, color_info in COLORS.items()],
            command=self.on_color_select,  # Called when a selection is made
            fg_color=color_info["background"],
            text_color="#000000",  # Set the text color to black
            button_color = color_info["background"],
        )

        self.color_dropdown.grid(row=3, column=1, pady=(0, 10), sticky="ew")
        
    def add_5_minutes(self):
        if self.focus_duration == 0:
            messagebox.showwarning("Warning", "Please Start a session first.")
        else:
            self.focus_duration += 5
            self.setted_focus_time_label.configure(text=f"Setted Focus Time: {self.focus_duration} min")

    def minus_5_minutes(self):
        if self.focus_duration == 0:
            messagebox.showwarning("Warning", "Please Start a session first.")
        elif self.focus_duration > 5:
            self.focus_duration -= 5
        else:
            self.focus_duration = 0
        self.setted_focus_time_label.configure(text=f"Setted Focus Time: {self.focus_duration} min")

    def start_focus_session(self):
        if not self.is_focus_running:
            try:
                self.focus_duration = int(self.focus_entry.get())
                self.task = self.task_entry.get()
                if not self.task:
                    messagebox.showwarning("Warning", "Please enter a task description.")
                    return
                self.elapsed_time = 0
                self.is_paused = False
                self.task_label.configure(text=f"Current Task: {self.task}")
                self.pause_button.configure(state="normal")
                self.stop_button.configure(state="normal")
                self.start_time = datetime.datetime.utcnow()
                self.is_focus_running = True
                self.is_break_running = False
                self.break_timer_label.configure(text="")
                threading.Thread(target=self.run_timer, daemon=True).start()
                self.setted_focus_time_label.configure(text=f"Setted Focus Time: {self.focus_duration} min")
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for focus duration.")

    def pause_focus_session(self):
        if self.is_focus_running:
            if self.is_paused:
                self.is_paused = False
                self.pause_button.configure(text="Pause")
            else:
                self.is_paused = True
                self.pause_button.configure(text="Resume")


    def update_focus_timer(self):
        text = self.format_time(self.elapsed_time)
        self.focus_timer_label.configure(text=f"Focus Timer: {text}")

    def stop_focus_session(self):
        if self.is_focus_running:
            self.is_focus_running = False
            self.update_stats()
            self.log_focus_to_calendar()
            self.reset_focus_timer()
            self.start_break_timer()

    def reset_focus_timer(self):
        self.elapsed_time = 0
        self.is_focus_running = False
        self.is_paused = False
        self.focus_timer_label.configure(text="Focus Timer: 00:00")
        self.pause_button.configure(state="disabled")
        self.stop_button.configure(state="disabled")
        self.start_focus_button.configure(state="normal")

    def log_focus_to_calendar(self):
        if self.start_time:
            elapsed_minutes = self.elapsed_time // 60
            cc_email = self.cc_email_entry.get()
            add_focus_session_to_calendar(self.start_time, elapsed_minutes, self.task, cc_email if cc_email else None, self.selected_color_id)

    def run_timer(self):
        self.start_time = datetime.datetime.utcnow()
        self.last_notification = 0
        self.update_timers()
    
    
    def update_timers(self):
        if self.is_focus_running and not self.is_paused:
            current_time = datetime.datetime.utcnow()
            self.elapsed_time = int((current_time - self.start_time).total_seconds())
            self.update_focus_timer()

            # Play sound every 15 minutes
            if self.elapsed_time - self.last_notification >= 900 and self.freq_sound_var.get():  # 900 seconds = 15 minutes
                self.play_sound(get_resource_path("sounds/wow-171498.mp3"))
                self.last_notification = self.elapsed_time

            if self.elapsed_time >= self.focus_duration * 60:
                self.is_focus_running = False
                self.play_sound(get_resource_path("sounds/success-fanfare-trumpets-6185.mp3"))
                self.log_focus_to_calendar()
                self.update_stats()
                self.reset_focus_timer()
                self.start_break_timer()
            else:
                self.after(1000, self.update_timers)
        elif self.is_break_running:
            text = self.format_time(int((datetime.datetime.utcnow() - self.start_time).total_seconds()))
            self.break_timer_label.configure(text=f"Break Timer: {text}")
            self.after(1000, self.update_timers)
    
    
    
    def start_break_timer(self):
        self.start_time = datetime.datetime.utcnow()
        self.is_focus_running = False
        self.is_break_running = True
        self.break_timer_label.configure(text="Break Timer: 00:00")
        self.update_timers()


    def update_stats(self):
        self.total_focus_time += self.elapsed_time
        self.sessions_completed += 1
        self.total_focus_label.configure(text=f"Total Focus Time: {self.format_time(self.total_focus_time)}")
        self.sessions_label.configure(text=f"Sessions Completed: {self.sessions_completed}")

        # Update daily focus times
        today = datetime.date.today().isoformat()
        if today in self.daily_focus_times:
            self.daily_focus_times[today] += self.elapsed_time
        else:
            self.daily_focus_times[today] = self.elapsed_time

        self.save_stats()
        self.update_productivity_graph()

    def reset_stats(self):
        if messagebox.askyesno("Reset Statistics", "Are you sure you want to reset your statistics?"):
            self.total_focus_time = 0
            self.sessions_completed = 0
            self.daily_focus_times = {}
            self.total_focus_label.configure(text="Total Focus Time: 00:00:00")
            self.sessions_label.configure(text="Sessions Completed: 0")
            self.save_stats()
            self.update_productivity_graph()

    def save_stats(self):
        stats = {
            "total_focus_time": self.total_focus_time,
            "sessions_completed": self.sessions_completed,
            "daily_focus_times": self.daily_focus_times
        }
        with open("focus_stats.json", "w") as f:
            json.dump(stats, f)

    def load_stats(self):
        try:
            with open("focus_stats.json", "r") as f:
                stats = json.load(f)
                self.total_focus_time = stats.get("total_focus_time", 0)
                self.sessions_completed = stats.get("sessions_completed", 0)
                self.daily_focus_times = stats.get("daily_focus_times", {})
        except FileNotFoundError:
            self.total_focus_time = 0
            self.sessions_completed = 0
            self.daily_focus_times = {}

    @staticmethod
    def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours == 0:
            text = f"{minutes:02}:{seconds:02}"
        else:
            text = f"{hours:02}:{minutes:02}:{seconds:02}"
        return text

    def play_sound(self, sound_file):
        if self.sound_var.get():
            try:
                playsound(sound_file)
            except Exception as e:
                print(f"Error playing sound: {e}")

    def update_productivity_graph(self):
        self.ax.clear()
        dates = list(self.daily_focus_times.keys())[-7:]  # Last 7 days
        times = [self.daily_focus_times[date] / 3600 for date in dates]  # Convert to hours
        dates = [date.split("-")[1] + "-" + date.split("-")[2] for date in dates]
        if len(times) == 0:
            average_time = 0
        else:   
            average_time = sum(times) / len(times)

        self.ax.bar(dates, times, color='skyblue')
        self.ax.axhline(average_time, color='red', linestyle='--', label='Average Time')
        self.ax.set_xlabel('Date')
        self.ax.set_ylabel('Focus Time (hours)')
        self.ax.set_title('Daily Focus Time (Last 7 Days)')
        self.ax.tick_params(axis='x')
        max_time = max(times) if times else 1
        self.ax.set_yticks([i for i in range(0, int(max_time)+1)])  # Set y-ticks to be every hour
        self.fig.tight_layout()
        self.canvas.draw()

    def on_color_select(self, event):
        """Update the preview label with the selected color."""
        self.selected_color_id = int(self.color_var.get().split(':')[0])
        color_info = COLORS[self.selected_color_id]
        self.color_dropdown.configure(fg_color=color_info["background"],
                                      button_color = color_info["background"],)  # Update background color

if __name__ == "__main__":
    app = FocusApp()
    app.mainloop()
