# QShift

QShift is a desktop-oriented staff scheduling system developed as a group project in the **Introduction to Software Engineering** course at **ITA**.

The system assists managers by automatically generating employee schedules according to each employee's time constraints and availability.

## Team

- Ângelo de Carvalho Nunes
- Arthur Rocha e Silva
- Artur Dantas Ferreira da Silva
- Gabriel Padilha Leonardo Ferreira
- Guilherme Eiji Moriya

## Main Features

- Employee registration and management
- Availability management per employee
- Shift and week configuration
- Automatic schedule generation and preview
- Approval and persistence of generated schedules
- Historical schedule and reporting views
- Export of schedules to spreadsheet format

## Tech Stack

### Backend

- Python + FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- OR-Tools (schedule optimization)

### Frontend

- React + Vite
- Axios
- TailwindCSS
- Chart.js

## Gabriel's Contributions

Key contributions highlights:

- Implemented core schedule backend API and schemas
- Delivered the scheduling engine and optimization logic
- Added preview flow for generated schedules
- Expanded quality coverage with tests around schedule generation edge cases
- Added employee analytics/reporting feature
