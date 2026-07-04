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

# Chat history initialize karna
if "messages" not in st.session_state:
    st.session_state.messages = []

# State to track file upload menu pop-up
if "show_upload" not in st.session_state:
    st.session_state.show_upload = False

# ==========================================
# SIDEBAR FEATURES
# ==========================================
st.sidebar.title("⚙️ NEX AI Options")

# Clear Chat Button
if st.sidebar.button("🧹 Clear Chat History", type="primary"):
    st.session_state.messages = []
    st.session_state.show_upload = False
    st.rerun()

# ==========================================
# MAIN CHAT HISTORY SCREEN
# ==========================================
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# GEMINI STYLE FILE UPLOAD CONTROL
# ==========================================
file_context = ""

# Plus button dabaane par khulne wala container
if st.session_state.show_upload:
    with st.container(border=True):
        uploaded_file = st.file_uploader(
            "Upload text, docs, PDFs, or photos", 
            type=["txt", "py", "md", "pdf", "docx", "jpg", "jpeg", "png"],
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            if "image" in uploaded_file.type:
                st.image(uploaded_file, caption="Attached Photo", width=150)
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
# MODERNISED HORIZONTAL CONTROL BAR
# ==========================================
# Spacing layout: [Plus Button] [Gap/Space] [Mic Button]
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([1, 10, 1])

with ctrl_col1:
    # ➕ button bina page ko bar-bar refresh kiye state toggle karega
    if st.button("➕", help="Upload Files/Photos", key="plus_toggle"):
        st.session_state.show_upload = not st.session_state.show_upload
        st.rerun()

with ctrl_col3:
    # Minimalist Voice Mic - Bina kisi bade logo ya text ke
    voice_text = speech_to_text(
        start_prompt="🎙️", 
        stop_prompt="⏹️", 
        language='en', 
        key='groq_mic'
    )

# ==========================================
# CHAT INPUT & PROCESSOR
# ==========================================
# `new.png` jaisa sleek text chat input bar
user_input = st.chat_input("Ask me anything...")

# Check inputs
final_prompt = None
if user_input:
    final_prompt = user_input
elif voice_text:
    final_prompt = voice_text

if final_prompt:
    if file_context:
        full_prompt = f"Context from file:\n{file_context}\n\nUser Question: {final_prompt}"
    else:
        full_prompt = final_prompt
        
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # AI Response generation
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
    
    # Message submit hote hi uploader hide kar do aur state reset karo
    st.session_state.show_upload = False
    st.rerun()
