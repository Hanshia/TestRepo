import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import fitz  # PDF 읽기용 (PyMuPDF)
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.output_parsers import StrOutputParser

st.session_state.language = '한국어'

# Streamlit 설정
st.set_page_config(page_title="캐릭터 챗봇", page_icon=":house_with_garden:")

# 환경 변수 설정
os.environ["GOOGLE_API_KEY"] = st.secrets["MY_GOOGLE_API_KEY"]

# Google Generative AI 설정
client = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.environ.get("GOOGLE_API_KEY"))

# 캐릭터 정보
characters = {
    "keroro": ["케로로", "https://i.namu.wiki/i/c1GTTKMxSQJhdu1ro8bu9KxQqe6csuMTxAA_V-TkxKS2D6CPzXFHXG8pG9PnAYeLFPOT-1vFSVDWmcEuT2fYTw.webp"],
    "friren": ["프리렌", "https://i.namu.wiki/i/cgrB_jrULuNEpf8XoA4VxMLhz9gS1Q7-OnOsP6ITfl-ANLBb4Pby48kgYPzen5e1kPkx3EzeFsIbBFUtXc_KI8bkzppjryI4FXJbZOBvDcEW_sgzgTAo0uyfwK-Gu6sVC27RWQqAP0h_oMsCe3YjGg.webp"]
}

# 사용자 및 봇 아바타
user_avatar_url = "https://via.placeholder.com/50?text=User"
assistant_avatar_url = "https://via.placeholder.com/50?text=Bot"

# 대화 기록 관리
if "chat_history" not in st.session_state:
    st.session_state.chat_history = ChatMessageHistory()

# PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        text = f"[PDF 읽기 오류: {str(e)}]"
    return text.strip()

# 캐릭터 설정 로드
def load_character_files(character):
    dialog_file = f"content/text/{character}/dialog.txt"
    output_file = f"content/text/{character}/output.txt"
    pdf_file = f"content/text/{character}/pd.pdf"

    dialog_text = output_text = pdf_text = ""

    if os.path.exists(dialog_file):
        with open(dialog_file, "r", encoding="utf-8") as file:
            dialog_text = file.read()

    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            output_text = file.read()

    if os.path.exists(pdf_file):
        pdf_text = extract_text_from_pdf(pdf_file)

    return dialog_text, output_text, pdf_text

# CSS 스타일 정의
def chat_styles():
    st.markdown("""
    <style>
    body, .stApp {
        background-color: white;
    }
    .stApp {
        color: black;
    }
    .title {
        color: black;
    }
    .title img {
        width: 100%;
        max-width: 300px;
        display: block;
        margin: 0 auto 20px auto;
    }
    .chat-bubble {
        padding: 10px;
        margin: 5px;
        border-radius: 10px;
        display: inline-block; /* 텍스트 길이에 맞춰 말풍선 길이 조정 */
        max-width: 70%;
        word-wrap: break-word;
        display: flex;
        align-items: flex-start;
    }
    .chat-avatar {
        width: 50px;
        height: 50px;
        border-radius: 50%;
        margin-right: 10px;
        object-fit: cover;
    }
    .user-bubble {
        background-color: #e0e0e0;
        color: black;
        border-top-right-radius: 0;
        margin-left: auto;
        flex-direction: row-reverse;
        gap: 10px;
    }
    .assistant-bubble {
        background-color: #d1a3ff;
        color: black;
        border-top-left-radius: 0;
        margin-right: auto;
        gap: 10px;
    }
    .user-message {
        align-self: flex-end;
    }
    .assistant-message {
        align-self: flex-start;
    }
    .spinner-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin: 10px 0;
    }
    .member-selection {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .member-card {
        background-color: #f1f1f1;
        border: none;
        padding: 10px;
        margin: 5px;
        border-radius: 10px;
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
        width: 200px;
        text-align: center;
    }
    .member-card img {
        border-radius: 50%;
        width: 100px;
        height: 100px;
        object-fit: cover;
        margin-bottom: 10px;
    }
    .member-card span {
        margin-bottom: 10px;
    }
    .member-button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px;
        text-align: center;
        text-decoration: none;
        display: inline-block;
        font-size: 14px;
        cursor: pointer;
        border-radius: 5px;
        width: 100%;
        box-sizing: border-box;
    }
    .member-card button {
        background-color: transparent;
        border: none;
        padding: 0;
        text-align: center;
        cursor: pointer;
    }
    </style>
    """, unsafe_allow_html=True)

