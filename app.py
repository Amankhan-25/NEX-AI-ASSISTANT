import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
import pypdf

# Page layout aur title setup
st.set_page_config(page_title="NEX AI Assistant", page_icon="🤖", layout="centered")

st.title("🤖 NEX AI Assistant")
st.caption("Made by Mr.Amankhan | Available 24/7 Live")

# Streamlit ke Secrets se API Key securely nikalna
if "GROQ_API_KEY" in st.secrets:
    api_key = st.secrets["GROQ_API_KEY"]
else:
    api_key = st.sidebar.text_input("Enter Groq API Key:", type="password")

if not api_key:
    st.info("Please add your Groq API Key to start chatting!", icon="🔑")
    st.stop()

# Groq Client start karna
client = Groq(api_key=api_key)

# Chat history aur session states initialize karna
if "messages" not in st.session_state:
    st.session_state.messages = []
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False
if "voice_active" not in st.session_state:
    st.session_state.voice_active = False

# ==========================================
# SIDEBAR FEATURES
# ==========================================
st.sidebar.title("⚙️ NEX AI Options")

# Clear Chat Button
if st.sidebar.button("🧹 Clear Chat History", type="primary"):
    st.session_state.messages = []
    st.session_state.show_upload = False
    st.session_state.voice_active = False
    st.rerun()

# ==========================================
# MAIN CHAT HISTORY SCREEN
# ==========================================
# Chat messages ke liye container taaki scroll proper rahe
chat_container = st.container()
with chat_container:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ==========================================
# GEMINI STYLE FILE UPLOAD PANEL
# ==========================================
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

# ==========================================
# FIXED SLEEK INPUT BAR LAYOUT (As per new.png)
# ==========================================
st.markdown("<br>", unsafe_allowed_html=True)

# Ek single horizontal row (Columns) chat input ke liye
input_col1, input_col2, input_col3, input_col4 = st.columns([0.6, 7.5, 0.7, 0.7])

with input_col1:
    # ➕ Icon Button
    if st.button("➕", help="Upload Files/Photos", key="btn_plus"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()

with input_col2:
    # Main TextInput (Placeholder: Ask me anything...)
    # label_visibility="collapsed" se box ekdum plain text bar jaisa dikhega
    text_prompt = st.text_input("Chat Input", placeholder="Ask me anything...", label_visibility="collapsed", key="text_msg")

with input_col3:
    # Minimalist Voice Mic - Bina kisi extra text ya instructions ke
    voice_prompt = speech_to_text(
        start_prompt="🎙️", 
        stop_prompt="⏹️", 
        language='en', 
        key='groq_mic_fixed'
    )

with input_col4:
    # Enter / Send Button (Arrow Icon)
    send_clicked = st.button("⬆️", key="btn_send")

# ==========================================
# FINAL PROMPT PROCESSING
# ==========================================
final_prompt = None

# Agar text likh kar enter/send kiya ya voice input aaya
if send_clicked and text_prompt:
    final_prompt = text_prompt
elif voice_prompt:
    final_prompt = voice_prompt

if final_prompt:
    # Context integration logic
    if file_context:
        full_prompt = f"Context from file:\n{file_context}\n\nUser Question: {final_prompt}"
    else:
        full_prompt = final_prompt
        
    # User message push
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    
    # AI Response generation
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
    
    # Reset states after sending message
    st.session_state.show_upload = False
    st.rerun()
