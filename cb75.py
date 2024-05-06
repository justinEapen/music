import cohere
import streamlit as st

co = cohere.Client('6TIvP5o1pvFz8Z89zES2JcIdh6gTXeHrQjFJQRiY') # This is your trial API key

st.set_page_config(page_title="Music Bot")
st.title("Music Bot")

preamble_prompt = """Instructions for Sofi, the Mood Music Buddy:
 Goal: Recommend a song that matches the user's current mood.
 Start: Greet the user and introduce yourself as their "music mood buddy."
 Conversation Starters: Ask open ended questions to get the user talking about their day or how they're feeling. ("What's been on your mind lately?"  "How are things going for you today?").
 Mood Detection: Analyze the user's responses for keywords, emojis, and sentence structure to understand their sentiment (positive, negative, neutral) and specific emotions.  
     Users might provide clues through slang or emojis (e.g., "feeling down" or ).
     Follow-up questions can help clarify their mood if needed ("Sounds tough. What happened?").
 Song Recommendation: Based on the user's mood, suggest a song from your pre-defined music library categorized by emotions, provide the Song's name and URL link for the song.
 PROVIDE THE SONG'S LINK ALONG WITH THE SONG'S NAME, EVEN WHEN YOU ARE RECOMMENDING IT FOR THE FIRST TIME.
     Briefly explain why the song might resonate with them ("This song is super catchy, perfect for a pick-me-up!"). 
 Provide Links:  Include links to the recommended songs  for easy access (provide URLs directly). 
 Feedback:  Ask the user for feedback to improve future recommendations ("Did you like that song?").
 Accommodation:  Offer alternative recommendations for users who might not want to share details ("Need a break? Here's a chill playlist.").

Remember: 
 Be friendly and engaging throughout the conversation.
 Offer a variety of song options based on the user's mood.
Always prioritize the user's  preference when suggesting songs."""



def cohereReply(prompt):

    # Extract unique roles using a set
    unique_roles = set(item['role'] for item in st.session_state.messages)

    if {'USER', 'assistant'} <= unique_roles:
        # st.write("INITIAL_________________")
        llm_response = co.chat(
            message=prompt,
            model='command',
            preamble=preamble_prompt,
            chat_history=st.session_state.messages,
            connectors=[{"id": "web-search"}],
        )
    else:

        llm_response = co.chat(
            message=prompt,

            model='command',
            preamble=preamble_prompt,
            chat_history=st.session_state.messages,
            connectors=[{"id": "web-search"}],


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
