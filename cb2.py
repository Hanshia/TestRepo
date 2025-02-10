import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import fitz  # PyMuPDF 라이브러리 (PDF 읽기용)

st.session_state.language = '한국어'

# Streamlit 설정
st.set_page_config(page_title="블로그 도와줘!", page_icon=":house_with_garden:")

# 환경 변수 설정
os.environ["GOOGLE_API_KEY"] = st.secrets["MY_GOOGLE_API_KEY"]

# Google Generative AI 설정
client = ChatGoogleGenerativeAI(model="gemini-1.5-flash", api_key=os.environ.get("GOOGLE_API_KEY"))

# 애니 캐릭터와 그들의 정보 및 이미지 URL
characters = {
    "keroro": ["케로로", "https://i.namu.wiki/i/c1GTTKMxSQJhdu1ro8bu9KxQqe6csuMTxAA_V-TkxKS2D6CPzXFHXG8pG9PnAYeLFPOT-1vFSVDWmcEuT2fYTw.webp"],
    "friren": ["프리렌", "https://i.namu.wiki/i/cgrB_jrULuNEpf8XoA4VxMLhz9gS1Q7-OnOsP6ITfl-ANLBb4Pby48kgYPzen5e1kPkx3EzeFsIbBFUtXc_KI8bkzppjryI4FXJbZOBvDcEW_sgzgTAo0uyfwK-Gu6sVC27RWQqAP0h_oMsCe3YjGg.webp"]
}

# 사용자 아바타 이미지 URL
user_avatar_url = "https://via.placeholder.com/50?text=User"
assistant_avatar_url = "https://via.placeholder.com/50?text=Bot"

# 특정 캐릭터의 대화 스타일을 로드하는 함수
def load_character_files(character):
    dialog_file = f"content/text/{character}/dialog.txt"
    output_file = f"content/text/{character}/output.txt"
    pdf_file = f"content/text/{character}/pd.pdf"  # 캐릭터 설정 문서 PDF

    dialog_text = ""
    output_text = ""
    pdf_text = ""

    # dialog.txt 읽기
    if os.path.exists(dialog_file):
        with open(dialog_file, "r", encoding="utf-8") as file:
            dialog_text = file.read()
    else:
        dialog_text = f"[{dialog_file} 파일을 찾을 수 없습니다.]"

    # output.txt 읽기
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            output_text = file.read()
    else:
        output_text = f"[{output_file} 파일을 찾을 수 없습니다.]"

    # PDF 파일 읽기
    if os.path.exists(pdf_file):
        pdf_text = extract_text_from_pdf(pdf_file)
    else:
        pdf_text = f"[{pdf_file} 파일을 찾을 수 없습니다.]"

    return dialog_text, output_text, pdf_text

# PDF에서 텍스트를 추출하는 함수
def extract_text_from_pdf(pdf_path):
    text = ""
    try:
        with fitz.open(pdf_path) as doc:
            for page in doc:
                text += page.get_text("text") + "\n"
    except Exception as e:
        text = f"[PDF 읽기 오류: {str(e)}]"
    return text.strip()

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

