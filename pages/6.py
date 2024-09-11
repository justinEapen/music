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

# Updated step: Track course progress and get user feedback
st.subheader("📈 Track Your Progress")
if 'course_feedback' not in st.session_state:
    st.write("Complete recommended courses and provide feedback to enhance your personalized learning experience.")
    st.button("Give Course Feedback", on_click=collect_course_feedback)
else:
    st.write("Thank you for your feedback!")
    user_feedback = st.session_state['course_feedback']

    # Step 7: Recommend adaptive learning pathway based on progress and feedback
    if st.session_state.get('skills_list'):
        missing_skills = [skill for skill in st.session_state['skills_list']]  # Example
        st.subheader("🎓 Adaptive Learning Pathway")

        adaptive_learning_pathway = recommend_adaptive_learning_pathway(missing_skills, user_feedback)
        
        for i, content in enumerate(adaptive_learning_pathway[:5]):
            st.write(f"{i+1}. {content}")
