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

# ==========================================
# SIDEBAR FEATURES (Clear Chat & Advanced File Upload)
# ==========================================
st.sidebar.title("⚙️ NEX AI Options")

# Clear Chat Button
if st.sidebar.button("🧹 Clear Chat History", type="primary"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

# Upgraded File Uploader (Text, PDFs, Word, Photos)
uploaded_file = st.sidebar.file_uploader(
    "📄 Upload Files or Photos", 
    type=["txt", "py", "md", "pdf", "docx", "jpg", "jpeg", "png"]
)
file_context = ""

if uploaded_file is not None:
    file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type}
    
    # Check if it's an image
    if "image" in uploaded_file.type:
        st.sidebar.image(uploaded_file, caption="Uploaded Photo", use_container_width=True)
        file_context = f"[User uploaded a photo named '{uploaded_file.name}']"
        st.sidebar.warning("Note: Images are recognized, text analysis coming soon!")
    else:
        try:
            # Handle PDF
            if uploaded_file.name.endswith('.pdf'):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    file_context += page.extract_text()
            # Handle Text Files
            else:
                file_context = uploaded_file.read().decode("utf-8")
            st.sidebar.success(f"📄 {uploaded_file.name} loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

# ==========================================
# MAIN CHAT LOGIC WITH VOICE INPUT
# ==========================================

# Purani chats ko screen par dikhana
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- GEMINI STYLE VOICE INPUT CONTAINER ---
st.markdown("### 🎙️ Speak to NEX AI")
# Ye button aapki aawaz ko sunega aur direct text me convert kar dega
voice_text = speech_to_text(start_prompt="🔴 Tap to Speak", stop_prompt="⏹️ Stop Recording", language='en', key='groq_mic')

# Text Chat Input
user_input = st.chat_input("Ask me anything...")

# Dono me se jo bhi input aaye, use final prompt banana
final_prompt = user_input if user_input else voice_text

if final_prompt:
    # Agar document upload hua hai toh uska content sath me jodna
    if file_context and user_input:
        full_prompt = f"Context from file:\n{file_context}\n\nUser Question: {final_prompt}"
    else:
        full_prompt = final_prompt
        
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    with st.chat_message("user"):
        st.markdown(final_prompt)

    # AI ka response generate karna
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
    
