import cohere
import streamlit as st
import PyPDF2
from docx import Document

# Initialize Cohere client
co = cohere.Client('GHyObF1CtNtzlgdHzrpdnXVq8lZRjporWOnGWo3Y')

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

# Function to extract skills from resume using Cohere
def extract_skills_from_resume(resume_text):
    prompt = f"""
    Extract skills from the following resume text.

    Resume: {resume_text}
    Skills: """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7,
    )
  
    return response.generations[0].text.replace("Skills: ", "").split(',')

# Function to extract required skills for the desired job role
def extract_required_skills(job_role):
    prompt = f"""
    Given the job title '{job_role}', list the most relevant skills required for this role.

    Job Role: {job_role}
    Skills: """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Skills: ", "").split(',')

# Function to perform skill gap analysis
def identify_skill_gaps(user_skills, required_skills):
    user_skills_set = set(user_skills)
    required_skills_set = set(required_skills)
    
    missing_skills = list(required_skills_set - user_skills_set)
    return missing_skills

# Function to recommend personalized courses based on missing skills
def recommend_personalized_courses(missing_skills):
    prompt = f"""
    Recommend online courses, workshops, or training programs for the following skills.

    Skills: {', '.join(missing_skills)}
    Courses: """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Courses: ", "").split(',')

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
        job_role = st.text_input("Desired job role (e.g., Data Scientist, Software Developer)", key="job_role")

        submit_profile = form_profile.form_submit_button("Submit Profile and Skills")

    if submit_profile:
        if profile_input == "" or skills_input == "" or job_role == "":
            st.error("Profile, skills, and desired job role fields cannot be blank")
        else:
            st.session_state['profile_input'] = profile_input
            st.session_state['skills_list'] = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            st.session_state['desired_job_role'] = job_role
            st.rerun()

# Step 2: Show skill gap analysis and personalized recommendations
if st.session_state.get('skills_list') and st.session_state.get('desired_job_role'):
    st.subheader(f"Skill Gap Analysis for {st.session_state['desired_job_role']}")

    # Step 3: Get required skills for the desired job role
    required_skills = extract_required_skills(st.session_state['desired_job_role'])
    st.write(f"Required skills for {st.session_state['desired_job_role']}: {', '.join(required_skills)}")

    # Step 4: Perform skill gap analysis
    missing_skills = identify_skill_gaps(st.session_state['skills_list'], required_skills)
    st.subheader("🔍 Skill Gaps")
    if missing_skills:
        st.write(f"You are missing the following skills: {', '.join(missing_skills)}")

        # Step 5: Recommend personalized courses
        st.subheader("📚 Personalized Course Recommendations")
        courses = recommend_personalized_courses(missing_skills)
        for i, course in enumerate(courses[:5]):
            st.write(f"{i+1}. {course}")
    else:
        st.write("You have all the required skills for this role!")

