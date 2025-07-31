# Habit Tracker (CLI-Based)

A command-line based Habit Tracker built in Python with SQLite for data storage. This tool helps you develop and stick to your daily and weekly habits by tracking progress, maintaining streaks, and analyzing patterns.

---

## Features

-  Add new habits (Daily / Weekly)
-  Track completion and update streaks
-  Automatically reset overdue habits
-  Edit, delete, or change frequency of habits
-  View habit analytics: longest/shortest streak
-  Data persistence using SQLite
-  Load predefined habits at startup
-  Clean, menu-driven CLI interface

---

## Tech Stack

- **Python 3**
- **SQLite (sqlite3 module)**
- `datetime` – to manage due dates
- `time` – for delay handling between actions

---

##  How to Run

1. **Clone the repo**  
```bash
git clone https://github.com/yourusername/habit-tracker-cli.git
cd habit-tracker-cli
```

2. **Run the script**  
```bash
python habit_tracker.py
```

>  Make sure Python 3 is installed.

---

##  Project Structure

```
habit-tracker-cli/
│
├── habit_tracker.py          # Main CLI logic
├── habits.db                 # SQLite database (created on first run)
├── README.md                 # This file
└── screenshots/              # Sample outputs for demo
```

---

##  Author

**Darpan**  
email:- darpanpallati@gmail.com

---

