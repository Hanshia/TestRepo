import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import os

st.session_state.language = '한국어'

# Streamlit 설정
st.set_page_config(page_title="블로그 도와줘!", page_icon=":house_with_garden:")

# 환경 변수 설정
os.environ["GOOGLE_API_KEY"] = st.secrets["MY_GOOGLE_API_KEY"]

# Google Generative AI 설정
client = ChatGoogleGenerativeAI(model="gemini-pro", api_key=os.environ.get("GOOGLE_API_KEY"))

# 애니 캐릭터와 그들의 정보 및 이미지 URL
characters = {
    "케로로": ["개구리중사", "https://i.namu.wiki/i/c1GTTKMxSQJhdu1ro8bu9KxQqe6csuMTxAA_V-TkxKS2D6CPzXFHXG8pG9PnAYeLFPOT-1vFSVDWmcEuT2fYTw.webp"],
    "코난": ["명탐정 코난", "https://i.namu.wiki/i/Tf8RK2-Zcr78evjdh9AzcnmL0c9KZvikc5mawtLMBjukOPqlJzRnN23MSJfwwNbvu0UGHyJjjnt3x519eqOA-g.webp"]
}

# 사용자 아바타 이미지 URL
user_avatar_url = "https://via.placeholder.com/50?text=User"
assistant_avatar_url = "https://via.placeholder.com/50?text=Bot"

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
    prompt = f"""
    1. 당신은 지금 {character}의 역할을 연기하고 있습니다. 사용자의의 요구와 질문에 {character}의 말투와 스타일로 한국어로 응답하세요.

    2. 다음은 애니 캐릭터에 대한 정보 링크입니다
    [케로로]: [https://namu.wiki/w/%EC%BC%80%EB%A1%9C%EB%A1%9C].
    [코난]: [https://namu.wiki/w/%EC%97%90%EB%8F%84%EA%B0%80%EC%99%80%20%EC%BD%94%EB%82%9C], 말투는 반말로 해주세요.
    [코난]의 명대사: [https://namu.wiki/w/%EB%AA%85%ED%83%90%EC%A0%95%20%EC%BD%94%EB%82%9C/%EB%AA%85%EB%8C%80%EC%82%AC]
    이 정보를 바탕으로, 질문에 답하거나 이 캐릭터로 역할을 연기하세요.

    3. 사용자가 주제를 추천하길 원한다면, 최근 구글에서서 [특정 주제 분야, 예: 기술, 여행, 음식 등]와 관련된 인기 있는 주제를 검색하여 추천해 주세요.

    4. 다음은 사용자의 블로그 링크입니다: [https://gunrestaurant.tistory.com/]. 제공된 블로그의 글 스타일을 분석한 후, 사용자가 입력한 주제로 동일한 스타일의 블로그 글을 작성해 주세요. 글의 길이는 약 500 단어로 작성해 주세요.

    5. 사용자가 글의 개선하고 싶어하면 내용을 검토한 후, 명확성, 톤, 전반적인 품질을 향상시킬 수 있는 수정 사항을 제안해 주세요

    사용자 입력: {user_input}
    """
    response = client.invoke(prompt)
    return response.content

# Streamlit 애플리케이션 시작
st.title("블로그 도와줘!")

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
        if st.button(f"{character} 선택", key=f"{character_key}_button"):
            selected_character = character
            break
        st.markdown(f"""
        <div class="member-card" id="{character_key}">
            <img src="{info[1]}" class="chat-avatar">
            <span>{character}</span>
        </div>
        """, unsafe_allow_html=True)

    if selected_character:
        st.session_state.character = selected_character
        st.session_state.character_avatar_url = characters[selected_character][1]
        request_message = f"안녕하세요! {selected_character}입니다. 무엇을 도와드릴까요?"
        st.session_state.messages.append({"role": "assistant", "content": request_message})
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
