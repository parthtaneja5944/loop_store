# Store Status Monitoring System

This project is designed to monitor the status of various stores over time, including uptime and downtime metrics based on business hours. The system is built using Flask, SQLAlchemy, and PostgreSQL, with data being loaded from CSV files and reports generated asynchronously.

## Project Structure

- **run.py**: Entry point to start the Flask application.
- **load_data.py**: Script to load data from CSV files into the PostgreSQL database.
- **config.py**: Configuration file containing database URI and other settings.
- **app/__init__.py**: Application factory function to create and configure the Flask application.
- **app/extensions.py**: Initializes Flask extensions like SQLAlchemy.
- **app/models.py**: Defines the database models (`StoreStatus`, `BusinessHours`, `Timezone`, `ReportStatus`).
- **app/routes.py**: Defines the Flask routes for triggering and retrieving reports.
- **app/utils.py**: Contains utility functions for calculating uptime/downtime and generating reports.

## Setup Instructions

### Prerequisites

- Python
- PostgreSQL
- SQLAlchemy
- Virtual environment tool (venv or virtualenv)

### Step 1: Clone the Repository

```bash
git clone https://github.com/parthtaneja5944/loop_store.git
cd store-status-monitoring
```
### Step 2: Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure the Database

- **Ensure PostgreSQL is installed and running.
- **Create a database named store_status_db.
- **Update the database URI in config.py if necessary.

### Step 5: Initialize the Database

```bash
flask db init
```

### Step 6: Load Data from CSV Files

```bash
python load_data.py
```

### Step 7: Run the Application

```bash
python run.py
```

## API Endpoints

### Trigger Report

- **URL**: `/trigger_report`
- **Method**: `POST`
- **Description**: Triggers the generation of a new report.
- **Response**: Returns a `report_id` that can be used to fetch the report status or download the report.

### Get Report Status or Download Report

- **URL**: `/get_report?report_id=<report_id>`
- **Method**: `GET`
- **Description**: Checks the status of the report generation. If the report is complete, it returns the CSV file.
- **Response**:
  - `status: "Running"` if the report is still being generated.
  - The CSV file if the report is complete.
  - `error: "Invalid report_id"` if the report ID is not found.

## Logic and Techniques Used

### 1. Database Models

- **StoreStatus**: Records the status of each store at different timestamps.
- **BusinessHours**: Stores the business hours of each store by day.
- **Timezone**: Maps stores to their respective timezones.
- **ReportStatus**: Tracks the status of report generation, including completion time.

### 2. Uptime and Downtime Calculation

- **Timezones**: Store statuses are converted to the store's local timezone using `pytz`.
- **Business Hours**: Business hours are used to determine whether a store should be considered "up" or "down" during specific intervals.
- **Parallel Processing**: The `multiprocessing` library is used to speed up report generation by processing multiple stores in parallel.

### 3. Asynchronous Report Generation

Reports are generated asynchronously using threads to avoid blocking the main application. The status of report generation is tracked in the `ReportStatus` model.

## Libraries Used

- **Flask**: Micro web framework for Python.
- **SQLAlchemy**: SQL toolkit and ORM for Python.
- **Pandas**: Data manipulation and analysis library.
- **pytz**: World timezone definitions for Python.
- **multiprocessing**: Support for parallel execution using multiple processes.
