import cohere
import streamlit as st
import os
from io import StringIO

co = cohere.Client('18V1Oo06GAf0xMaXbBjkHlhdHktqbjc5tusZHZMV')

def extract_skills_from_resume(resume_text):
    prompt = f"""
    Extract skills from the following resume text.

    Resume: {resume_text}
    Skills: """

    response = co.chat(
        model='command-r',
        message=prompt,
        preamble="")
  
    return response.text.replace("Skills: ", "").split(',')

def find_skill_gaps(profile_summary, skills_ratings):
    prompt = f"""
    Given the candidate's profile and the skills they rated, find the skills they need to improve and recommend additional skills.

    Profile: {profile_summary}
    Skills Ratings: {', '.join([f"{skill} ({rating}/10)" for skill, rating in skills_ratings.items()])}
    Suggested Improvements: """

    response = co.chat(
        model='command-r',
        message=prompt,
        preamble="")
  
    return response.text.replace("Suggested Improvements: ", "").split(',')

def recommend_courses(missing_skills):
    prompt = f"""
    Recommend online courses for the following skills.

    Skills: {', '.join(missing_skills)}
    Courses: """

    response = co.chat(
        model='command-r',
        message=prompt,
        preamble="")
  
    return response.text.replace("Courses: ", "").split(',')

def recommend_jobs(profile_summary):
    prompt = f"""
    Based on the candidate's profile, recommend job titles they should consider.

    Profile: {profile_summary}
    Recommended Jobs: """

    response = co.chat(
        model='command-r',
        message=prompt,
        preamble="")
  
    return response.text.replace("Recommended Jobs: ", "").split(',')

# Step 1: Get user's profile, skills, or resume
st.title("💼 Candidate Profile Evaluator")

# Check if profile and skills have already been provided
if 'profile_input' not in st.session_state:
    st.session_state['profile_input'] = ''
if 'skills_list' not in st.session_state:
    st.session_state['skills_list'] = []

# Allow user to upload resume
resume_upload = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])

# Function to read uploaded resume (for simplicity, let's assume it's a text file for now)
def read_resume(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            # For simplicity, assuming the user uploaded a plain text or machine-readable PDF
            # In reality, we would use a library like PyPDF2 to extract text from PDF
            return StringIO(uploaded_file.read().decode('utf-8')).read()
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # Assuming the user uploaded a docx file (use `python-docx` in real use case)
            return StringIO(uploaded_file.read().decode('utf-8')).read()
    return ""

# If resume is uploaded, extract skills
if resume_upload:
    resume_text = read_resume(resume_upload)
    if resume_text:
        # Extract skills from resume using Cohere
        st.session_state['skills_list'] = extract_skills_from_resume(resume_text)
        st.session_state['profile_input'] = "Resume-based profile"  # For now, using a generic description
        st.rerun()  # Refresh to move to the next step

# If resume is not uploaded or skills are still empty, show manual profile input form
if not st.session_state['profile_input'] and not st.session_state['skills_list']:
    form_profile = st.form(key="user_profile")
    with form_profile:
        profile_input = st.text_input("Briefly describe your profile (e.g., Software Engineer with 3 years of experience)", key="profile_input_input")
        skills_input = st.text_input("List your skills (comma-separated)", key="skills_input")
        
        submit_profile = form_profile.form_submit_button("Submit Profile and Skills")

    if submit_profile:
        if profile_input == "" or skills_input == "":
            st.error("Profile and skills fields cannot be blank")
        else:
            st.session_state['profile_input'] = profile_input
            st.session_state['skills_list'] = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            st.rerun()  # Refresh to proceed

# Step 2: Ask user to rate the skills (if skills are provided)
if st.session_state['skills_list']:
    st.subheader("Rate your skills from 1 to 10")

    form_ratings = st.form(key="user_ratings")
    skills_ratings = {}
    
    for skill in st.session_state['skills_list']:
        skills_ratings[skill] = form_ratings.slider(f"{skill}", 1, 10, 5, key=f"{skill}_rating")
    
    submit_ratings = form_ratings.form_submit_button("Evaluate Profile")

    if submit_ratings:
        my_bar = st.progress(0.05)

        # Step 3: Find skill gaps
        missing_skills = find_skill_gaps(st.session_state['profile_input'], skills_ratings)
        st.subheader("🔍 Skill Gaps and Suggested Improvements")
        if missing_skills:
            st.write("The following skills need improvement or could be learned additionally:")
            st.write(", ".join(missing_skills))
        else:
            st.write("No skill gaps found. You're doing great!")

        # Step 4: Recommend courses
        st.subheader("📚 Recommended Courses")
        courses = recommend_courses(missing_skills)
        for i, course in enumerate(courses[:5]):  # Recommending top 5 courses
            st.write(f"{i+1}. {course}")

        # Step 5: Recommend jobs
        st.subheader("💼 Recommended Jobs")
        jobs = recommend_jobs(st.session_state['profile_input'])
        for i, job in enumerate(jobs[:5]):  # Recommending top 5 jobs
            st.write(f"{i+1}. {job}")
        
        my_bar.progress(1.0)
