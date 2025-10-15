# AI-Finance Full-Stack Application

This project is a full-stack financial management application designed to help users track their transactions, manage budgets, and generate reports. It provides a comprehensive solution for personal finance, built with a modern web frontend and a robust backend.

## Features

- **Transaction Management**: Record, categorize, and view all your financial transactions.
- **Budgeting**: Create and manage budgets for different categories to control spending.
- **Reporting**: Generate various financial reports (e.g., monthly, annual, custom range) to gain insights into your financial health.
- **Consistent Error Handling**: User-friendly error messages are displayed for all key operations.
- **Loading States**: Visual feedback (spinners, progress bars) is provided during data loading and form submissions for a smooth user experience.

## Technologies Used

### Frontend
- **Angular**: A platform for building mobile and desktop web applications.
- **TypeScript**: A superset of JavaScript that adds static typing.
- **Angular Material**: A UI component library for Angular applications.
- **Tailwind CSS**: A utility-first CSS framework for rapidly building custom designs.

### Backend
- **Django**: A high-level Python Web framework that encourages rapid development and clean, pragmatic design.
- **Django REST Framework**: A powerful and flexible toolkit for building Web APIs.
- **Python**: The programming language used for the backend logic.
- **SQLite**: A C-language library that implements a small, fast, self-contained, high-reliability, full-featured, SQL database engine.

## Setup Instructions

To get the application up and running on your local machine, follow these steps:

### 1. Clone the Repository

```bash
git clone <repository_url>
cd AI-finance
```

### 2. Backend Setup

Navigate to the `budget_tracker` directory:

```bash
cd budget_tracker
```

Create and activate a virtual environment (recommended):

```bash
python -m venv venv
.\venv\Scripts\activate  # On Windows
source venv/bin/activate # On macOS/Linux
```

Install backend dependencies:

```bash
pip install -r requirements.txt
```

Apply database migrations:

```bash
python manage.py migrate
```

Create a superuser (optional, for accessing Django admin):

```bash
python manage.py createsuperuser
```

### 3. Frontend Setup

Navigate to the `frontend` directory:

```bash
cd ../frontend
```

Install frontend dependencies:

```bash
npm install
```

## How to Run the Application

### 1. Start the Backend Server

In the `budget_tracker` directory, run:

```bash
python manage.py runserver
```

The backend API will be available at `http://127.0.0.1:8000/`.

### 2. Start the Frontend Development Server

In the `frontend` directory, run:

```bash
npm start
```

The frontend application will be available at `http://localhost:4200/`.

Open your browser and navigate to `http://localhost:4200/` to access the application.

Enjoy managing your finances with AI-Finance!