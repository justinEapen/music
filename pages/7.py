import cohere
import streamlit as st
import PyPDF2
from docx import Document
import matplotlib.pyplot as plt
import pandas as pd
import io

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

# Function to extract skills from resume
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

# Functions for finding skill gaps, recommending courses, and jobs
def find_skill_gaps(profile_summary, skills_ratings):
    prompt = f"""
    Given the candidate's profile and the skills they rated, find the skills they need to improve and recommend additional skills.

    Profile: {profile_summary}
    Skills Ratings: {', '.join([f"{skill} ({rating}/10)" for skill, rating in skills_ratings.items()])}
    Suggested Improvements: """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Suggested Improvements: ", "").split(',')

def recommend_courses(missing_skills):
    prompt = f"""
    Recommend online courses for the following skills.

    Skills: {', '.join(missing_skills)}
    Courses: """

    response = co.generate(
        model='command-xlarge-nightly',
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
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=100,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Recommended Jobs: ", "").split(',')

# Function to compare skills with job role
def compare_skills_with_job_role(user_skills, job_role):
    prompt = f"""
    Based on the job role '{job_role}', list the key skills required for the role.
    
    Job Role: {job_role}
    Required Skills: """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7
    )
  
    required_skills = response.generations[0].text.replace("Required Skills: ", "").split(',')
    
    missing_skills = [skill.strip() for skill in required_skills if skill.strip() not in user_skills]
    return missing_skills, required_skills

# Function to recommend adaptive learning pathways
def recommend_adaptive_learning_pathway(missing_skills, user_feedback):
    prompt = f"""
    Based on the following skills that the user needs to improve, and their feedback on previous courses, recommend a personalized learning pathway including a mix of micro-courses, webinars, and hands-on projects.

    Missing Skills: {', '.join(missing_skills)}
    User Feedback: {user_feedback}
    Recommended Learning Pathway: """

    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=200,
        temperature=0.7
    )
  
    return response.generations[0].text.replace("Recommended Learning Pathway: ", "").split('\n')

# Function to collect feedback on completed courses
def collect_course_feedback():
    st.subheader("📊 Course Feedback")
    feedback_form = st.form(key="course_feedback_form")
    
    with feedback_form:
        feedback_input = st.text_area("Provide your feedback on the recommended courses (e.g., Did it help you? Was it too advanced or too basic?)", key="feedback_input")
        submit_feedback = feedback_form.form_submit_button("Submit Feedback")
    
    if submit_feedback:
        if feedback_input == "":
            st.error("Feedback cannot be blank")
        else:
            st.session_state['course_feedback'] = feedback_input
            st.success("Thank you for your feedback!")
            st.rerun()

# Create a function to plot skill ratings
def plot_skill_ratings(skills_ratings):
    df = pd.DataFrame(list(skills_ratings.items()), columns=['Skill', 'Rating'])
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(kind='bar', x='Skill', y='Rating', ax=ax, color='skyblue', legend=False)
    plt.xlabel('Skill')
    plt.ylabel('Rating')
    plt.title('Skill Ratings')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    
    return buf

# Custom CSS for enhanced styling
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
        }
        .title {
            color: #007bff;
            font-size: 36px;
        }
        .section-title {
            color: #0056b3;
            font-size: 24px;
            margin-top: 20px;
        }
        .subheader {
            color: #003d79;
            font-size: 20px;
            margin-top: 20px;
        }
        .stButton>button {
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
        }
        .stButton>button:hover {
            background-color: #0056b3;
        }
        .footer {
            text-align: center;
            color: #6c757d;
            padding: 20px;
            font-size: 14px;
        }
    </style>
