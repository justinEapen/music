import cohere
import streamlit as st

co = cohere.Client('18V1Oo06GAf0xMaXbBjkHlhdHktqbjc5tusZHZMV') # This is your trial API key

st.set_page_config(page_title="Kirti - Your Personal Mental Health Assistant")
st.title("Mental Health Bot")

preamble_prompt = """You are an AI Mental Health Therapist named "Kirti". You are a mental health therapist chatbot designed to provide empathetic and supportive responses to individuals seeking help with their emotional well-being. Your goal is to create a safe and non-judgmental space for users to express their feelings, thoughts, and concerns. Actively listen, offer thoughtful insights, and provide guidance that encourages self-reflection and positive coping strategies. Keep in mind the importance of maintaining user privacy and confidentiality. If the user expresses thoughts of self-harm or harm to others, prioritize safety by encouraging them to seek professional help or contacting emergency services. Remember to approach each interaction with empathy and respect, fostering a therapeutic environment through your responses. 
Gather all the necessary information such as name, gender, age category, and any extras they may want to add.
Ask these questions one after another. DO NOT ASK EVERYTHING AT ONCE. Get the information one at a time.
After knowing their problem, Ask if they wish to consult a therapist and then generate a random Therapist's name and contact details and provide it to them according to their location and type. Don't say that it is a random therapist, encourage them to seek the therapist's help.
If you don't know the answer to any query, just say you don't know. DO NOT try to make up an answer.
If the question is not related to the context, politely respond that you are tuned to only answer questions that are related to the context."""


docs = [
    {
        "name" : "Mental Health"
    }
]


def cohereReply(prompt):

    # Extract unique roles using a set
    unique_roles = set(item['role'] for item in st.session_state.messages)

    if {'USER', 'assistant'} <= unique_roles:
        # st.write("INITIAL_________________")
        llm_response = co.chat(
            message=prompt,
            documents=docs,
            model='command',
            preamble=preamble_prompt,
            chat_history=st.session_state.messages,
        )
    else:

        llm_response = co.chat(
            message=prompt,
            documents=docs,
            model='command',
            preamble=preamble_prompt,
            chat_history=st.session_state.messages,

        )

    print(llm_response)
    return llm_response.text


def initiailize_state():
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []


def main():

    initiailize_state()
    # Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["message"])

    # React to user input
    if prompt := st.chat_input("What is up?"):
        # Display user message in chat message container
        st.chat_message("USER").markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "USER", "message": prompt})
        # print(st.session_state.messages)

        llm_reponse = cohereReply(prompt)
        with st.chat_message("assistant"):
            st.markdown(llm_reponse)
        st.session_state.messages.append(
            {"role": "assistant", "message": llm_reponse})




if __name__ == "__main__":
    main()
