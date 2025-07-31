import sqlite3
from datetime import datetime, timedelta
import time

DB_NAME = "habits.db"

class Habit:
    def __init__(self, title, period='daily', due_date=None, streak=0, habit_id=None):
        self.id = habit_id  # database primary key
        self.title = title
        self.period = period  # 'daily' or 'weekly'
        self.due_date = due_date if due_date else self.calculate_due_date()
        self.streak = streak

    def calculate_due_date(self):
        today = datetime.now().date()
        if self.period == 'daily':
            return today + timedelta(days=1)
        elif self.period == 'weekly':
            return today + timedelta(weeks=1)
        else:
            return today + timedelta(days=1)  # default daily

    def reset_if_overdue(self):
        today = datetime.now().date()
        if self.due_date < today:
            self.streak = 0
            self.due_date = self.calculate_due_date()
            return True
        return False

    def complete_task(self):
        today = datetime.now().date()
        if self.due_date >= today:
            self.streak += 1
            self.due_date = self.calculate_due_date()
            return True
        else:
            print(f"Task '{self.title}' is overdue and was reset. Complete it again.")
            self.reset_if_overdue()
            return False


class HabitTracker:
    def __init__(self):
        print("HABIT TRACKER STARTED")
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                period TEXT CHECK(period IN ('daily', 'weekly')) NOT NULL,
                due_date TEXT NOT NULL,
                streak INTEGER NOT NULL
            )
        ''')
        self.conn.commit()
        print("Habit table initialized.")

    def recreate_table(self):
        print("Recreating the habits table...")
        self.cursor.execute('DROP TABLE IF EXISTS habits')
        self.conn.commit()
        self.create_table()
        print("Table recreated successfully.")

    def add_habit_to_db(self, habit):
        self.cursor.execute('''
            INSERT INTO habits (title, period, due_date, streak)
            VALUES (?, ?, ?, ?)
        ''', (habit.title, habit.period, habit.due_date.isoformat(), habit.streak))
        self.conn.commit()
        habit.id = self.cursor.lastrowid

    def update_habit_in_db(self, habit):
        self.cursor.execute('''
            UPDATE habits
            SET title = ?, period = ?, due_date = ?, streak = ?
            WHERE id = ?
        ''', (habit.title, habit.period, habit.due_date.isoformat(), habit.streak, habit.id))
        self.conn.commit()

    def delete_habit_from_db(self, habit_id):
        self.cursor.execute('DELETE FROM habits WHERE id = ?', (habit_id,))
        self.conn.commit()

    def fetch_all_habits(self):
        self.cursor.execute('SELECT * FROM habits')
        rows = self.cursor.fetchall()
        habits = []
        for row in rows:
            habit_id, title, period, due_date_str, streak = row
            due_date = datetime.fromisoformat(due_date_str).date()
            habits.append(Habit(title, period, due_date, streak, habit_id))
        return habits

    def reset_overdue_habits(self):
        print("Resetting overdue habits if any...")
        habits = self.fetch_all_habits()
        for habit in habits:
            if habit.reset_if_overdue():
                self.update_habit_in_db(habit)
                print(f"Habit '{habit.title}' was overdue and has been reset.")

    def add_predefined_habits(self):
        today = datetime.now().date()
        predefined = [
            Habit("Exercise", period='daily', due_date=today + timedelta(days=1), streak=0),
            Habit("Read Book", period='daily', due_date=today + timedelta(days=1), streak=0),
            Habit("Meditate", period='daily', due_date=today + timedelta(days=1), streak=0),
            Habit("Weekly Review", period='weekly', due_date=today + timedelta(weeks=1), streak=0),
            Habit("Plan Next Week", period='weekly', due_date=today + timedelta(weeks=1), streak=0),
        ]
        for habit in predefined:
            self.add_habit_to_db(habit)
        print("Predefined habits added.")

    def create_new_habit(self):
        title = input("Enter new habit title: ").strip()
        period = ''
        while period not in ['daily', 'weekly']:
            period = input("Enter period (daily/weekly): ").strip().lower()
            if period not in ['daily', 'weekly']:
                print("Please enter 'daily' or 'weekly'.")
        new_habit = Habit(title=title, period=period)
        self.add_habit_to_db(new_habit)
        print(f"New habit '{title}' added with {period} period and due date {new_habit.due_date}.")

    def delete_habit(self):
        habits = self.fetch_all_habits()
        self.list_all_habits(habits)
        title = input("Enter habit title to delete: ").strip().lower()
        for habit in habits:
            if habit.title.lower() == title:
                self.delete_habit_from_db(habit.id)
                print(f"Habit '{title}' deleted.")
                return
        print(f"Habit '{title}' not found.")

    def edit_habit_title(self):
        habits = self.fetch_all_habits()
        self.list_all_habits(habits)
        old_title = input("Enter current habit title to edit: ").strip().lower()
        for habit in habits:
            if habit.title.lower() == old_title:
                new_title = input("Enter new title: ").strip()
                habit.title = new_title
                self.update_habit_in_db(habit)
                print(f"Habit title updated from '{old_title}' to '{new_title}'.")
                return
        print(f"Habit '{old_title}' not found.")

    def change_habit_period(self, to_period):
        habits = self.fetch_all_habits()
        self.list_all_habits(habits)
        title = input(f"Enter habit title to change period to {to_period}: ").strip().lower()
        for habit in habits:
            if habit.title.lower() == title:
                habit.period = to_period
                habit.due_date = habit.calculate_due_date()
                self.update_habit_in_db(habit)
                print(f"Habit '{title}' period changed to {to_period} with new due date {habit.due_date}.")
                return
        print(f"Habit '{title}' not found.")

    def complete_task(self):
        habits = self.fetch_all_habits()
        self.list_all_habits(habits)
        title = input("Enter habit title to mark as completed: ").strip().lower()
        for habit in habits:
            if habit.title.lower() == title:
                if habit.complete_task():
                    self.update_habit_in_db(habit)
                    print(f"Habit '{title}' marked as completed. Streak: {habit.streak}")
                return
        print(f"Habit '{title}' not found.")

    def list_all_habits(self, habits=None):
        if habits is None:
            habits = self.fetch_all_habits()
        if not habits:
            print("No habits found.")
            return
        print("\nAll habits:")
        for habit in habits:
            print(f"- {habit.title} ({habit.period}), Streak: {habit.streak}, Due: {habit.due_date}")
        print()

    def list_habits_by_period(self, period):
        habits = self.fetch_all_habits()
        filtered = [h for h in habits if h.period == period]
        if not filtered:
            print(f"No {period} habits found.")
            return
        print(f"\n{period.capitalize()} habits:")
        for habit in filtered:
            print(f"- {habit.title}, Streak: {habit.streak}, Due: {habit.due_date}")
        print()

    def longest_streak_habit(self):
        habits = self.fetch_all_habits()
        if not habits:
            print("No habits found.")
            return
        longest = max(habits, key=lambda h: h.streak)
        print(f"Longest streak habit: '{longest.title}' with streak {longest.streak}")

    def shortest_streak_habit(self):
        habits = self.fetch_all_habits()
        if not habits:
            print("No habits found.")
            return
        shortest = min(habits, key=lambda h: h.streak)
        print(f"Habit you struggled the most: '{shortest.title}' with streak {shortest.streak}")

    def close(self):
        self.conn.close()


def main_page():
    tracker = HabitTracker()

    # Ask user if they want to recreate the table (WARNING: will erase all data)
    recreate = input("Do you want to recreate the habits table? This will erase existing data (Y/N): ").strip().upper()
    if recreate == 'Y':
        tracker.recreate_table()

    use_predefined = input("USE PREDEFINED HABITS? Y/N: ").strip().upper()
    if use_predefined == 'Y':
        tracker.add_predefined_habits()

    while True:
        print("\n[1] CREATE NEW HABIT")
        print("[2] COMPLETE TASKS")
        print("[3] MANAGE (EDIT/DELETE) HABITS")
        print("[4] ANALYSE HABITS")
        print("[Q] QUIT")
        choice = input("YOUR CHOICE: ").strip().lower()

        tracker.reset_overdue_habits()

        if choice == '1':
            tracker.create_new_habit()
            time.sleep(1)
        elif choice == '2':
            tracker.complete_task()
            time.sleep(1)
        elif choice == '3':
            while True:
                print("\n[1] DELETE HABIT")
                print("[2] EDIT HABIT TITLE")
                print("[3] CHANGE TO DAILY")
                print("[4] CHANGE TO WEEKLY")
                print("[X] EXIT MANAGE")
                m_choice = input("YOUR CHOICE: ").strip().lower()
                if m_choice == '1':
                    tracker.delete_habit()
                elif m_choice == '2':
                    tracker.edit_habit_title()
                elif m_choice == '3':
                    tracker.change_habit_period('daily')
                elif m_choice == '4':
                    tracker.change_habit_period('weekly')
                elif m_choice == 'x':
                    break
                else:
                    print("Invalid option.")
                time.sleep(1)
        elif choice == '4':
            while True:
                print("\n[1] DISPLAY ALL HABITS")
                print("[2] DISPLAY DAILY HABITS")
                print("[3] DISPLAY WEEKLY HABITS")
                print("[4] LONGEST STREAK HABIT")
                print("[5] SHORTEST STREAK HABIT")
                print("[X] EXIT ANALYSE")
                a_choice = input("YOUR CHOICE: ").strip().lower()
                if a_choice == '1':
                    tracker.list_all_habits()
                elif a_choice == '2':
                    tracker.list_habits_by_period('daily')
                elif a_choice == '3':
                    tracker.list_habits_by_period('weekly')
                elif a_choice == '4':
                    tracker.longest_streak_habit()
                elif a_choice == '5':
                    tracker.shortest_streak_habit()
                elif a_choice == 'x':
                    break
                else:
                    print("Invalid option.")
                time.sleep(1)
        elif choice == 'q':
            print("See you soon!")
            tracker.close()
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main_page()
