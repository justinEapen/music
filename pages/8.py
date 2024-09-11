import cohere
import streamlit as st
import re

# Initialize Cohere client
co = cohere.Client('GHyObF1CtNtzlgdHzrpdnXVq8lZRjporWOnGWo3Y')

# Function to generate questions using Cohere
def generate_questions(skill):
    prompt = f"""
    Generate a set of multiple-choice questions (MCQs) for the following skill. Each question should have four options and the correct answer. Provide the questions in the following format:
    Question: [Question text]
    Options: [Option1, Option2, Option3, Option4]
    Answer: [Correct Option]
    
    Skill: {skill}
    Questions and Answers:
    """
    
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=500,
        temperature=0.7,
    )
    
    questions_text = response.generations[0].text.strip()
    return questions_text

# Function to parse questions
def parse_questions(questions_text):
    questions_list = []
    question_blocks = questions_text.split('\n\n')
    
    for block in question_blocks:
        question_match = re.search(r'Question:\s*(.*)', block)
        options_match = re.search(r'Options:\s*\[(.*)\]', block)
        answer_match = re.search(r'Answer:\s*(.*)', block)
        
        if question_match and options_match and answer_match:
            question = question_match.group(1).strip()
            options = [option.strip() for option in options_match.group(1).split(',')]
            answer = answer_match.group(1).strip()
            
            questions_list.append({
                'question': question,
                'options': options,
                'answer': answer
            })
        else:
            st.error(f"Error parsing question block: {block}")
    
    return questions_list

# Function to recommend courses based on score
def recommend_courses(skill, score):
    level = 'beginner' if score < 50 else 'intermediate' if score < 80 else 'advanced'
    prompt = f"""
    Recommend online courses for the following skill based on the user's performance level.

    Skill: {skill}
    Performance Level: {level}
    Courses: """
    
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
    )
    
    courses_text = response.generations[0].text.strip()
    return courses_text.split(',')

# Function to recommend jobs based on score
def recommend_jobs(skill, score):
    level = 'entry-level' if score < 50 else 'mid-level' if score < 80 else 'senior-level'
    prompt = f"""
    Based on the following skill and the user's performance level, recommend job titles that are suitable.

    Skill: {skill}
    Performance Level: {level}
    Recommended Jobs: """
    
    response = co.generate(
        model='command-xlarge-nightly',
        prompt=prompt,
        max_tokens=150,
        temperature=0.7,
    )
    
    jobs_text = response.generations[0].text.strip()
    return jobs_text.split(',')

# Function to display the test
def display_test(skill):
    st.subheader(f"📚 {skill} Test")
    
    # Generate questions using Cohere
    questions_text = generate_questions(skill)
    st.write(f"Generated Questions: {questions_text}")  # Debugging line
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
                st.write(f"Question: {q['question']}")  # Debugging line
                st.write(f"Selected Answer: {answers[i]}")  # Debugging line
                st.write(f"Correct Answer: {q['answer']}")  # Debugging line
                if answers[i] == q['answer']:
                    correct_answers += 1
            
            total_questions = len(questions_list)
            score = (correct_answers / total_questions) * 100
            st.write(f"You answered {correct_answers} out of {total_questions} questions correctly.")
            
            if score >= 80:
                st.success("Congratulations! You passed the test.")
                st.write(generate_certificate(f"Certified {skill} Specialist"))
                st.image("path_to_certificate_image.png")  # Replace with the actual path to a certificate image
                st.write("Share your achievement on LinkedIn:")
                linkedin_share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={st.secrets['app_url']}&title=I%20earned%20the%20Certified%20{skill}%20Specialist%20certificate!"
                st.markdown(f"[Share on LinkedIn]({linkedin_share_url})", unsafe_allow_html=True)
                
                # Recommend courses and jobs
                st.subheader("📚 Recommended Courses")
                courses = recommend_courses(skill, score)
                for i, course in enumerate(courses[:5]):
                    st.write(f"{i+1}. {course}")
                
                st.subheader("💼 Recommended Jobs")
                jobs = recommend_jobs(skill, score)
                for i, job in enumerate(jobs[:5]):
                    st.write(f"{i+1}. {job}")
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
