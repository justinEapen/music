import cohere
import streamlit as st
import PyPDF2
from docx import Document

# Initialize Cohere client
co = cohere.Client('YOUR_API_KEY')

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

# Function to match candidate's skills with job requirements and find gaps
def find_skill_gaps(candidate_skills_ratings, job_role):
    required_skills = get_required_skills_for_job(job_role)
    missing_skills = []
    gaps = {}

    for skill, rating in candidate_skills_ratings.items():
        if skill in required_skills:
            if rating < required_skills[skill]:  # If candidate's rating is less than the required level
                missing_skills.append(skill)
                gaps[skill] = (rating, required_skills[skill])

    for required_skill, level in required_skills.items():
        if required_skill not in candidate_skills_ratings:
            missing_skills.append(required_skill)
            gaps[required_skill] = (0, level)  # Candidate lacks the skill

    return missing_skills, gaps

# Function to retrieve skills required for a specific job role
def get_required_skills_for_job(job_role):
    # This would typically query a job database or use an API to get required skills for job roles.
    # For demo purposes, we're using hardcoded data.
    job_skills_data = {
        'Software Engineer': {
            'Python': 8,
            'Data Structures': 7,
            'Algorithms': 7,
            'Version Control (Git)': 6,
            'Databases': 6
        },
        'Data Scientist': {
            'Python': 8,
            'Machine Learning': 8,
            'Statistics': 7,
            'Data Visualization': 7,
            'SQL': 6
        },
        'Product Manager': {
            'Leadership': 8,
            'Communication': 7,
            'Project Management': 7,
            'Strategic Thinking': 6,
            'Problem Solving': 7
        }
    }
    return job_skills_data.get(job_role, {})

# Function to recommend personalized courses
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

# Function to recommend jobs based on profile
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

# Streamlit app
st.title("💼 Skill Gap Analysis & Job Recommendations")

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

# Step 1: Upload resume or manually input profile and skills
if resume_upload:
    resume_text = read_resume(resume_upload)
    if resume_text:
        st.session_state['skills_list'] = extract_skills_from_resume(resume_text)
        st.session_state['profile_input'] = "Resume-based profile"
        st.experimental_rerun()

if not st.session_state.get('profile_input') and not st.session_state.get('skills_list'):
    form_profile = st.form(key="user_profile")
    with form_profile:
        profile_input = st.text_input("Briefly describe your profile (e.g., Software Engineer with 3 years of experience)")
        job_role = st.selectbox("Select your desired job role", ["Software Engineer", "Data Scientist", "Product Manager"])
        skills_input = st.text_input("List your skills (comma-separated)")
        submit_profile = form_profile.form_submit_button("Submit Profile and Skills")

    if submit_profile:
        if profile_input == "" or skills_input == "":
            st.error("Profile and skills fields cannot be blank")
        else:
            st.session_state['profile_input'] = profile_input
            st.session_state['skills_list'] = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
            st.session_state['job_role'] = job_role
            st.experimental_rerun()

# Step 2: Ask user to rate the skills
if st.session_state.get('skills_list'):
    st.subheader("Rate your skills from 1 to 10")
    form_ratings = st.form(key="user_ratings")
    skills_ratings = {}

    for skill in st.session_state['skills_list']:
        skills_ratings[skill] = form_ratings.slider(f"{skill}", 1, 10, 5, key=f"{skill}_rating")

    submit_ratings = form_ratings.form_submit_button("Evaluate Profile")

    if submit_ratings:
        my_bar = st.progress(0.05)

        # Step 3: Find skill gaps
        missing_skills, skill_gaps = find_skill_gaps(skills_ratings, st.session_state['job_role'])
        st.subheader(f"🔍 Skill Gaps for {st.session_state['job_role']}")
        if skill_gaps:
            st.write("The following skills need improvement or are missing:")
            for skill, (current, required) in skill_gaps.items():
                st.write(f"{skill}: Current Level: {current}/10, Required: {required}/10")
        else:
            st.write("No skill gaps found. You're ready for this role!")

        # Step 4: Recommend courses
        if missing_skills:
            st.subheader("📚 Personalized Course Recommendations")
            courses = recommend_courses(missing_skills)
            for i, course in enumerate(courses[:5]):
                st.write(f"{i+1}. {course}")

        # Step 5: Recommend jobs
        st.subheader("💼 Recommended Jobs Based on Profile")
        jobs = recommend_jobs(st.session_state['profile_input'])
        for i, job in enumerate(jobs[:5]):
            st.write(f"{i+1}. {job}")
        
        my_bar.progress(1.0)
