import streamlit as st
from groq import Groq
import pypdf
import base64

# Page layout aur title setup (Sabse upar hona chahiye)
st.set_page_config(page_title="NEX AI Assistant", page_icon="🤖", layout="centered")

# ==========================================
# ADVANCED TECHY THEME WITH INLINE BUTTONS FIX
# ==========================================
st.html(r"""
    <style>
    /* Main Background Tech Gradient */
    .stApp {
        background: linear-gradient(135deg, #0b0d19 0%, #111424 50%, #0d0f1d 100%) !important;
        color: #e2e8f0 !important;
    }
    
    /* Gemini Glowing Gradient Title */
    h1 {
        background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Sidebar Glassmorphism */
    section[data-testid="stSidebar"] {
        background-color: rgba(17, 20, 36, 0.7) !important;
        backdrop-filter: blur(10px);
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Chat Input Floating Box Vibe */
    div[data-testid="stChatInput"] {
        background-color: #1e2238 !important;
        border: 1px solid rgba(79, 172, 254, 0.3) !important;
        border-radius: 16px !important;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }
    
    /* TECHIE CHAT BUBBLES CUSTOM STYLING */
    .chat-row {
        display: flex;
        margin-bottom: 5px;
        width: 100%;
    }
    .row-user {
        justify-content: flex-end;
    }
    .row-bot {
        justify-content: flex-start;
    }
    .bubble {
        padding: 12px 16px;
        border-radius: 14px;
        max-width: 75%;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    }
    .bubble-user {
        background-color: rgba(79, 172, 254, 0.15);
        border: 1px solid rgba(79, 172, 254, 0.4);
        color: #ffffff;
        border-top-right-radius: 2px;
    }
    .bubble-bot {
        background-color: rgba(30, 34, 56, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        color: #e2e8f0;
        border-top-left-radius: 2px;
    }
    .avatar {
        font-size: 18px;
        margin: 0 10px;
        display: flex;
        align-items: center;
    }
    
    /* FIX FOR THE STRANGE BUTTON BOXES (a2.png Fix) */
    div[data-testid="stHorizontalBlock"] button {
        background-color: transparent !important;
        border: none !important;
        padding: 2px 6px !important;
        margin: 0px !important;
        width: auto !important;
        height: auto !important;
        box-shadow: none !important;
        font-size: 16px !important;
        transition: transform 0.2s ease;
    }
    div[data-testid="stHorizontalBlock"] button:hover {
        transform: scale(1.2);
        background-color: transparent !important;
    }
    div[data-testid="stHorizontalBlock"] button p {
        font-size: 16px !important;
    }
    
    /* Gemini Action Toolbar Spacing */
    .action-bar-container {
        margin-left: 45px;
        margin-bottom: 15px;
        margin-top: -5px;
    }
    </style>
    
    <script>
    // Real-time Operating System Clipboard Copy Function
    function nexCopyToClipboard(base64Text) {
        const text = atob(base64Text);
        navigator.clipboard.writeText(text).then(function() {
            // Streamlit Native Component standard communication framework fallback text
            console.log('Copied successfully');
        }).catch(function(err) {
            console.error('Failed to copy text: ', err);
        });
    }
    </script>
""")

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
if "regenerate_trigger" not in st.session_state:
    st.session_state.regenerate_trigger = None

# ==========================================
# SIDEBAR FEATURES
# ==========================================
st.sidebar.title("⚙️ NEX AI Options")

if st.sidebar.button("🧹 Clear Chat History", type="primary"):
    st.session_state.messages = []
    st.rerun()

st.sidebar.markdown("---")

# Upgraded File Uploader
uploaded_file = st.sidebar.file_uploader(
    "📄 Upload Files or Photos", 
    type=["txt", "py", "md", "pdf", "docx", "jpg", "jpeg", "png"]
)
file_context = ""

if uploaded_file is not None:
    if "image" in uploaded_file.type:
        st.sidebar.image(uploaded_file, caption="Uploaded Photo", use_container_width=True)
        file_context = f"[User uploaded a photo named '{uploaded_file.name}']"
        st.sidebar.warning("Note: Images are recognized, text analysis coming soon!")
    else:
        try:
            if uploaded_file.name.endswith('.pdf'):
                pdf_reader = pypdf.PdfReader(uploaded_file)
                for page in pdf_reader.pages:
                    file_context += page.extract_text()
            else:
                file_context = uploaded_file.read().decode("utf-8")
            st.sidebar.success(f"📄 {uploaded_file.name} loaded successfully!")
        except Exception as e:
            st.sidebar.error(f"Error reading file: {e}")

# ==========================================
# MAIN CHAT LOGIC WITH FIXED GEMINI TOOLBAR
# ==========================================

# Purani chats ko screen par dikhana
for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.html(f'''
            <div class="chat-row row-user">
                <div class="bubble bubble-user">{message["content"]}</div>
                <div class="avatar">👤</div>
            </div>
        ''')
    else:
        # Assistant Response Bubble
        st.html(f'''
            <div class="chat-row row-bot">
                <div class="avatar">🤖</div>
                <div class="bubble bubble-bot">{message["content"]}</div>
            </div>
        ''')
        
        # Wrapped container for perfect alignment alignment
        st.markdown('<div class="action-bar-container">', unsafe_allowed_html=True)
        btn_cols = st.columns([0.05, 0.05, 0.05, 0.05, 0.05, 0.75], gap="small")
        
        with btn_cols[0]:
            if st.button("👍", key=f"good_{idx}", help="Good response"):
                st.toast("Thanks for feedback! 👍")
        with btn_cols[1]:
            if st.button("👎", key=f"bad_{idx}", help="Bad response"):
                st.toast("Feedback recorded to improve NEX. 👎")
        with btn_cols[2]:
            if st.button("🔄", key=f"redo_{idx}", help="Regenerate response"):
                for prev in reversed(st.session_state.messages[:idx]):
                    if prev["role"] == "user":
                        st.session_state.regenerate_trigger = prev["content"]
                        st.rerun()
        with btn_cols[3]:
            st.download_button("📤", data=message["content"], file_name="nex_response.txt", key=f"share_{idx}", help="Export response")
        with btn_cols[4]:
            # Fixed Copy Button using dynamic Base64 encryption to avoid break codes
            encoded_txt = base64.b64encode(message["content"].encode('utf-8')).decode('utf-8')
            if st.button("📋", key=f"copy_{idx}", help="Copy to clipboard"):
                st.html(f"<script>nexCopyToClipboard('{encoded_txt}');</script>")
                st.toast("Copied to clipboard! 📋")
        st.markdown('</div>', unsafe_allowed_html=True)

# Input Processing Elements
user_input = st.chat_input("Ask me anything...")

# Redo chain activation override
final_prompt = None
if user_input:
    final_prompt = user_input
elif st.session_state.regenerate_trigger:
    final_prompt = st.session_state.regenerate_trigger
    st.session_state.regenerate_trigger = None  # Reset state after trigger

if final_prompt:
    if file_context:
        full_prompt = f"Context from file:\n{file_context}\n\nUser Question: {final_prompt}"
    else:
        full_prompt = final_prompt
        
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    st.rerun()

# AI Response Generation Setup
if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
    latest_user_msg = st.session_state.messages[-1]["content"]
    
    try:
        current_messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        if file_context:
            current_messages[-1]["content"] = f"Context from file:\n{file_context}\n\nUser Question: {latest_user_msg}"

        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant", 
            messages=current_messages,
            stream=False,
        )
        
        full_response = completion.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": full_response})
        st.rerun()
    except Exception as e:
        st.error(f"Error: {e}")
        