# 말풍선 스타일의 메시지 표시 함수
def display_chat_message(role, content, avatar_url):
    bubble_class = "user-bubble" if role == "user" else "assistant-bubble"
    message_class = "user-message" if role == "user" else "assistant-message"
    st.markdown(f"""
    <div class="chat-bubble {bubble_class} {message_class}">
        <img src="{avatar_url}" class="chat-avatar">
        <div>{content}</div>
    </div>
    """, unsafe_allow_html=True)

# LangChain 프롬프트 템플릿 설정
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", """너는 {character}의 역할을 수행해야 해. {character}의 스타일과 말투를 유지해야 해.
    아래는 {character}의 대화 패턴 및 설정 문서에서 가져온 정보야.

    🔹 **대화 예시**  
    {dialog_text}

    🔹 **대화 패턴 분석 결과**  
    {output_text}

    🔹 **공식 설정 문서 정보**  
    {pdf_text}

    위 정보를 기반으로 {character}답게 대화를 해줘.
    """),
    MessagesPlaceholder(variable_name="history"),
    ("user", "{input}")
])

# Runnable 설정
chat_chain = (
    chat_prompt
    | client
    | StrOutputParser()
)

# 메시지 히스토리를 포함하는 실행 객체 생성
chat_with_memory = RunnableWithMessageHistory(
    chat_chain,
    lambda session_id: st.session_state.chat_history,
    input_messages_key="input",
    history_messages_key="history"
)

# 챗봇 응답 생성 함수
def get_response(character, user_input):
    dialog_text, output_text, pdf_text = load_character_files(character)
    response = chat_with_memory.invoke(
        {
            "character": character, 
            "input": user_input,
            "dialog_text": dialog_text,
            "output_text": output_text,
            "pdf_text": pdf_text
        },
        config={"configurable": {"session_id": "current"}}
    )
    return response

# Streamlit UI 시작
st.title("캐릭터 챗봇")

# CSS 스타일 적용
chat_styles()

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.character = None
    st.session_state.language = "한국어"
    st.session_state.character_avatar_url = assistant_avatar_url
    st.session_state.stage = 1

# 대화 히스토리 표시
chat_container = st.empty()
with chat_container.container():
    st.markdown('<div class="chat-wrapper"><div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        display_chat_message(msg["role"], msg["content"], st.session_state.character_avatar_url if msg["role"] == "assistant" else user_avatar_url)
    st.markdown('</div></div>', unsafe_allow_html=True)

# 캐릭터 선택
if st.session_state.stage == 1:
    selected_character = None
    st.markdown('<div class="member-selection">', unsafe_allow_html=True)
    st.markdown("<h3>캐릭터를 선택하세요:</h3>", unsafe_allow_html=True)
    for character, info in characters.items():
        character_key = f"button_{character}"
        if st.button(f"{info[0]} 선택", key=f"{character_key}_button"):
            selected_character = character
            break
        st.markdown(f"""
        <div class="member-card" id="{character_key}">
            <img src="{info[1]}" class="chat-avatar">
            <span>{info[0]}</span>
        </div>
        """, unsafe_allow_html=True)

    if selected_character:
        st.session_state.character = selected_character
        st.session_state.character_avatar_url = characters[selected_character][1]

        # 캐릭터 첫 인사 생성
        first_message = get_response(selected_character, "캐릭터의 말투와 행동을 재현한 짧은 인삿말을 생성하세요.")
        st.session_state.messages.append({"role": "assistant", "content": first_message})

        st.session_state.stage = 2
        st.rerun()

# 대화 진행
elif st.session_state.stage == 2:
    user_input = st.chat_input("대화를 입력하세요:")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        display_chat_message("user", user_input, user_avatar_url)
    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        with st.spinner('답변 생성 중... 잠시만 기다려 주세요.'):
            response = get_response(st.session_state.character, user_input)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()

chat_container.empty()  # 이전 메시지 지우기
with chat_container.container():
    st.markdown('<div class="chat-wrapper"><div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        display_chat_message(msg["role"], msg["content"], st.session_state.character_avatar_url if msg["role"] == "assistant" else user_avatar_url)
    st.markdown('</div></div>', unsafe_allow_html=True)
