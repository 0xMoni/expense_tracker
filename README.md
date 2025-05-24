# Expense Tracker

A simple, minimal, and modern expense tracker web app built with Python (Flask), HTML, and CSS.

## Features
- User signup and login
- Add, edit, and delete expenses and categories
- Add notes/descriptions to expenses
- Filter expenses by date range
- Download expenses as CSV
- Clean, responsive UI

## Setup
1. **Clone the repository:**
   ```bash
   git clone https://github.com/0xMoni/expense_tracker.git
   cd expense_tracker
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the app:**
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development  # Optional, for debug mode
   flask run
   ```
5. **Open your browser:**
   Go to [http://localhost:5000](http://localhost:5000)

## Usage
- Sign up for a new account or log in.
- Add categories and expenses.
- Edit or delete any entry.
- Filter expenses by date range.
- Download your expenses as a CSV file.

## Notes
- Data is stored in memory (not persistent). All data will be lost when the server restarts.
- For production or persistent use, consider adding a database (SQLite, PostgreSQL, etc.).

## License
MIT 