
# Innomatics Resume Analyser

An automated system to evaluate candidate resumes against a job description using a combination of keyword matching and semantic analysis. This application is built with Streamlit and uses the Google Gemini API for personalized feedback generation.

## Features

-   **Resume & JD Parsing:** Extracts text from PDF and DOCX files.
-   **Dual Scoring Model:**
    -   **Hard Score:** Measures direct keyword matches.
    -   **Semantic Score:** Analyzes contextual relevance using fuzzy string matching.
-   **Final Verdict:** Provides a "High Fit," "Medium Fit," or "Low Fit" verdict based on a weighted final score.
-   **Personalized Feedback:** Utilizes the Gemini AI to generate detailed, actionable feedback for each candidate.
-   **Data Persistence:** Stores all evaluation results in a local SQLite database.

## Technologies Used

-   Python
-   Streamlit
-   Google Generative AI (Gemini API)
-   `pdfplumber`
-   `docx2txt`
-   `rapidfuzz`
-   `SQLAlchemy`
-   SQLite

## Getting Started

Follow these steps to set up and run the application locally.

### Prerequisites

-   Python 3.8+
-   A Google Gemini API key. You can get one from the [Google AI Studio](https://aistudio.google.com/app/apikey).
 
### Installation

1.  Clone the repository:
    ```bash
    git clone [https://github.com/your-username/resume-analyzer-app.git](https://github.com/your-username/resume-analyzer-app.git)
    cd resume-analyzer-app
    ```

2.  Create a virtual environment (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
    ```

3.  Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

### Configuration

Set your Gemini API key as an environment variable. Alternatively, you can directly replace the placeholder API keys in the Python script (`app.py`).

On macOS/Linux:
```bash
export GOOGLE_API_KEY="YOUR_API_KEY"
On Windows:

Bash

set GOOGLE_API_KEY="YOUR_API_KEY"
Running the Application
Ensure your virtual environment is active.

Run the Streamlit application from your terminal:

Bash

streamlit run app.py
The application will open in your default web browser at https://resume-checker-automated.streamlit.app/.

Usage
Create an Account: On the login page, click the "Create Account" button. Fill in your desired username, email, and password to register.

Login: Use the credentials you just created to log in.

Upload Files: Navigate to the "Resume Checker" page from the sidebar. Upload a single job description file and one or more resume files.

Analyze: Click the "Check" button to start the analysis. The results will be saved to a local database (results.db).

View Results: After the evaluation is complete, click "View Results" to navigate to the Dashboard and see the scores, verdicts, and detailed feedback for each candidate.

Dashboard: On the "Dashboard" page, you can see all evaluation results. Use the "Sort by Final Score" button to organize the results. You can also use "Clear Dashboard" to temporarily hide the results or "🔴 Clear All Results Permanently" to delete all saved data from the database.

