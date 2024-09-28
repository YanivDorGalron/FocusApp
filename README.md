# FocusApp

**FocusApp** is a productivity tool designed to help you track and manage your focus sessions. It provides a visual timer, task management, and statistics tracking, along with a productivity graph that shows your focus time over the past week.

## Features

- **Focus Timer**: Start, pause, and stop focus sessions with customizable durations.
- **Break Timer**: Automatically starts a break timer after completing a focus session.
- **Task Management**: Enter and track tasks associated with each focus session.
- **Statistics Tracking**: View total focus time, number of completed sessions, and reset statistics if needed.
- **Productivity Graph**: Visualize your daily focus time for the last 7 days.
- **Sound Notifications**: Optionally enable sound notifications for session milestones.
- **Google Calendar Integration**: Will record past focus session on your google calendar. CC friends is possible.


<div style="display: flex; justify-content: space-between;">
    <img src="https://github.com/user-attachments/assets/06625bdc-6aea-4e7e-a0f3-9c55732f8ff8" alt="Image 1" style="height: 300px; object-fit: cover;"/>
    <img src="https://github.com/user-attachments/assets/27559d58-6a31-49c0-9074-ad8e2ad6d422" alt="Image 2" style="height: 300px; object-fit: cover;"/>
</div>

## Pyinstaller

To create an executable file using PyInstaller, follow these steps:

1. Install PyInstaller:
   ```
   pip install pyinstaller
   ```

2. Command to create executable:
    ```
     pyinstaller --add-data "sounds;sounds" FocusApp.py --name FocusApp --noconsole --add-data "cred.json;." --onefile" 
    ```

3. The executable file will be generated in the `dist` folder.

## cred.json

1. You need to create a cred.json. You can get it by creating a project on google cloud platform and enabling the google calendar api. 
