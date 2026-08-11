import os
import streamlit as st
from dotenv import load_dotenv
import google.genai as genai
from google.genai import types
import pypdf
import docx

# Load environment variables robustly
base_dir = os.path.dirname(os.path.abspath(__file__))
dotenv_path = os.path.join(base_dir, ".env")
load_dotenv(dotenv_path)

api_key = os.getenv("GOOGLE_API_KEY")

# Page Configuration
st.set_page_config(
    page_title="DocuMind AI - Document Reader & Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Sleek gradient and glassmorphism styling */
    .main {
        background: #0e1117;
    }
    .stChatInputContainer {
        padding-bottom: 20px;
    }
    section[data-testid="stSidebar"] {
        background-color: #1a1c23;
    }
    h1 {
        font-family: 'Outfit', 'Inter', sans-serif;
        font-weight: 700;
        background: linear-gradient(45deg, #FF4B4B, #FF8F8F);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .doc-card {
        padding: 15px;
        border-radius: 10px;
        background-color: #1e222b;
        border-left: 5px solid #FF4B4B;
        margin-bottom: 15px;
    }
    .info-text {
        font-size: 0.9rem;
        color: #a0aec0;
    }
    /* Smooth hover transitions */
    .stButton>button {
        transition: all 0.3s ease;
        border-radius: 8px;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 75, 75, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# App Title & Header
st.title("🤖 DocuMind AI")
st.write("An intelligent conversational document assistant powered by Gemini 3.5.")

# Check API Key
if not api_key:
    st.error("⚠️ GOOGLE_API_KEY is missing in your `.env` file. Please check your `.env` configuration.")
    st.stop()

# Initialize Gemini Client
@st.cache_resource
def get_gemini_client(key):
    try:
        return genai.Client(api_key=key)
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")
        st.stop()

client = get_gemini_client(api_key)

# Sidebar Options and Document Upload
with st.sidebar:
    st.header("📁 Document Center")
    st.write("Upload your document to chat with it.")
    
    uploaded_file = st.file_uploader(
        "Supported formats: PDF, DOCX, TXT", 
        type=["pdf", "docx", "txt"],
        help="Upload a file and ask questions about its content."
    )
    
    st.markdown("---")
    st.header("⚙️ Session Controls")
    
    # Clear chat session
    if st.button("🔄 Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.success("Conversation history cleared!")
        st.rerun()

# Track active document in session state
if "active_doc_name" not in st.session_state:
    st.session_state.active_doc_name = None
if "document_text" not in st.session_state:
    st.session_state.document_text = ""
if "document_bytes" not in st.session_state:
    st.session_state.document_bytes = None
if "document_mime" not in st.session_state:
    st.session_state.document_mime = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# Process uploaded file
if uploaded_file is not None:
    # If a new document is uploaded, reset the conversation to avoid cross-contamination
    if st.session_state.active_doc_name != uploaded_file.name:
        st.session_state.active_doc_name = uploaded_file.name
        st.session_state.messages = []  # Clear history for new document
        st.session_state.document_text = ""
        st.session_state.document_bytes = None
        st.session_state.document_mime = None
        
        file_type = uploaded_file.name.split(".")[-1].lower()
        
        with st.spinner("Extracting content..."):
            try:
                uploaded_file.seek(0)
                if file_type == "pdf":
                    # Keep raw bytes for Gemini native processing
                    st.session_state.document_bytes = uploaded_file.getvalue()
                    st.session_state.document_mime = "application/pdf"
                    
                    # Extract text for local preview/metadata fallback
                    reader = pypdf.PdfReader(uploaded_file)
                    text_pages = []
                    for page in reader.pages:
                        extracted = page.extract_text()
                        if extracted:
                            text_pages.append(extracted)
                    st.session_state.document_text = "\n".join(text_pages)
                    
                elif file_type == "txt":
                    raw_data = uploaded_file.read()
                    try:
                        st.session_state.document_text = raw_data.decode("utf-8")
                    except UnicodeDecodeError:
                        st.session_state.document_text = raw_data.decode("latin-1")
                        
                elif file_type == "docx":
                    doc = docx.Document(uploaded_file)
                    st.session_state.document_text = "\n".join([para.text for para in doc.paragraphs])
                
                st.toast(f"Successfully processed {uploaded_file.name}!", icon="✅")
            except Exception as e:
                st.error(f"Error reading document: {e}")
                st.session_state.active_doc_name = None
else:
    st.session_state.active_doc_name = None
    st.session_state.document_text = ""
    st.session_state.document_bytes = None
    st.session_state.document_mime = None

# Show Document Info Card in Sidebar if loaded
if st.session_state.active_doc_name:
    with st.sidebar:
        char_count = len(st.session_state.document_text)
        word_count = len(st.session_state.document_text.split()) if char_count > 0 else 0
        st.markdown(f"""
        <div class="doc-card">
            <strong>📄 Active Document:</strong><br/>
            <span style="font-size: 0.85rem; color:#FF8F8F;">{st.session_state.active_doc_name}</span>
            <div class="info-text" style="margin-top: 8px;">
                📏 Characters: {char_count:,}<br/>
                📝 Words: {word_count:,}<br/>
                ℹ️ <em>Gemini will process this document natively.</em>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.document_text:
            with st.expander("🔍 Preview Document Text"):
                st.text(st.session_state.document_text[:2000] + ("..." if char_count > 2000 else ""))
else:
    with st.sidebar:
        st.info("💡 No document active. You can still chat with Gemini about general topics.")

# Display Chat History
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User Chat Input
user_input = st.chat_input("Ask a question about the document or anything else...")

if user_input:
    # Render user message
    with st.chat_message("user"):
        st.markdown(user_input)
    
    # Store user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Prepare contents history for Gemini
    gemini_contents = []
    
    # Determine system instructions
    system_instruction = "You are DocuMind, an elite AI assistant. Be helpful, concise, and accurate."
    
    # If we have extracted text but no bytes (like TXT/DOCX), put it in system instruction
    if st.session_state.document_text and not st.session_state.document_bytes:
        system_instruction += f"\n\nHere is the content of the user's uploaded document:\n{st.session_state.document_text}\n\nAnswer all questions using the document context above."
    
    # Map messages to API structures
    for idx, msg in enumerate(st.session_state.messages):
        role = "user" if msg["role"] == "user" else "model"
        
        # In Gemini API, if we have raw PDF bytes, we send it in the FIRST user message
        if idx == 0 and role == "user" and st.session_state.document_bytes:
            gemini_contents.append(
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_bytes(
                            data=st.session_state.document_bytes,
                            mime_type=st.session_state.document_mime
                        ),
                        types.Part.from_text(text=f"Please analyze this document. User question: {msg['content']}")
                    ]
                )
            )
        else:
            gemini_contents.append(
                types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])]
                )
            )
            
    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("DocuMind is thinking..."):
            try:
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=gemini_contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction
                    )
                )
                assistant_response = response.text
                message_placeholder.markdown(assistant_response)
                
                # Store response
                st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            except Exception as e:
                err_msg = f"Sorry, I encountered an error: {e}"
                message_placeholder.error(err_msg)
                # Don't store the failed response in message history to avoid repeating errors
