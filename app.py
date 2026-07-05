import streamlit as st
from groq import Groq
import pypdf
import json

# Page layout aur title setup (Sabse upar hona chahiye)
st.set_page_config(page_title="NEX AI Assistant", page_icon="🤖", layout="centered")

# ==========================================
# SAFE DYNAMIC TECHY & GEMINI-INSPIRED THEME
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
        flex-direction: column;
        align-items: flex-start;
    }
    .bubble-wrapper {
        display: flex;
        align-items: flex-start;
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
    
    /* PROPER INLINE GEMINI TOOLBAR STYLING */
    .gemini-toolbar {
        display: flex;
        gap: 16px;
        margin-left: 45px;
        margin-top: 4px;
        margin-bottom: 15px;
        align-items: center;
    }
    .tool-btn {
        background: transparent;
        border: none;
        color: #8a8d9f;
        cursor: pointer;
        font-size: 14px;
        transition: color 0.2s;
        padding: 4px;
    }
    .tool-btn:hover {
        color: #00f2fe;
    }
    
    /* Native utility toast style overlay */
    .toast-popup {
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: #1e2238;
        color: #00f2fe;
        border: 1px solid #4facfe;
        padding: 8px 16px;
        border-radius: 20px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        z-index: 99999;
        font-family: sans-serif;
    }
    </style>
    
    <script>
    // System UI clipboard callback framework
    function copyTextToClipboard(base64Text) {
        // Decode base64 to avoid formatting breaking issues
        const text = atob(base64Text);
        navigator.clipboard.writeText(text).then(function() {
            const toast = document.createElement('div');
            toast.className = 'toast-popup';
            toast.innerText = '📋 Text Copied!';
            document.body.appendChild(toast);
            setTimeout(() => toast.remove(), 1800);
        }).catch(function(err) {
            console.error('Could not copy text: ', err);
        });
    }
    
    function triggerToast(message) {
        const toast = document.createElement('div');
        toast.className = 'toast-popup';
        toast.innerText = message;
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 1800);
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
# MAIN CHAT LOGIC WITH INLINE GEMINI CONTROLS
# ==========================================

# Query Re-generation checker
if "redo_query" not in st.session_state:
    st.session_state.redo_query = None

# Purani chats ko render karna
for idx, message in enumerate(st.session_state.messages):
    if message["role"] == "user":
        st.html(f'''
            <div class="chat-row row-user">
                <div class="bubble bubble-user">{message["content"]}</div>
                <div class="avatar">👤</div>
            </div>
        ''')
    else:
        # String encoding hack to safely pass data to JavaScript without crashing on quotes/newlines
        import base64
        encoded_response = base64.b64encode(message["content"].encode('utf-8')).decode('utf-8')
        
        # Ek single layout container me bubble aur unke tool rows ko align kiya hai
        st.html(f'''
            <div class="chat-row row-bot">
                <div class="bubble-wrapper">
                    <div class="avatar">🤖</div>
                    <div class="bubble bubble-bot">{message["content"]}</div>
                </div>
                <!-- Perfectly aligned tool row structure -->
                <div class="gemini-toolbar">
                    <button class="tool-btn" onclick="triggerToast('👍 Thanks for the feedback!')">👍</button>
                    <button class="tool-btn" onclick="triggerToast('👎 Feedback recorded.')">👎</button>
                    <button class="tool-btn" onclick="window.location.href='?redo_idx={idx}'">🔄</button>
                    <button class="tool-btn" onclick="triggerToast('📤 Feature Coming Soon!')">📤</button>
                    <!-- Base64 Decoded 100% Working Clipboard Copy Command -->
                    <button class="tool-btn" onclick="copyTextToClipboard('{encoded_response}')">📋</button>
                </div>
            </div>
        ''')

# Handle Redo clicks smoothly
query_params = st.query_params
if "redo_idx" in query_params:
    redo_index = int(query_params["redo_idx"])
    st.query_params.clear()
    for prev in reversed(st.session_state.messages[:redo_index]):
        if prev["role"] == "user":
            st.session_state.redo_query = prev["content"]
            st.rerun()

# Text Chat Input Processing
user_input = st.chat_input("Ask me anything...")

final_prompt = user_input if user_input else st.session_state.redo_query

if final_prompt:
    if st.session_state.redo_query:
        st.session_state.redo_query = None
        
    if file_context:
        full_prompt = f"Context from file:\n{file_context}\n\nUser Question: {final_prompt}"
    else:
        full_prompt = final_prompt
        
    st.session_state.messages.append({"role": "user", "content": final_prompt})
    st.rerun()

# AI Assistant Text Execution Chain
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
