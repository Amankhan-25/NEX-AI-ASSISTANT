import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
import pypdf

# 1. Page Config (Sabse upar hona chahiye)
st.set_page_config(page_title="NEX AI Assistant", page_icon="🤖", layout="centered")

# Custom CSS taaki input columns ek line me perfect dikhein
st.markdown("""
    <style>
    div[data-testid="column"] {
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .stTextInput>div>div>input {
        padding: 10px;
    }
    </style>
""", unsafe_allowed_html=True)

st.title("🤖 NEX AI Assistant")
st.caption("Made by Mr.Amankhan | Available 24/7 Live")

# 2. API Key Management
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not api_key:
    st.info("Please add your Groq API Key to start chatting!", icon="🔑")
    st.stop()

client = Groq(api_key=api_key)

# 3. Session States Setup
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False

# Sidebar Options (Sirf Clear Chat rakha hai)
st.sidebar.title("⚙️ NEX AI Options")
if st.sidebar.button("🧹 Clear Chat History", type="primary"):
    st.session_state.messages = []
    st.session_state.show_upload = False
    st.rerun()

# 4. Chat History Render Container
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# 5. Gemini-style Dropdown File Uploader
file_context = ""
if st.session_state.show_upload:
    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Upload files/photos", 
            type=["txt", "py", "md", "pdf", "docx", "jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            if "image" in uploaded_file.type:
                st.image(uploaded_file, caption="Attached Photo", width=120)
                file_context = f"[User uploaded a photo named '{uploaded_file.name}']"
            else:
                try:
                    if uploaded_file.name.endswith('.pdf'):
                        pdf_reader = pypdf.PdfReader(uploaded_file)
                        for page in pdf_reader.pages:
                            file_context += page.extract_text()
                    else:
                        file_context = uploaded_file.read().decode("utf-8")
                    st.success(f"📄 {uploaded_file.name} attached!")
                except Exception as e:
                    st.error(f"Error: {e}")

st.markdown("<br>", unsafe_allowed_html=True)

# 6. UPDATED INPUT BAR LAYOUT (Parallel Columns)
input_col1, input_col2, input_col3, input_col4 = st.columns([0.8, 8.0, 0.8, 0.8])

with input_col1:
    # ➕ Icon Button for file upload toggle
    if st.button("➕", help="Upload Files", key="plus_btn"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()

with input_col2:
    # Text Input Box (Ask me anything...)
    text_prompt = st.text_input("Input Text", placeholder="Ask me anything...", label_visibility="collapsed", key="user_text_input")

with input_col3:
    # Voice Input Mic Widget (No extra text labels)
    voice_prompt = speech_to_text(
        start_prompt="🎙️", 
        stop_prompt="⏹️", 
        language='en', 
        key='nex_voice_mic'
    )

with input_col4:
    # Send Arrow Button
    send_btn = st.button("⬆️", key="submit_send")

# 7. AI Logic Processing
final_prompt = None
if send_btn and text_prompt:
    final_prompt = text_prompt
elif voice_prompt:
    final_prompt = voice_prompt

if final_prompt:
    if file_context:
        full_prompt = f"Context from file:\n{file_context}\n\nUser Question: {final_prompt}"
    else:
        full_prompt = final_prompt
        
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    
    with chat_container:
        with st.chat_message("user"):
            st.markdown(final_prompt)
            
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            
            try:
                current_messages = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
                if file_context:
                    current_messages[-1]["content"] = full_prompt

                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant", 
                    messages=current_messages,
                    stream=True,
                )
                
                for chunk in completion:
                    if chunk.choices[0].delta.content:
                        full_response += chunk.choices[0].delta.content
                        message_placeholder.markdown(full_response + "▌")
                
                message_placeholder.markdown(full_response)
            except Exception as e:
                st.error(f"Error: {e}")
                
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.show_upload = False
    st.rerun()
