# Innomatics Resume Analyser

The Innomatics Resume Analyser is an automated system designed to evaluate the relevance of a candidate's resume against a specific job description. It uses a combination of keyword matching (Hard Score) and semantic analysis (Semantic Score) powered by a Gemini AI model to provide a comprehensive final score and personalized feedback.

---

### Key Features

* **Secure User Authentication**: Users can create an account, log in, and reset their password.
* **Resume Evaluation**: Upload multiple resumes and a job description to get a detailed fit analysis.
* **Dual Scoring System**:
    * **Hard Score**: Measures the direct presence of essential skills and keywords from the job description.
    * **Semantic Score**: Evaluates the contextual and thematic relevance of the resume's content.
* **AI-Generated Feedback**: The system provides intelligent, actionable feedback on each resume, highlighting missing skills and suggesting improvements.
* **Interactive Dashboard**: View, sort, and manage all evaluation results in a clear, user-friendly dashboard.
* **Permanent Data Management**: A "Clear All Results" button allows you to permanently delete all stored evaluation data from the database.

---

### Usage

1.  **Set up the Environment**:
    * Ensure you have the required Python libraries installed by running: `pip install -r requirements.txt`.
    * Set your Google Gemini API key as an environment variable or update the `API_KEYS` list in the `app.py` file.

2.  **Run the Application**:
    * Start the Streamlit application from your terminal: `streamlit run app.py`

3.  **Create an Account**:
    * On the login page, click the **"Create Account"** button.
    * Enter your desired **username**, **email**, and a **password**.
    * Click "Create Account" to register. You will be redirected back to the login page.

4.  **Login**:
    * Use the **username** and **password** you just created to log in.

5.  **Use the App**:
    * Navigate to the **"Resume Checker"** page from the sidebar.
    * Upload a single Job Description file.
    * Upload one or more Resume files.
    * Click the **"Check"** button to start the analysis.
    * After the evaluation is complete, click **"View Results"** to see the scores and feedback on the dashboard.

6.  **Dashboard**:
    * On the **"Dashboard"** page, you can see all evaluation results.
    * Use the **"Sort by Final Score"** button to organize the results.
    * The **"Clear Dashboard"** button temporarily hides the results from the screen.
    * The **"Show All Results"** button brings back the results that were temporarily hidden.
    * The **"🔴 Clear All Results Permanently"** button will delete all saved data from the database.

---

### Dependencies

* `streamlit`
* `sqlalchemy`
* `hashlib`
* `pdfplumber`
* `docx2txt`
* `rapidfuzz`
* `google-generativeai`

---

### License

This project is licensed under the MIT License.
