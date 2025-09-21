import streamlit as st
import os
import re
import warnings
import pdfplumber
import docx2txt
from rapidfuzz import fuzz, process
from datetime import datetime
import google.generativeai as genai
from sqlalchemy import create_engine, Column, Integer, String, Float, JSON, DateTime, desc
from sqlalchemy.orm import declarative_base, sessionmaker

# ---------------- Suppress Warnings & API Setup ----------------
warnings.filterwarnings("ignore")
os.environ['ABSL_CPP_MIN_LOG_LEVEL'] = '2'

# List of API keys to try in order
API_KEYS = [
    "AIzaSyB50KX7024Ojb4MDIL9rZVzM3e3GjIGx0s",
    "AIzaSyBovodHTCEcrYVQ3j8idS5Wxt9idzk7jxQ"
]

# ---------------- Database Setup ----------------
DATABASE_URL = "sqlite:///results.db"
engine = create_engine(DATABASE_URL, echo=False)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)

class ResumeResult(Base):
    __tablename__ = "resume_results"
    id = Column(Integer, primary_key=True, index=True)
    resume_file = Column(String, nullable=False, unique=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    hard_score = Column(Float, nullable=False)
    semantic_score = Column(Float, nullable=False)
    final_score = Column(Float, nullable=False)
    verdict = Column(String, nullable=False)
    missing_skills = Column(JSON, nullable=True)
    feedback = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ---------------- Skills Dictionary (Unchanged) ----------------
JOB_TERMS = { 
    "python","pandas","numpy","sql","r","excel","powerbi","tableau", 
    "nlp","ai","ml","machinelearning","deeplearning","automation", 
    "analysis","analytics","visualization","exploration","engineering", 
    "automotive","mechanical","manufacturing","production","databricks", 
    "cloud","azure","aws","docker","git","kubernetes", 
    "statistics","modelling","science","stakeholders","product", 
    "spark","kafka","hadoop","etl","bigdata","datavisualization" 
}

# ---------------- Utility Functions ----------------
def extract_text(file):
    if file.name.lower().endswith(".pdf"):
        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text.strip()
    elif file.name.lower().endswith(".docx"):
        return docx2txt.process(file).strip()
    return ""

def compute_hard_score(resume_keywords, jd_keywords):
    matched_count = 0
    for jd_kw in jd_keywords:
        for res_kw in resume_keywords:
            if fuzz.ratio(jd_kw, res_kw) >= 70:
                matched_count += 1
                break
    return round((matched_count / len(jd_keywords)) * 100, 2) if jd_keywords else 0

def compute_semantic_score(resume_text, jd_text):
    def get_phrases(text):
        words = text.split()
        return {f"{words[i]} {words[i+1]}" for i in range(len(words)-1)}
    resume_phrases = get_phrases(resume_text)
    jd_phrases = get_phrases(jd_text)
    if not jd_phrases:
        return 0
    matched = 0
    for jd_phrase in jd_phrases:
        best_match_tuple = process.extractOne(jd_phrase, resume_phrases)
        if best_match_tuple and best_match_tuple[1] >= 70:
            matched += 1
    return round((matched / len(jd_phrases)) * 100, 2)

def extract_candidate_info(text):
    info = {}
    emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b', text)
    info['email'] = emails[0] if emails else 'Not found'
    phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?(\(?\d{3,4}\)?[-.\s]?)?(\d{10})', text)
    phones_clean = [''.join(p).replace(' ', '').replace('-', '').replace('(', '').replace(')', '') for p in phones if ''.join(p).strip()]
    info['phone'] = phones_clean[0] if phones_clean else 'Not found'
    lines = text.strip().split('\n')
    name = 'Unknown'
    for line in lines[:5]:
        line_clean = re.sub(r'[^\w\s]', '', line).strip()
        if 2 <= len(line_clean.split()) <= 4 and not any(c.isdigit() for c in line_clean):
            name = line_clean
            break
    info['name'] = name
    return info

def get_missing_skills(resume_keywords, jd_keywords):
    resume_set = set(word.lower() for word in resume_keywords)
    missing = {kw.lower() for kw in jd_keywords if kw.lower() in JOB_TERMS and kw.lower() not in resume_set}
    return list(missing)

def generate_feedback(name, missing_skills, hard_score, semantic_score, final_score):
    if not missing_skills and final_score > 70:
        return f"{name} has a strong resume matching the job description well. Keep it up!"
    
    prompt = f"""
    Generate professional resume feedback for {name}, who applied for a technical job.
    Missing skills: {', '.join(missing_skills) if missing_skills else 'None'}.
    Hard score: {hard_score}/100, Semantic score: {semantic_score}/100, Final score: {final_score}/100.
    Suggest practical advice to improve their resume, skills, and employability.
    """
    
    for api_key in API_KEYS:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            return response.text
        except Exception as e:
            st.warning(f"An error occurred with the current API key. Trying next key...")
            continue
            
    return "Feedback could not be generated due to API issues. Please try again later."


# ----------------- Streamlit Pages -----------------
def login_page():
    st.markdown("""
        <style>
            .login-header {
                font-size: 80px; 
                color: #1F4E79;
                font-weight: bold;
                text-align: center;
                margin-bottom: 20px;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<div class='login-header'>Innomatics Resume Analyser</div>", unsafe_allow_html=True)
    
    col_main1, col_main2, col_main3 = st.columns([3, 1, 4])
    
    with col_main1:
        st.image("https://t3.ftcdn.net/jpg/16/36/90/94/360_F_1636909486_F1tC8g6rv3RrDv9qi89s9MwYYc7n2XNh.jpg", width='stretch')
    
    with col_main3:
        st.markdown("<h2 style='color: #1F4E79;'>Login</h2>", unsafe_allow_html=True)
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "password":
                st.session_state.logged_in = True
                st.session_state.page = "Home"
                st.rerun()
            else:
                st.error("Incorrect username or password")

def home_page():
    st.markdown("<h3 class='stSubtitle' style='text-align: left; font-weight: bold;'>Automated Resume Relevance Check System</h3>", unsafe_allow_html=True)
    
    st.markdown("<style> .home-buttons { margin-top: -10px; } </style>", unsafe_allow_html=True)
    
    st.markdown("<hr style='border: 1px solid #1F4E79; margin-top: -10px; margin-bottom: -10px;'>", unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1])
    with col1:
        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;'>", unsafe_allow_html=True)
        st.markdown("### Checking new resumes? 📄")
        if st.button("Resume Checker"):
            st.session_state.page = "Resume Checker"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div style='display: flex; flex-direction: column; align-items: center;'>", unsafe_allow_html=True)
        st.markdown("### Visiting results? 📊")
        if st.button("Results Dashboard"):
            st.session_state.page = "Dashboard"
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

def resume_checker_page():
    st.markdown("<h1 class='stTitle'>Innomatics Resume Checker</h1>", unsafe_allow_html=True)
    
    st.markdown("<h3 style='text-align: center;'>Upload Job Description and Resumes to evaluate candidate fit.</h3>", unsafe_allow_html=True)
    
    st.markdown("### Job Description")
    jd_file = st.file_uploader("Upload Job Description (PDF/DOCX)", type=["pdf", "docx"], key="jd_uploader")
    
    st.markdown("### Resumes")
    resume_files = st.file_uploader("Upload Resumes (PDF/DOCX)", type=["pdf", "docx"], accept_multiple_files=True, key="resumes_uploader")

    if 'evaluation_done' not in st.session_state:
        st.session_state.evaluation_done = False

    if st.button("Check"):
        if not jd_file or not resume_files:
            st.error("Please upload both a Job Description and at least one Resume.")
        else:
            jd_text = extract_text(jd_file) 
            jd_keywords = jd_text.lower().split() 
            db = SessionLocal() 

            try:
                for resume_file in resume_files:
                    existing_record = db.query(ResumeResult).filter_by(resume_file=resume_file.name).first()
                    if existing_record:
                        db.delete(existing_record)
                        db.commit()

                    resume_text = extract_text(resume_file) 
                    resume_keywords = resume_text.lower().split() 
                    hard_score = compute_hard_score(resume_keywords, jd_keywords) 
                    semantic_score = compute_semantic_score(resume_text.lower(), jd_text.lower()) 
                    final_score = round(hard_score * 0.7 + semantic_score * 0.3, 2) 

                    if final_score >= 70: 
                        verdict = "🟢 High Fit" 
                    elif final_score >= 50: 
                        verdict = "🟡 Medium Fit" 
                    elif final_score >= 30: 
                        verdict = "🟠 Low Fit" 
                    else: 
                        verdict = "🔴 Poor Fit" 

                    info = extract_candidate_info(resume_text) 
                    missing_skills = get_missing_skills(resume_keywords, jd_keywords) 
                    feedback = generate_feedback(info['name'], missing_skills, hard_score, semantic_score, final_score) 

                    record = ResumeResult( 
                        resume_file=resume_file.name, 
                        name=info['name'], 
                        email=info['email'], 
                        phone=info['phone'], 
                        hard_score=hard_score, 
                        semantic_score=semantic_score, 
                        final_score=final_score, 
                        verdict=verdict, 
                        missing_skills=missing_skills, 
                        feedback=feedback 
                    ) 
                    db.add(record) 
                
                db.commit()
                st.success("✅ Evaluation complete!")
                st.session_state.evaluation_done = True
                st.rerun()

            except Exception as e:
                db.rollback()
                st.error(f"An error occurred during evaluation: {e}")
            finally:
                db.close()

    if st.session_state.evaluation_done:
        if st.button("View Results"):
            st.session_state.page = "Dashboard"
            st.session_state.evaluation_done = False
            st.rerun()

def dashboard_page():
    st.title("Results Dashboard")
    st.markdown("Here you can see the results of all resume evaluations.")
    
    if 'sorted_by_score' not in st.session_state:
        st.session_state.sorted_by_score = False
    
    if 'display_results' not in st.session_state:
        st.session_state.display_results = True

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sort by Final Score"):
            st.session_state.sorted_by_score = not st.session_state.sorted_by_score
            st.rerun()
    
    with col2:
        if st.button("Clear Dashboard"):
            st.session_state.display_results = False
            st.rerun()
    
    if st.session_state.display_results:
        db = SessionLocal()
        if st.session_state.sorted_by_score:
            results = db.query(ResumeResult).order_by(desc(ResumeResult.final_score)).all()
        else:
            results = db.query(ResumeResult).order_by(desc(ResumeResult.created_at)).all()
        db.close()

        if results:
            for record in results:
                with st.expander(f"📌 {record.name} ({record.resume_file})"):
                    st.write(f"**Email:** {record.email}")
                    st.write(f"**Phone:** {record.phone}")
                    st.write(f"**Hard Score:** {record.hard_score}/100")
                    st.write(f"**Semantic Score:** {record.semantic_score}/100")
                    st.write(f"**Final Score:** {record.final_score}/100")
                    st.write(f"**Verdict:** {record.verdict}")
                    if record.missing_skills:
                        st.write(f"**Missing Skills:** {', '.join(record.missing_skills)}")
                    st.write(f"**Feedback:** {record.feedback}")
        else:
            st.info("No evaluation results found. Please upload and run a new evaluation on the Resume page.")
    else:
        st.info("Dashboard cleared. Data is still in the database. To view it again, go back to the Resume page or add a 'Show Results' button.")

# ----------------- Main App Logic -----------------
st.set_page_config(layout="wide")
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom right, #87CEFA, #FFFFE0);
        background-attachment: fixed;
        color: #333333;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    .stTitle {
        color: #1F4E79;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .stSubtitle {
        color: #1F4E79;
        font-size: 1.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    .stExpander {
        background-color: rgba(255, 255, 255, 0.85);
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 2px 2px 12px rgba(0,0,0,0.1);
    }
    div.stButton > button:first-child {
        background-color: #1F4E79;
        color: white;
        font-weight: bold;
        border-radius: 10px;
        padding: 8px 20px;
    }
    div.stButton > button:first-child:hover {
        background-color: #145374;
        color: #FFFFE0;
    }
    .stFileUploader {
        border: 2px dashed #1F4E79;
        border-radius: 12px;
        padding: 10px;
        background-color: rgba(255,255,255,0.7);
    }
    .login-container {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 100%;
        margin-top: 50px;
    }
    .left-side {
        text-align: center;
        margin-right: 30px;
    }
    .right-side {
        padding-left: 30px;
        border-left: 2px solid #1F4E79;
    }
    /* New CSS for the logo */
    .circular-logo {
        border-radius: 50%;
        overflow: hidden;
        border: 2px solid #1F4E79;
        width: 50px; /* Adjust size as needed */
        height: 50px;
    }
    /* New CSS for the main header with background color */
    .main-header {
        background-color: #1F4E79;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
        margin-top: -10px; /* Reduced space from the top */
    }
    </style>
    """, unsafe_allow_html=True)
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'page' not in st.session_state:
    st.session_state.page = "Login"

if not st.session_state.logged_in:
    login_page()
else:
    # A single column to hold the combined logo and header
    col_main = st.columns([1])[0]
    with col_main:
        # Use a single markdown block for inline styling and alignment
        st.markdown("""
            <div style="display: flex; align-items: center; justify-content: flex-start; gap: 10px;">
                <div class="circular-logo">
                    <img src="https://media.licdn.com/dms/image/v2/C510BAQGCyNM05beRVw/company-logo_200_200/company-logo_200_200/0/1630626033780/innomaticshyd_logo?e=2147483647&v=beta&t=yNdkasvVugaPt4oGo1CmQx45A0DSaN5KW5z2-9qwtrA" width="50" style="border-radius: 50%;">
                </div>
                <h2 style='color: #1F4E79; font-weight: bold;'>Innomatics Resume Analyser</h2>
            </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.markdown(f'<div style="text-align: center;"><img src="https://media.licdn.com/dms/image/v2/C510BAQGCyNM05beRVw/company-logo_200_200/company-logo_200_200/0/1630626033780/innomaticshyd_logo?e=2147483647&v=beta&t=yNdkasvVugaPt4oGo1CmQx45A0DSaN5KW5z2-9qwtrA" width="100"></div>', unsafe_allow_html=True)
    st.sidebar.markdown("<h2 style='text-align: center; color: #1F4E79;'>Innomatics</h2>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
    st.session_state.page = st.sidebar.radio("Go to", ["Home", "Resume Checker", "Dashboard"], index=["Home", "Resume Checker", "Dashboard"].index(st.session_state.page) if st.session_state.page in ["Home", "Resume Checker", "Dashboard"] else 0)
    st.sidebar.markdown("---")
    
    if st.session_state.page == "Home":
        home_page()
    elif st.session_state.page == "Resume Checker":
        resume_checker_page()
    elif st.session_state.page == "Dashboard":
        dashboard_page()

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.page = "Login"
        st.rerun()