# 대화를 생성하는 함수
def generate_conversation(language, character, user_input):
    dialog_text, output_text, pdf_text = load_character_files(character)
    prompt = f"""
    아래는 {character}와 다른 인물 간의 실제 대화 내용입니다:
    {dialog_text}

    아래는 {character}의 대화 패턴 분석 결과입니다:
    {output_text}

    아래는 {character}의 공식 설정 문서에서 추출한 정보입니다:
    {pdf_text}

    1. {pdf_text}에서 추출한 캐릭터의 상세한 성격과 전형적인 행동을 바탕으로, {output_text}에서 분석한 대화 패턴을 활용하여 프리렌의 말투와 행동을 재현한 응답을 생성하세요.
    또한, {dialog_text} 파일에 있는 캐릭터와 다른 인물 간의 대화를 참고하여 보다 자연스러운 표현을 반영하세요. 만약 {pdf_text}와 {output_text}과 {dialog_text}가 비어있다면 2번 항목을 참고하세요.

    2. 다음은 애니 캐릭터에 대한 정보 링크입니다.  {pdf_text}와 {output_text}과 {dialog_text}가 비어있지 않다면 이 항목은 넘기세요.
    [keroro]: [https://namu.wiki/w/%EC%BC%80%EB%A1%9C%EB%A1%9C].
    [friren]: [https://namu.wiki/w/%ED%94%84%EB%A6%AC%EB%A0%8C].
    이 정보를 바탕으로, 질문에 답하거나 이 캐릭터로 역할을 연기하세요.

    3. 사용자가 주제를 추천하길 원한다면, 최근 구글에서 [특정 주제 분야, 예: 기술, 여행, 음식 등]와 관련된 인기 있는 주제를 검색하여 추천해 주세요.

    4. 사용자가 글의 개선하고 싶어하면 내용을 검토한 후, 명확성, 톤, 전반적인 품질을 향상시킬 수 있는 수정 사항을 제안해 주세요.

    5. 반드시 응답만 작성하세요.

    6. 사용자 입력만으로는 어떤 응답을 생성해야 할지 알 수 없다면, 캐릭터의 스타일에 따른 아무 응답이나 하세요.


    사용자 입력: {user_input}
    """
    response = client.invoke(prompt)
    return response.content

# Streamlit 애플리케이션 시작
st.title("블로그 도와줘!")

# CSS 스타일 적용
chat_styles()

# 세션 상태 초기화
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

# 캐릭터 선택 단계
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
        dialog_text, output_text, pdf_text = load_character_files(character)
        # 첫 인사를 캐릭터 스타일에 맞게 생성
        first_message = generate_conversation(
            st.session_state.language, 
            selected_character, 
            f"""
            아래는 {character}와 다른 인물 간의 실제 대화 내용입니다:
            {dialog_text}

            아래는 {character}의 대화 패턴 분석 결과입니다:
            {output_text}

            아래는 {character}의 공식 설정 문서에서 추출한 정보입니다:
            {pdf_text}

            1. {pdf_text}에서 추출한 캐릭터의 상세한 성격과 전형적인 행동을 바탕으로, {output_text}에서 분석한 대화 패턴을 활용하여 캐릭터의 말투와 행동을 재현한, 사용자가 처음 만났을 때 자연스러운 짧은 인사말을 하세요.
            또한, {dialog_text} 파일에 있는 캐릭터와 다른 인물 간의 대화를 참고하여 보다 자연스러운 표현을 반영하세요. 만약 {pdf_text}와 {output_text}과 {dialog_text}가 비어있다면 2번 항목을 참고하세요.

            2. 다음은 애니 캐릭터에 대한 정보 링크입니다.  {pdf_text}와 {output_text}과 {dialog_text}가 비어있지 않다면 이 항목은 넘기세요.
            [케로로]: [https://namu.wiki/w/%EC%BC%80%EB%A1%9C%EB%A1%9C].
            [프리렌]: [https://namu.wiki/w/%ED%94%84%EB%A6%AC%EB%A0%8C].
            이 정보를 바탕으로, 질문에 답하거나 이 캐릭터로 역할을 연기하세요.

            3. 당신의 캐릭터가 아닌 다른 캐릭터를 인삿말에 언급하지 마세요.

            4. 반드시 한국어로 작성하세요.

            5. 인사말만 작성하세요.
            """
        )
        st.session_state.messages.append({"role": "assistant", "content": first_message})
        st.session_state.stage = 2
        st.rerun()

# 대화 처리 단계
elif st.session_state.stage == 2:
    user_input = st.chat_input("대화를 입력하세요:", key="input_conversation")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.spinner('답변 생성 중... 잠시만 기다려 주세요.'):
            response = generate_conversation(st.session_state.language, st.session_state.character, user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})

# 대화 히스토리 다시 표시
chat_container.empty()  # 이전 메시지 지우기
with chat_container.container():
    st.markdown('<div class="chat-wrapper"><div class="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.messages:
        display_chat_message(msg["role"], msg["content"], st.session_state.character_avatar_url if msg["role"] == "assistant" else user_avatar_url)
    st.markdown('</div></div>', unsafe_allow_html=True)
