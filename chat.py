import os

static_dir = 'static'
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

from dotenv import load_dotenv
import streamlit as st
import fitz  
import google.generativeai as genai
from IPython.display import display
from IPython.display import Markdown
import textwrap

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

load_dotenv()


google_api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=google_api_key)

model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

def get_gemini_response(question):
    response = chat.send_message(question, stream=True)
    return response


def extract_text_from_pdf(pdf_file):
    pdf_document = fitz.open(pdf_file)
    text = ""
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text += page.get_text()
    return text


st.set_page_config(page_title="Q&A Demo")
st.header("Chatbot")


uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    file_path = os.path.join(static_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    pdf_text = extract_text_from_pdf(file_path)
    st.text_area("PDF Content", pdf_text, height=300)
    
    input = st.text_input("Ask a question related to the PDF:", key="input")

    submit = st.button("Ask the question")

    if submit and input:
        
        full_question = f"Based on the following document:\n\n{pdf_text}\n\nQuestion: {input}"
        response = get_gemini_response(full_question)
        
        st.subheader("The Response is")
        for chunk in response:
            st.write(chunk.text)
            st.write("_" * 80)
        
        st.write(chat.history)
