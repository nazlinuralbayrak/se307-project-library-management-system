# Library Management System

**Course:** SE307 Programming with Python · Fall 2026–27
**Topic code:** SE307-13   ·   **Working as:** Group (4 members)
**Agreed extra feature(s):** Simulated e-mail notifications for overdue books

## Members

| Name | Student no. | GitHub username |
|---|---|---|
| Nazlınur Albayrak | 230201006 | @nazlinuralbayrak |
| Mehmet Ali Kanevetci | 230201041 | @MehmetAlikkk |
| Emir Sirmen Ersoy | 230201025 | @Sirmen3410 |
| Yaman Balcı | 220201081 | @yamanbalci |

## What the project does

A web-based library management system for librarians and registered members. Books, members, loans and reservations are stored in an SQLite database and handled by an object-oriented Python backend with a Flask web interface. Members can search the catalogue and borrow or return books under due-date rules; librarians manage the catalogue, see overdue loans and a statistics dashboard, and the system produces simulated e-mail warnings for overdue books.

## How to install and run

```bash
git clone https://github.com/nazlinuralbayrak/se307-project-library-management-system.git
cd se307-project-library-management-system
python -m venv .venv
# Windows: .venv\Scripts\activate     macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
flask --app app run
```

## Data

| Data / file | Source (link) or "created by us" | Licence / terms of use |
|---|---|---|
| `data/library.db` | Created by us (synthetic data) | Free to use |

> No real people's personal data, passwords or health records are stored.

## Folder structure

```
├── README.md
├── requirements.txt
├── app.py               # Flask entry point
├── src/                 # database, models, analytics, notifications
├── templates/ static/   # web pages
├── tests/               # tests
├── data/                # SQLite database and data generation script
├── notebooks/           # project.ipynb
├── reports/             # interim and final reports
└── video.md             # link to the presentation video
```

## Who did what

| Member | Main responsibilities | Main files / parts |
|---|---|---|
| @nazlinuralbayrak | Database schema, models (OOP), synthetic data population | `src/models.py`, `src/database.py`, `data/sample_books.csv` |
| @MehmetAlikkk | Authentication, user roles (librarian/member), session management | `src/auth.py`, `templates/login.html`, `templates/register.html` |
| @yamanbalci | Book catalogue search, loan & return logic, statistics dashboard | `src/loan_service.py`, `templates/books.html`, `templates/dashboard.html` |
| @Sirmen3410 | Overdue check logic, simulated e-mail notifications, log filtering | `src/notification_service.py`, `templates/notifications.html` |

Every member commits their own work from their own GitHub account.

## External code, libraries and AI tools

| What | Used for | Where |
|---|---|---|
| Flask | Web interface and routing | `app.py`, `templates/` |
| SQLite3 | Relational database storage | `src/database.py` |
| pandas, Matplotlib | Statistics and dashboard charts | `src/loan_service.py`, `templates/dashboard.html` |
| pytest | Unit testing core rules | `tests/` |
| AI assistant (Gemini) | Project guidance, architectural setup, Git troubleshooting, drafting | Project structure, notebook drafting |

## Reports and video

- Interim report (Week 10): `reports/interim_report.pdf`
- Final report: `reports/final_report.pdf`
- Presentation video: link added at the final
