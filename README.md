# UniHustle 🎓💼

**UniHustle** is a Smart Student Job Agent Platform designed to help students find **part-time jobs** and internships that perfectly fit their academic schedule and financial needs.

## 🚀 Features

- **Smart Matching**: AI-driven matching algorithm that pairs students with relevant job opportunities based on their skills, preferences, and availability.
- **Automated Scraping**: Aggregates job listings from multiple sources (e.g., Reed) to provide a centralized pool of opportunities.
- **Schedule Conflict Detection**: Compares job requirements with the student's academic timetable to ensure compatibility.
- **Comprehensive Dashboard**: A user-friendly interface for students to manage their profile, view matches, and track applications.
- **Background Processing**: Utilizes Celery for efficient background tasks like web scraping and matching updates.

## 🛠️ Technology Stack

### Frontend
- **Framework**: [React](https://reactjs.org/) (Project initialized with [Vite](https://vitejs.dev/))
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: Context API / React Hooks

### Backend
- **Framework**: [Flask](https://flask.palletsprojects.com/) (Python)
- **Database**: PostgreSQL (Development uses SQLite)
- **Task Queue**: [Celery](https://docs.celeryq.dev/) with Redis
- **ORM**: SQLAlchemy

## 📦 Project Structure

```
Unihustle/
├── backend/            # Flask API, Scrapers, and Logic
│   ├── app/            # Application factory, models, routes
│   ├── migrations/     # Database migrations
│   └── ...
└── frontend/           # React Application
    ├── src/            # Components, Pages, Services
    └── ...
```

## 🔧 Getting Started

### Backend Setup

1.  Navigate to the `backend` directory:
    ```bash
    cd backend
    ```
2.  Create a virtual environment:
    ```bash
    python -m venv venv
    ```
3.  Activate the virtual environment:
    - Windows: `venv\Scripts\activate`
    - Mac/Linux: `source venv/bin/activate`
4.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
5.  Run the Flask server:
    ```bash
    flask run
    ```

### Frontend Setup

1.  Navigate to the `frontend` directory:
    ```bash
    cd frontend
    ```
2.  Install dependencies:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