""", unsafe_allow_html=True)

# Main Page Layout
st.title("💼 Candidate Profile Evaluator", anchor="title")

# Add a logo or image
st.image('https://via.placeholder.com/800x150.png?text=Candidate+Profile+Evaluator', use_column_width=True)

# Resume Upload
st.subheader("Upload Your Resume", anchor="section-title")
resume_upload = st.file_uploader("Upload your resume (PDF or DOCX)", type=['pdf', 'docx'])

def read_resume(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            return extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return extract_text_from_docx(uploaded_file)
    return ""

if resume_upload:
    resume_text = read_resume(resume_upload)
    if resume_text:
        if 'skills_list' not in st.session_state:
            st.session_state['skills_list'] = extract_skills_from_resume(resume_text)
            st.session_state['profile_input'] = "Resume-based profile"
            st.rerun()

# Manual Profile Input
if not st.session_state.get('profile_input') and not st.session_state.get('skills_list'):
    st.subheader("Manual Profile Input", anchor="section-title")
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
            st.rerun()

# Skill Rating
if st.session_state.get('skills_list'):
    st.subheader("Rate Your Skills", anchor="section-title")

    form_ratings = st.form(key="user_ratings")
    skills_ratings = {}
    
    for skill in st.session_state['skills_list']:
        skills_ratings[skill] = form_ratings.slider(f"{skill}", 1, 10, 5, key=f"{skill}_rating")
    
    submit_ratings = form_ratings.form_submit_button("Evaluate Profile")

    if submit_ratings:
        my_bar = st.progress(0.05)

        # Display skill ratings
        st.subheader("📊 Skill Ratings", anchor="section-title")
        buf = plot_skill_ratings(skills_ratings)
        st.image(buf, use_column_width=True)
        
        # Find skill gaps
        missing_skills = find_skill_gaps(st.session_state['profile_input'], skills_ratings)
        st.subheader("🔍 Skill Gaps and Suggested Improvements", anchor="section-title")
        
        if missing_skills:
            st.write("The following skills need improvement or could be learned additionally:")
            st.write(", ".join([skill.strip() for skill in missing_skills if skill.strip()]))
        else:
            st.write("No significant skill gaps identified.")

        # Recommend courses
        if missing_skills:
            recommended_courses = recommend_courses(missing_skills)
            st.subheader("📚 Recommended Courses", anchor="section-title")
            if recommended_courses:
                st.write("Here are some courses to help you improve your skills:")
                for course in recommended_courses:
                    st.write(f"- {course.strip()}")
            else:
                st.write("No course recommendations found.")

        # Recommend jobs
        recommended_jobs = recommend_jobs(st.session_state['profile_input'])
        st.subheader("💼 Recommended Job Titles", anchor="section-title")
        if recommended_jobs:
            st.write("Based on your profile, consider these job titles:")
            for job in recommended_jobs:
                st.write(f"- {job.strip()}")
        else:
            st.write("No job recommendations found.")

        # Collect course feedback
        collect_course_feedback()

# Compare skills with job role
st.subheader("🔎 Compare Skills with Job Role", anchor="section-title")
job_role = st.text_input("Enter a job role to compare with your skills (e.g., Data Scientist)", key="job_role")

if job_role:
    if 'skills_list' in st.session_state:
        missing_skills, required_skills = compare_skills_with_job_role(st.session_state['skills_list'], job_role)
        st.write(f"**Required Skills for {job_role}:**")
        st.write(", ".join(required_skills))
        
        st.write(f"**Missing Skills for {job_role}:**")
        st.write(", ".join(missing_skills))
        
        # Provide adaptive learning pathways
        if missing_skills:
            user_feedback = st.session_state.get('course_feedback', '')
            learning_pathway = recommend_adaptive_learning_pathway(missing_skills, user_feedback)
            st.subheader("🛤️ Adaptive Learning Pathways", anchor="section-title")
            st.write("Here is a personalized learning pathway for you:")
            for pathway in learning_pathway:
                st.write(f"- {pathway.strip()}")
        else:
            st.write("You have the required skills for this job role.")

# Add a footer
st.markdown("""
    <footer class="footer">
        <p>Created with ❤️ by Andrea</p>
    </footer>
""", unsafe_allow_html=True)
