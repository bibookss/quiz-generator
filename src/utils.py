from typing import List, Optional

from pypdf import PdfReader
from langchain.chat_models import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
from youtube_transcript_api import YouTubeTranscriptApi


def extract_text_from_pdf(pdf_file):
    text = ""
    pdf_reader = PdfReader(pdf_file)
    num_pages = len(pdf_reader.pages)
    for i in range(num_pages):
        text += pdf_reader.pages[i].extract_text()
    return text


def extract_text_from_youtube_transcript(youtube_link):
    video_id = youtube_link.split("=")[-1]
    transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

    transcript = transcript_list.find_transcript(["en-US", "en"])
    text = " ".join([item["text"] for item in transcript.fetch()])
    return text


def generate_quiz(source_text, num_questions, question_type, openai_api_key):
    class QuestionSchema(BaseModel):
        question: str
        options: Optional[List[str]]
        correct_answer: str

    class QuizCreateSchema(BaseModel):
        questions: List[QuestionSchema]

    query = f"""
      Generate a {num_questions}-question quiz. The quiz should contain {question_type} \
      questions with 4 options each if applicable. The quiz should be based on the content below.\n{source_text}
    """

    parser = PydanticOutputParser(pydantic_object=QuizCreateSchema)

    prompt = PromptTemplate(
        template="Answer the user query.\n{format_instructions}\n{query}\n",
        input_variables=["query"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.1, verbose=True, openai_api_key=openai_api_key)

    chain = prompt | llm | parser

    return chain.invoke(query).questions
