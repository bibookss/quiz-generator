import streamlit as st

from utils import (
    extract_text_from_pdf,
    extract_text_from_youtube_transcript,
    generate_quiz,
)

if __name__ == "__main__":
    quiz = st.session_state.get("quiz", None)
    question_index = st.session_state.get("question_index", 0)
    anwers = st.session_state.get("answers", [])

    st.set_page_config(page_title="Quiz Generator", page_icon="🧠")
    st.title("Quiz Generator")
    st.write(
        "This app generates a quiz based on the content of a Youtube video or a PDF document."
    )
    with st.sidebar:
        st.subheader("OpenAI API Key")
        openai_api_key = st.text_input("OpenAI API Key", type="password")
        if not openai_api_key:
            st.warning("Please enter your OpenAI API key!", icon="⚠")

        st.subheader("Quiz Configuration")
        question_type = st.selectbox(
            "Select a question type",
            ["Multiple choice", "True or false"],
        )
        num_questions = st.number_input("Number of questions", 1, 20, 5)

        st.subheader("Quiz Generation")
        source_text = ""
        document_type = st.selectbox(
            "Select a document type", ["Youtube transcript", "PDF"]
        )
        if document_type == "PDF":
            uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
            button_placeholder = st.sidebar.empty()
            processing = False

            if uploaded_file is not None:
                processing = button_placeholder.button("Process")

            if processing:
                button_placeholder.empty()
                progress_placeholder = st.sidebar.empty()
                with st.spinner("Processing..."):
                    source_text = extract_text_from_pdf(uploaded_file)
                    progress_placeholder.success("Processing completed!")
        elif document_type == "Youtube transcript":
            youtube_link = st.text_input("Enter a Youtube link", "")
            button_placeholder = st.sidebar.empty()
            processing = False

            # if youtube_link and not youtube_link in valid_youtube_urls:
            #     st.warning("Please enter a valid Youtube link!", icon="⚠")

            if youtube_link:
                processing = button_placeholder.button("Process")

            if processing:
                progress_placeholder = st.sidebar.empty()
                with st.spinner("Processing..."):
                    source_text = extract_text_from_youtube_transcript(youtube_link)
                    progress_placeholder.success("Processing completed!")

        if source_text and openai_api_key:
            quiz = generate_quiz(source_text, num_questions, question_type, openai_api_key)
            st.session_state.quiz = quiz

    if quiz:
        st.subheader("Quiz")
        for i, question in enumerate(quiz):
            question_text = question.question
            options = question.options

            st.write(f"**Question {i + 1}**: {question_text}")
            answer = st.radio("Options", options, index=None, key=i)
            anwers.append(answer)

        submit_button = st.button("Submit")
        if submit_button:
            st.subheader("Results")
            score = 0
            for i, question in enumerate(quiz):
                question_text = question.question
                options = question.options
                correct_answer = question.correct_answer
                answer = anwers[i]

                st.write(f"**Question {i + 1}**: {question_text}")
                st.write(f"Correct answer: {correct_answer}")
                st.write(f"Your answer: {answer}")

                if answer == correct_answer:
                    score += 1

            st.write(f"Your score: {score}/{num_questions}")

            st.session_state.quiz = None
            st.session_state.question_index = 0