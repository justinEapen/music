import cohere
import streamlit as st
import random

# Initialize Cohere client
co = cohere.Client('GHyObF1CtNtzlgdHzrpdnXVq8lZRjporWOnGWo3Y')

# Function to generate questions using Cohere
def generate_questions(skill):
    prompt = f"Generate a set of multiple-choice questions for the following skill. Include the question, four options, and the correct answer.\n\nSkill: {skill}\nQuestions and Answers: "
    
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
    )
    
    questions_text = response.generations[0].text.strip()
    return questions_text

# Function to parse questions
def parse_questions(questions_text):
    questions_list = []
    for item in questions_text.split('\n'):
        if 'Question' in item:
            parts = item.split('|')
            if len(parts) == 3:
                question = parts[0].replace('Question:', '').strip()
                options = [option.strip() for option in parts[1].split(',')]
                answer = parts[2].replace('Answer:', '').strip()
                questions_list.append({'question': question, 'options': options, 'answer': answer})
    return questions_list

# Function to display the test
def display_test(skill):
    st.subheader(f"📚 {skill} Test")
    
    # Generate questions using Cohere
    questions_text = generate_questions(skill)
    questions_list = parse_questions(questions_text)
    
    if questions_list:
        answers = []
        for idx, q in enumerate(questions_list):
            st.write(f"{idx + 1}. {q['question']}")
            answer = st.radio(
                f"Question {idx + 1}",
                q['options'],
                key=f"question_{idx + 1}"
            )
            answers.append(answer)
        
        if st.button("Submit Test"):
            correct_answers = 0
            for i, q in enumerate(questions_list):
                if answers[i] == q['answer']:
                    correct_answers += 1
            
            total_questions = len(questions_list)
            st.write(f"You answered {correct_answers} out of {total_questions} questions correctly.")
            
            if correct_answers == total_questions:
                st.success("Congratulations! You passed the test.")
                st.write(generate_certificate(f"Certified {skill} Specialist"))
                st.image("path_to_certificate_image.png")  # Replace with the actual path to a certificate image
                st.write("Share your achievement on LinkedIn:")
                linkedin_share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={st.secrets['app_url']}&title=I%20earned%20the%20Certified%20{skill}%20Specialist%20certificate!"
                st.markdown(f"[Share on LinkedIn]({linkedin_share_url})", unsafe_allow_html=True)
            else:
                st.warning("You did not pass the test. Keep learning and try again!")
    else:
        st.error("No questions available for this skill.")

# Generate a certificate
def generate_certificate(badge_name):
    return f"Congratulations! You've earned the {badge_name} badge."

# Page to display test for selected skill
st.title("📝 Skill Test")

# Allow user to input skills
skills_input = st.text_input("Enter the skills you want to be tested on (comma-separated)", key="skills_input")

if skills_input:
    skills = [skill.strip() for skill in skills_input.split(",") if skill.strip()]
    
    if skills:
        selected_skill = st.selectbox("Select a skill to test:", skills)
        if selected_skill:
            display_test(selected_skill)
    else:
        st.error("Please enter at least one skill.")
