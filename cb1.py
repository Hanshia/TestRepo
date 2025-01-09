import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI

st.set_page_config(page_title="무엇이든 질문하세요~")
st.title('무엇이든 질문하세요~')

import os
os.environ["GOOGLE_API_KEY"] = "MY_GOOGLE_API_KEY"  # "sk-" 대신 본인의 API 키를 입력하세요.

def generate_response(input_text):  # llm 답변 생성
    llm = ChatGoogleGenerativeAI(model="gemini-exp-1206", temperature=0.5, convert_system_message_to_human=True)
    st.info(llm.invoke(input_text).content)

with st.form('Question'):
    text = st.text_area('질문 입력:', 'What types of text models does Google provode?')  # 첫 페이지에서의 질문
    submitted = st.form_submit_button('보내기')
    if submitted:  # 버튼이 눌렸을 때만 답변 생성
        generate_response(text)