import cohere
import streamlit as st
import PyPDF2
from docx import Document

# Initialize Cohere client with a valid API key
co = cohere.Client('GHyObF1CtNtzlgdHzrpdnXVq8lZRjporWOnGWo3Y')  # Replace 'your-api-key' with your actual API key

# Function to extract text from PDF
def extract_text_from_pdf(file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading PDF file: {e}")
    return text

# Function to extract text from DOCX
def extract_text_from_docx(file):
    text = ""
    try:
        doc = Document(file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        st.error(f"Error reading DOCX file: {e}")
    return text

# Function to extract skills from resume using the correct API method
def extract_skills_from_resume(resume_text):
    prompt = f"""
    Extract skills from the following resume text.

    Resume: {resume_text}
    Skills: """

    try:
        response = co.generate(
            model='command-xlarge',
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
        )
        return response.generations[0].text.replace("Skills: ", "").split(',')
    except cohere.errors.UnauthorizedError as e:
        st.error("Invalid API token. Please check your Cohere API key.")
        return []
    except Exception as e:
        st.error(f"Error extracting skills: {e}")
        return []

# Function to extract required skills for a job role
def extract_required_skills(job_role):
    prompt = f"""
    List the skills required for the job role of {job_role}.
    Skills:
    """
    try:
        # Generate the required skills using Cohere
        response = co.generate(
            model='command-xlarge',  # Using a general-purpose model
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )
        return response.generations[0].text.strip().split(',')
    except cohere.errors.UnauthorizedError as e:
        st.error("Invalid API token. Please check your Cohere API key.")
        return []
    except Exception as e:
        st.error(f"Error fetching required skills: {e}")
        return []

# Functions to find skill gaps, recommend courses, and recommend jobs
def find_skill_gaps(profile_summary, skills_ratings, required_skills):
    prompt = f"""
    Given the candidate's profile, their rated skills, and the required skills for the job, find the skill gaps.

    Profile: {profile_summary}
    Skills Ratings: {', '.join([f"{skill} ({rating}/10)" for skill, rating in skills_ratings.items()])}
    Required Skills: {', '.join(required_skills)}
    Skill Gaps: """

    response = co.generate(
        model='command-xlarge',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Skill Gaps: ", "").split(',')

def recommend_courses(missing_skills):
    prompt = f"""
    Recommend online courses for the following skills.

    Skills: {', '.join(missing_skills)}
    Courses: """

    response = co.generate(
        model='command-xlarge',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Courses: ", "").split(',')

def recommend_jobs(profile_summary):
    prompt = f"""
    Based on the candidate's profile, recommend job titles they should consider.

    Profile: {profile_summary}
    Recommended Jobs: """

    response = co.generate(
        model='command-xlarge',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Recommended Jobs: ", "").split(',')

# Step 1: Get user's profile, skills, or resume
st.title("💼 Candidate Profile Evaluator")

# Allow user to upload resume
resume_upload = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])

# Function to read uploaded resume and extract text
def read_resume(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
    return ""

# If resume is uploaded, extract skills
if resume_upload:
    resume_text = read_resume(resume_upload)
    if resume_text:
        # Extract skills from resume using Cohere
        st.session_state['skills_list'] = extract_skills_from_resume(resume_text)
        st.session_state['profile_input'] = "Resume-based profile"
        st.rerun()

# If resume is not uploaded or skills are still empty, show manual profile input form
if not st.session_state.get('profile_input') and not st.session_state.get('skills_list'):
    form_profile = st.form(key="user_profile")
    with form_profile:
        profile_input = st.text_input("Briefly describe your profile (e.g., Software Engineer with 3 years of experience)", key="profile_input_input")
        skills_input = st.text_input("List your skills (comma-separated)", key="skills_input")
        desired_job_role = st.text_input("Desired Job Role", key="desired_job_input")
        submit_profile = form_profile.form_submit_button("Submit Profile and Skills")

    if submit_profile:
        if profile_input == "" or skills_input == "" or desired_job_role == "":
            st.error("Profile, skills, and desired job role fields cannot be blank")
        else:
            st.session_state['profile_input'] = profile_input
            st.session_state['skills_list'] = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            st.session_state['desired_job_role'] = desired_job_role
            st.rerun()

# Step 2: Ask user to rate the skills (if skills are provided)
if st.session_state.get('skills_list'):
    st.subheader("Rate your skills from 1 to 10")

    form_ratings = st.form(key="user_ratings")
    skills_ratings = {}
    
   
