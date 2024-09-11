# Function to compare user's skills against required skills for a job role
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

# Updated step: Get user's desired job role
st.subheader("🎯 Desired Job Role")
job_role_input = st.text_input("Enter your desired job role (e.g., Data Scientist, Software Engineer)", key="job_role_input")

# When both profile and job role are provided, evaluate skill gaps
if st.session_state.get('skills_list') and job_role_input:
    st.subheader(f"🔍 Skill Gap Analysis for '{job_role_input}'")
    
    # Compare user's skills with job role requirements
    missing_skills, required_skills = compare_skills_with_job_role(st.session_state['skills_list'], job_role_input)
    
    # Show missing skills and required skills
    if missing_skills:
        st.write(f"The following skills are required for a '{job_role_input}' and are missing from your profile:")
        st.write(", ".join(missing_skills))
    else:
        st.write(f"You have all the key skills for the '{job_role_input}' role!")
    
    st.write(f"Required Skills for '{job_role_input}': {', '.join(required_skills)}")
    
    # Step 4: Recommend courses to close the skill gaps
    st.subheader("📚 Recommended Courses to Close Skill Gaps")
    if missing_skills:
        courses = recommend_courses(missing_skills)
        for i, course in enumerate(courses[:5]):
            st.write(f"{i+1}. {course}")
    else:
        st.write("No courses needed. You have the required skills!")

    # Step 5: Recommend job roles
    st.subheader("💼 Recommended Jobs")
    jobs = recommend_jobs(st.session_state['profile_input'])
    for i, job in enumerate(jobs[:5]):
        st.write(f"{i+1}. {job}")
