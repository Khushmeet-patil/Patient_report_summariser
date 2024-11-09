# %%writefile app.py
import os
import tempfile
from datetime import datetime
import streamlit as st
from PyPDF2 import PdfReader
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain

# Page configuration
st.set_page_config(
    page_title="Clinical Records Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced medical-themed CSS [Previous CSS remains the same]
st.markdown("""
    <style>
    .patient-vitals {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        padding: 1rem;
        background-color: #f8f9fa;
        border-radius: 8px;
        margin: 1rem 0;
    }

    .vital-item {
        display: flex;
        align-items: center;
        padding: 0.5rem;
        background-color: white;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .vital-icon {
        margin-right: 0.5rem;
        color: #3498db;
        font-size: 1.2rem;
    }

    .vital-content {
        display: flex;
        flex-direction: column;
    }

    .vital-label {
        font-size: 0.8rem;
        color: #666;
        margin-bottom: 0.2rem;
    }

    .vital-value {
        font-weight: 500;
        color: #2c3e50;
    }
    </style>
""", unsafe_allow_html=True)

def init_session_state():
    if 'patient_records' not in st.session_state:
        st.session_state.patient_records = {}
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'form_key' not in st.session_state:
        st.session_state.form_key = 0
    if 'vector_store' not in st.session_state:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        st.session_state.vector_store = Chroma(
            persist_directory="./chroma_db",
            embedding_function=embeddings
        )
    if 'llm' not in st.session_state:
        api_key = "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"
        st.session_state.llm = ChatGroq(
            model="llama-3.1-70b-versatile",
            api_key=api_key,
            temperature=0,
            max_tokens=8000,
            timeout=60,
            max_retries=3
        )

def format_patient_context(patient_data):
    """Format patient data in a structured way for the LLM."""
    return f"""
PATIENT INFORMATION:
Name: {patient_data['name']}
ID: {patient_data['id']}
Age: {patient_data['age']}
Gender: {patient_data['gender']}
Last Updated: {patient_data['timestamp']}

MEDICAL HISTORY:
{patient_data['text']}

MEDICAL SUMMARY:
{patient_data['summary']}

CURRENT PRESCRIPTION:
{patient_data.get('prescription', 'No current prescription')}
"""

def get_relevant_context(selected_patient=None):
    """Get relevant patient context based on selection."""
    if selected_patient and selected_patient != "All Patients":
        if selected_patient in st.session_state.patient_records:
            return format_patient_context(st.session_state.patient_records[selected_patient])
    else:
        # Combine context from all patients
        all_contexts = []
        for patient_id, data in st.session_state.patient_records.items():
            all_contexts.append(format_patient_context(data))
        return "\n\n===NEXT PATIENT===\n\n".join(all_contexts)
    return ""

def chat_with_docs(question, selected_patient=None):
    """Enhanced chatbot function with better context management."""
    try:
        # Get relevant patient context
        context = get_relevant_context(selected_patient)

        # Prepare the system message
        system_message = """You are an advanced medical assistant with access to patient records.
        Your role is to provide accurate, relevant information based on the available medical records.
        Always specify which patient you're referring to when answering questions.
        If discussing multiple patients, clearly differentiate between them.
        Focus on medical facts and avoid speculation.
        If you're unsure about any information, explicitly state that."""

        # Prepare the question with context
        full_prompt = f"""
Context: {context}

Question: {question}

Please provide a comprehensive answer based on the available medical records.
"""
        messages = [
            ("system", system_message),
            ("human", full_prompt)
        ]

        # Get response from LLM
        response = st.session_state.llm.invoke(messages)

        return response.content

    except Exception as e:
        st.error(f"Error processing question: {str(e)}")
        return None

def extract_text_from_pdf(pdf_file):
    """Extract text from uploaded PDF file."""
    try:
        pdf_reader = PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error extracting text from PDF: {str(e)}")
        return None

def generate_summary(text):
    """Generate medical summary using LLM."""
    try:
        system_prompt = """You are a medical professional summarizing patient records.
        Focus on key medical findings, diagnoses, treatments, and recommendations.
        Format the summary in clear sections:
        1. Chief Complaints
        2. Key Findings
        3. Diagnoses
        4. Treatments
        5. Recommendations
        Use medical terminology appropriately and be concise but thorough."""

        messages = [
            ("system", system_prompt),
            ("human", f"Please summarize the following medical record:\n\n{text}")
        ]

        response = st.session_state.llm.invoke(messages)
        return response.content
    except Exception as e:
        st.error(f"Error generating summary: {str(e)}")
        return None

def main():
    init_session_state()

    # Header
    st.markdown("""
        <div class="hospital-header">
            <h1>🏥 Clinical Records Management System</h1>
            <p>Secure • Efficient • Intelligent</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.image("D:\hackthisfall\large.png", width=150)
        st.title("Patient Management")

        # Patient record form
        with st.form(key=f"patient_record_form_{st.session_state.form_key}"):
            st.markdown("<h3>Add New Patient Record</h3>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                patient_name = st.text_input("Patient Name")
                patient_age = st.number_input("Age", min_value=0, step=1)
            with col2:
                patient_id = st.text_input("Patient ID")
                patient_gender = st.selectbox("Gender", ["Select", "Male", "Female", "Other"])

            st.markdown("""
                <div class="upload-container">
                    <h4>📄 Upload Medical Records</h4>
                </div>
            """, unsafe_allow_html=True)
            patient_history = st.file_uploader("Upload Patient History (PDF)", type=["pdf"])

            submit_button = st.form_submit_button("Add Patient Record")

            if submit_button:
                if all([patient_name, patient_id, patient_history]) and patient_gender != "Select":
                    with st.spinner("Processing patient record..."):
                        text = extract_text_from_pdf(patient_history)
                        if text:
                            summary = generate_summary(text)
                            if summary:
                                record = {
                                    'name': patient_name,
                                    'id': patient_id,
                                    'age': patient_age,
                                    'gender': patient_gender,
                                    'text': text,
                                    'summary': summary,
                                    'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                }
                                st.session_state.patient_records[patient_id] = record
                                st.success(f"Successfully added patient: {patient_name}")
                                st.session_state.form_key += 1
                                st.rerun()
                else:
                    st.warning("Please fill in all required fields.")

    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["📋 Patient Records", "📊 Medical Summaries", "💬 Medical Assistant"])

    # Patient Records Tab
    with tab1:
      st.subheader("Patient Records")
      if st.session_state.patient_records:
          for patient_id, data in st.session_state.patient_records.items():
            with st.container():
                # Create a card-like container
                with st.container():
                    # Header with patient name and ID
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"### {data['name']} 🟢")
                    with col2:
                        st.markdown(f"**ID:** {patient_id}")

                    # Divider
                    st.divider()

                    # Patient vitals in columns
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        st.markdown("##### Age 👤")
                        st.write(f"{data['age']} years")

                    with col2:
                        st.markdown("##### Gender ⚧")
                        st.write(data['gender'])

                    with col3:
                        st.markdown("##### Last Updated 🕒")
                        st.write(data['timestamp'])

                    # Medical Record Expander
                    with st.expander("View Full Medical Record"):
                        st.text_area("", data['text'], height=300)

                # Add some spacing between patient cards
                st.markdown("<br>", unsafe_allow_html=True)
          else:
            st.info("No patient records available. Add patients using the sidebar form.")
    # Medical Summaries Tab
    with tab2:
        st.subheader("Medical Summaries")
        if st.session_state.patient_records:
            selected_patient = st.selectbox(
                "Select Patient",
                options=list(st.session_state.patient_records.keys()),
                format_func=lambda x: f"{st.session_state.patient_records[x]['name']} (ID: {x})"
            )

            if selected_patient:
                data = st.session_state.patient_records[selected_patient]
                st.markdown(f"""
                    <div class="medical-summary">
                        <h3>{data['name']}</h3>
                        <div style="margin-top: 1rem;">
                            <h4>Medical Summary:</h4>
                            <p>{data['summary']}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='prescription-box'>", unsafe_allow_html=True)
                prescription = st.text_area(
                    "Update Prescription",
                    value=data.get('prescription', ''),
                    height=200
                )
                if st.button("Save Prescription"):
                    data['prescription'] = prescription
                    st.session_state.patient_records[selected_patient] = data
                    st.success("Prescription updated successfully!")
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("No patient summaries available. Add patients using the sidebar form.")

    # Medical Assistant Tab
    with tab3:
        st.subheader("Medical Assistant")

        if st.session_state.patient_records:
            col1, col2 = st.columns([3, 1])
            with col1:
                selected_patient = st.selectbox(
                    "Select Patient Context",
                    ["All Patients"] + list(st.session_state.patient_records.keys()),
                    format_func=lambda x: (
                        "All Patients" if x == "All Patients"
                        else f"{st.session_state.patient_records[x]['name']} (ID: {x})"
                    )
                )

            with col2:
                if st.button("Clear Chat History", key="clear_chat"):
                    st.session_state.chat_history = []
                    st.rerun()

            # Chat interface
            st.markdown("<div class='chat-container'>", unsafe_allow_html=True)

            # Display chat history
            for message in st.session_state.chat_history:
                st.markdown(
                    f"""<div class="chat-message {message['role']}">
                        <strong>{'You' if message['role'] == 'user' else '🤖 Medical Assistant'}:</strong>
                        <div style="margin-top: 0.5rem;">{message['content']}</div>
                    </div>""",
                    unsafe_allow_html=True
                )

            # Chat input
            with st.container():
                question = st.text_input("Ask about patient medical records:", key="chat_input")
                if question:
                    if st.button("Send", key="send_button"):
                        with st.spinner("Processing your question..."):
                            answer = chat_with_docs(question, selected_patient)
                            if answer:
                                st.session_state.chat_history.append({'role': 'user', 'content': question})
                                st.session_state.chat_history.append({'role': 'assistant', 'content': answer})
                                st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.info("Add patient records to start using the medical assistant.")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please refresh the page and try again.")