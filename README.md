# AI-Powered Business Intelligence Report Generator

An AI-powered Business Intelligence (BI) Report Generator that analyzes CSV datasets, generates visualizations, extracts key insights, and produces an automated business report.

The application uses a React frontend, FastAPI backend, Pandas for data analysis, Matplotlib for visualizations, and a locally running Llama 3.2 model through Ollama for generating the report narrative.

---

## Features

- Upload CSV datasets through a web interface
- Automatic dataset profiling
- Data quality analysis
- KPI extraction
- Automatic chart generation
- Trend and distribution analysis
- Correlation analysis
- AI-generated business insights
- Executive summary generation
- Business recommendations
- Markdown report generation
- Fully local AI report generation using Ollama
- No paid AI API required

---

## Tech Stack

### Frontend

- React
- Vite
- JavaScript
- CSS

### Backend

- Python
- FastAPI
- Pandas
- Matplotlib
- Pydantic

### AI

- Ollama
- Llama 3.2 3B

### Development Tools

- Git
- GitHub
- VS Code

---

## Project Architecture

```text
CSV Dataset
     │
     ▼
React Frontend
     │
     ▼
FastAPI Backend
     │
     ├── Data Profiling
     │      └── Pandas
     │
     ├── Visualization
     │      └── Matplotlib
     │
     └── AI Report Generation
            └── Ollama
                  │
                  ▼
             Llama 3.2 3B
                  │
                  ▼
          Business Intelligence
               Report
Project Structure
bi-report-generator/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py
│   │   │
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py
│   │   │
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── chart_builder.py
│   │   │   ├── data_profiler.py
│   │   │   └── report_generator.py
│   │   │
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   └── file_utils.py
│   │   │
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── main.py
│   │
│   ├── .env.example
│   ├── Dockerfile
│   ├── requirements.txt
│   └── run.py
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChartsGrid.jsx
│   │   │   ├── FileUpload.jsx
│   │   │   ├── KpiCards.jsx
│   │   │   ├── LoadingState.jsx
│   │   │   └── ReportView.jsx
│   │   │
│   │   ├── api/
│   │   │   └── client.js
│   │   │
│   │   ├── App.jsx
│   │   ├── index.css
│   │   └── main.jsx
│   │
│   ├── Dockerfile
│   ├── index.html
│   ├── package-lock.json
│   ├── package.json
│   └── vite.config.js
│
├── sample_data/
│   └── sample_sales.csv
│
├── docker-compose.yml
├── .gitignore
└── README.md
Installation
Prerequisites

Make sure the following are installed:

Python 3.11 or 3.12
Node.js
npm
Ollama
Git

Check the installations:

python --version
node --version
npm --version
ollama --version
git --version
1. Clone the Repository

Clone the GitHub repository:

git clone https://github.com/YOUR_USERNAME/bi-report-generator.git

Move into the project directory:

cd bi-report-generator

Replace YOUR_USERNAME with your GitHub username.

2. Backend Setup

Go to the backend directory:

cd backend

Create a Python virtual environment:

python -m venv venv
Windows

Activate the virtual environment:

venv\Scripts\activate

Install the required Python packages:

pip install -r requirements.txt
3. Ollama Setup

This project uses a local Llama 3.2 model through Ollama for AI-generated business reports.

No paid AI API key is required.

Install Ollama

Download and install Ollama from:

https://ollama.com/download

Check the installation:

ollama --version
Download Llama 3.2

Run:

ollama pull llama3.2:3b

Check the installed models:

ollama list

You should see:

NAME
llama3.2:3b
Test the model

Run:

ollama run llama3.2:3b

Then enter:

Explain business intelligence in one sentence.

If the model responds successfully, Ollama is ready.

Exit the model using:

/bye
4. Environment Configuration

Create a .env file inside the backend directory:

backend/
└── .env

Add the following:

OLLAMA_URL=http://localhost:11434/api/generate
OLLAMA_MODEL=llama3.2:3b

MAX_PROFILE_ROWS=200000

STORAGE_DIR=storage

FRONTEND_ORIGIN=http://localhost:5173

The .env file is intentionally excluded from Git using .gitignore.

Do not commit private API keys, passwords, or other sensitive information to GitHub.

5. Start the Backend

From the backend directory, make sure the virtual environment is activated:

venv\Scripts\activate

Start the FastAPI server:

python run.py

The backend will normally run at:

http://localhost:8000

FastAPI's interactive API documentation is available at:

http://localhost:8000/docs
6. Frontend Setup

Open a new terminal.

From the project root, go to the frontend directory:

cd frontend

Install the Node.js dependencies:

npm install

Start the development server:

npm run dev

The frontend will normally be available at:

http://localhost:5173
7. Running the Application

To run the complete application, three components are required:

Ollama
   │
   ├── Llama 3.2 3B
   │
   ▼
FastAPI Backend
   │
   ▼
React Frontend
Terminal 1 — Backend
cd backend
venv\Scripts\activate
python run.py
Terminal 2 — Frontend
cd frontend
npm run dev

Ollama should be installed and running in the background.

Then open:

http://localhost:5173
8. Using the Application
Open the application in your browser.
Upload a CSV dataset.
The backend validates and analyzes the dataset.
Pandas generates the statistical profile.
The application identifies important metrics and data quality information.
Matplotlib generates relevant visualizations.
The statistical profile is sent to the local Llama 3.2 model through Ollama.
Llama generates the business analysis.
The application creates the final BI report.
The generated report is displayed in the frontend.
Report Generation Pipeline
CSV Upload
    │
    ▼
Dataset Validation
    │
    ▼
Data Profiling
    │
    ├── Dataset dimensions
    ├── Column information
    ├── Data types
    ├── Missing values
    ├── Duplicate records
    └── Statistical summaries
    │
    ▼
Visualization
    │
    ├── Revenue distribution
    ├── Regional analysis
    ├── Trend analysis
    └── Correlation analysis
    │
    ▼
Statistical Profile
    │
    ▼
Ollama
    │
    ▼
Llama 3.2 3B
    │
    ▼
AI Business Analysis
    │
    ├── Executive Summary
    ├── KPIs
    ├── Business Insights
    ├── Data Quality Notes
    └── Recommendations
    │
    ▼
Final BI Report
Sample Dataset

A sample sales dataset is included in the repository:

sample_data/sample_sales.csv

It can be used to test the application after installation.

You can also upload other compatible CSV datasets.

Generated Reports

Generated reports and uploaded files are stored locally under:

backend/storage/

These generated files are excluded from Git using .gitignore.

This keeps temporary reports, charts, and uploaded datasets from being committed to the repository.

API

The backend uses FastAPI to provide the application's API.

The interactive API documentation can be accessed at:

http://localhost:8000/docs

The API handles operations such as:

CSV upload
Dataset analysis
Report generation
Report data delivery
Why Ollama?

The project uses Ollama with Llama 3.2 3B instead of a paid cloud-based AI API.

Advantages
No paid API credits required
No API key required for report generation
Local AI inference
Data can remain on the local machine
No external AI service dependency
Suitable for development and demonstrations
Can continue working without an internet connection after the model is installed
Data Processing

The application uses Pandas to analyze uploaded datasets.

The data profiling stage can identify:

Number of rows
Number of columns
Column data types
Missing values
Duplicate records
Numerical statistics
Categorical information
Important dataset characteristics

The resulting statistical profile is provided to the AI model so that the generated report is based on the analyzed dataset.

Visualization

The application automatically generates visualizations based on the dataset.

Examples include:

Distribution charts
Regional comparisons
Trend charts
Correlation heatmaps

The generated charts are incorporated into the final business report.

AI-Generated Report

The local Llama 3.2 model generates structured business content including:

Executive Summary

A concise overview of the major findings from the dataset.

KPIs

Important numerical metrics extracted from the analyzed data.

Business Insights

Interpretation of important patterns and trends.

Data Quality Notes

Important observations regarding missing values, duplicates, or other data quality issues.

Recommendations

Actionable recommendations based on the available dataset information.

Security and Privacy

The application is designed to run the AI component locally using Ollama.

Uploaded datasets are processed by the local backend and the statistical profile is passed to the local Llama model.

The project does not require a paid external AI API for report generation.

Sensitive configuration files such as .env are excluded from version control.

Future Improvements

Possible future improvements include:

Excel file support
PDF report export
Interactive dashboards
Additional chart types
More advanced KPI detection
Custom business prompts
Support for additional local AI models
Database integration
User authentication
Automated report scheduling
Cloud deployment
Advanced forecasting
More detailed anomaly detection
Troubleshooting
Ollama command not found

Install Ollama and restart your terminal.

Check:

ollama --version
Model not found

Download the model:

ollama pull llama3.2:3b

Then check:

ollama list
Backend does not start

Make sure the virtual environment is activated:

venv\Scripts\activate

Then reinstall dependencies:

pip install -r requirements.txt

Start the server again:

python run.py
Frontend does not start

Install the dependencies:

npm install

Then run:

npm run dev
Report generation fails

Make sure:

Ollama is installed.
llama3.2:3b is available.
The backend is running.
The .env file contains the correct Ollama configuration.
The CSV file is valid.

Check the model:

ollama list
GitHub

The project is maintained using Git and GitHub for version control.

The repository contains the source code, configuration examples, sample data, and project documentation.

Generated reports, uploaded files, virtual environments, and .env files are excluded from version control.

Author

Developed as an academic project for Business Intelligence and AI-based automated report generation.
