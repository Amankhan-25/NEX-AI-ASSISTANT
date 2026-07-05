import streamlit as st
from groq import Groq
from streamlit_mic_recorder import speech_to_text
import pypdf

# Page layout aur title setup
st.set_page_config(page_title="NEX AI Assistant", page_icon="🤖", layout="centered")

# ==========================================
# ADVANCED TECHY & GEMINI-INSPIRED THEME (CSS)
# ==========================================
st.markdown("""
    <style>
    /* Main Background & Techy Gradient Vibe */
    .stApp {
        background: linear-gradient(135deg, #0b0d19 0%, #111424 50%, #0d0f1d 100%);
        color: #e2e8f0;
        font-family: 'Inter', sans-serif;
    }
    
    /* Top Header/Title Styling */
    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.5px;
    }
    
    /* Sidebar / Glassmorphism effect */
    section[data-testid="stSidebar"] {
        background-color: rgba(17, 20, 36, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Chat Input Bar - Gemini Floating Box Style */
    div[data-testid="stChatInput"] {
        background-color: #1e2238 !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), 0 0 15px rgba(79, 172, 254, 0.1);
        padding: 4px !important;
    }
    
    div[data-testid="stChatInput"] textarea {
        color: #ffffff !important;
    }
    
    /* Chat Message Bubbles Customized */
    div[data-testid="stChatMessage"] {
        background-color: rgba(30, 34, 56, 0.4) !important;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.03);
        margin-bottom: 10px;
        padding: 15px !important;
    }
    
    /* User Message distinct style */
    div[data-testid="stChatMessageUser"] {
        background-color: rgba(79, 172, 254, 0.1) !important;
        border: 1px solid rgba(79, 172, 254, 0.2) !important;
    }
    
    /* Custom divider */
    hr {
        border-color: rgba(255, 255, 255, 0.05) !important;
    }
    </style>
""", unsafe_allowed_html=True)

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
