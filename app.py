from attr import s
import streamlit as st
import fitz  # PyMuPDF for PDF
from openai import OpenAI
import json
import re
import datetime


# Define password for testing
# Retrieve the correct password securely from Streamlit secrets
CORRECT_PASSWORD = st.secrets["test_password"]

def check_password():
    """Returns `True` if the user had the correct password."""
    
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False
        
    if not st.session_state["password_correct"]:
        st.title("Login Required")
        
        with st.form("login_form", clear_on_submit=True):
            password = st.text_input("Enter password:", type="password")
            submitted = st.form_submit_button("Submit")
            
            if submitted:
                if password == CORRECT_PASSWORD:
                    st.session_state["password_correct"] = True
                    st.rerun()
                else:
                    st.error("Access denied. Incorrect password.")
         
        return False
    
    return True

# Call the function to check authentication
if check_password():
    client = OpenAI(api_key=st.secrets["openai_api_key"])

    # Helper function to extract text from PDF
    def extract_text_from_pdf(pdf_file):
        pdf_reader = fitz.open(stream=pdf_file.read(), filetype="pdf")
        return "".join(page.get_text() for page in pdf_reader)

    # Helper function to call OpenAI and return metadata
    def call_openai_for_metadata(text):
        metadata_prompt = f"""
        You are a friendly legal assistant. From the following contract, please extract:
        - Contract Type
        - Parties Involved (as a comma-separated string, not a list)
        - Effective Date
        - Expiration Date
        - Brief Summary

        Contract Text:
        {text}

        Format the output strictly as JSON with these keys:
        {{
            "Contract Type": "",
            "Parties Involved": "",
            "Effective Date": "",
            "Expiration Date": "",
            "Summary Text": ""
        }}
        """
        response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": metadata_prompt}]
            )
        
        metadata_text = re.sub(r"```(?:json)?\s*(.*?)```", r"\1", response.choices[0].message.content.strip(), flags=re.DOTALL).strip() 
        try:
            return json.loads(metadata_text)
        except Exception:
            return {}

    # Helper function to format parties nicely
    def format_parties(parties):
        if isinstance(parties, list):
            if len(parties) == 2:
                return " and ".join(parties)
            elif len(parties) > 2:
                return ", ".join(parties[:-1]) + ", and " + parties[-1]
            elif len(parties) == 1:
                return "Not specified"
        return parties


    # Helper function to validate metafields
    def validate_metadata_field(field_value, default="Not specified"):
        if not field_value or field_value.strip().lower() in ["", "not specified", "n/a", "none"]:
            return default, False
        return field_value.strip(), True


    # Helper function to build display metadata summary for prompts
    def build_metadata_summary(meta):
        summary_lines = []

        # Contract Type
        contract_type, ct_valid = validate_metadata_field(meta.get("Contract Type"))
        if ct_valid:
            summary_lines.append(f"Contract Type: {contract_type}")

        # Parties Involved (formatted)
        parties_raw, pi_valid = validate_metadata_field(meta.get("Parties Involved"))
        if pi_valid:
            # Convert to list if comma-separated string
            if isinstance(parties_raw, str):
                parties_list = [p.strip() for p in parties_raw.split(",") if p.strip()]
            elif isinstance(parties_raw, list):
                parties_list = parties_raw
            else:
                parties_list = []

            formatted_parties = format_parties(parties_list)
            summary_lines.append(f"Parties Involved: {formatted_parties}")

        # Dates
        effective_date, ed_valid = validate_metadata_field(meta.get("Effective Date"))
        if ed_valid:
            summary_lines.append(f"Effective Date: {effective_date}")

        expiration_date, exd_valid = validate_metadata_field(meta.get("Expiration Date"))
        if exd_valid:
            summary_lines.append(f"Expiration Date: {expiration_date}")

        # Summary
        summary_text, st_valid = validate_metadata_field(meta.get("Summary Text"))
        if st_valid:
            summary_lines.append(f"Summary: {summary_text}")

        if not summary_lines:
            return "Metadata could not be reliably extracted from the contract."
    
        return "\n".join(summary_lines)



    st.set_page_config(layout="wide")

    st.markdown(
        """
        <style>
        .stApp {
            background-color: #003959;
            color: black;
        }
        .block-container {
            background-color: #ecf5ff;
            max-width: 800px;
            margin: auto;
            padding: 30px;
            border-radius: 10px;
        }
        label, .stTextInput label, .stTextArea label {
            color: black !important;
        }
        textarea:disabled, textarea[disabled] {
            cursor: default !important;
            background-color: #00255f !important;
            color: white !important;
            -webkit-text-fill-color: white !important;
            opacity: 1 !important;
        }
        .stButton > button {
            color: white !important;
            background-color: #3a7bd5 !important;
        }
        .stButton > button:hover {
            background-color: #285f9e !important;
        }
        .stButton > button:active {
            background-color: #1d3e66 !important;
        }
        h1, h2, h3, h4, h5, h6 {
            text-align: center !important;
        }
        .centered {
            display: flex;
            justify-content: center;
        }
        .field-a {
            background-color: #2f6acc;
            color:white;
            padding: 5px;
            border-radius: 8px;
        }
 
        div[data-testid="column"] > div {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100px;  /* Adjusted fixed height */
        }

        .stButton > button {
            color: white !important;
            background-color: #3a7bd5 !important;
            height: 80px !important;  /* Same fixed height for all buttons */
            white-space: normal !important;  /* Allows wrapping */
            padding: 10px 15px !important;
            font-weight: 500;
            border-radius: 8px;
        }


        /* Text input and text areas */
        textarea, input[type="text"] {
            background-color: black !important;
            color: white !important;
            border: 1px solid #888 !important;
        }

        textarea::placeholder,
        input::placeholder {
            color: #aaa !important;
        }
    
        /* --- FILE UPLOADER BLACK MODE --- */

        /* Change the label color ("Please upload a PDF document") */
        div[data-testid="stFileUploader"] > label {
            color: #ecf5ff !important;
        }

        /* Style the main dropzone */
        div[data-testid="stFileUploader"] > div > div[data-baseweb="file-uploader"] {
            background-color: #000000 !important; /* Solid black background */
            border-color: #444444 !important;   /* Dark gray for the border */
            border-style: dashed !important;
        }

        /* Use a universal selector (*) to force ALL text elements to be white */
        div[data-testid="stFileUploader"] > div > div[data-baseweb="file-uploader"] * {
            color: #ffffff !important; /* White text for max readability */
        }

        /* Target the specific class for the "Limit..." text */
        .st-emotion-cache-1rpn56r {
            color: white !important;
        }

        /* Style the upload icon (overrides the universal selector for the icon shape) */
        div[data-testid="stFileUploader"] > div > div[data-baseweb="file-uploader"] svg {
            fill: #ffffff !important; /* White icon */
        }

        /* Style the 'Browse files' button */
        div[data-testid="stFileUploader"] button {
            background-color: #333333 !important; /* Dark gray button */
            color: white !important;
            border: 1px solid #555555 !important;
        }

        /* Style the 'Browse files' button on hover */
        div[data-testid="stFileUploader"] button:hover {
            background-color: #555555 !important; /* Lighter gray on hover */
            border-color: #777777 !important;
        }

        /* Style the pill of the uploaded file */
        div[data-testid="stFileUploader"] .st-emotion-cache-1gulkj5 {
            background-color: #333333 !important; /* Dark gray for the file pill */
            color: white !important;
        }

        /* Style the 'X' to remove the uploaded file */
        div[data-testid="stFileUploader"] .st-emotion-cache-1gulkj5 svg {
            fill: white !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Contract Insights Assistant")

    uploaded_file = st.file_uploader("Please upload a PDF document", type="pdf")

    if uploaded_file is not None:
        text = extract_text_from_pdf(uploaded_file)
        metadata = call_openai_for_metadata(text)
        metadata_summary = build_metadata_summary(metadata)

        contract_type, _ = validate_metadata_field(metadata.get("Contract Type", "Not specified"))
        # Handle and format parties involved
        parties_raw = metadata.get("Parties Involved", "Not specified")
        if isinstance(parties_raw, str):
            parties_list = [p.strip() for p in parties_raw.split(",") if p.strip()]
        else:
            parties_list = parties_raw
        parties_involved = format_parties(parties_list)
        effective_date, _ = validate_metadata_field(metadata.get("Effective Date", "Not specified"))
        expiration_date, _ = validate_metadata_field(metadata.get("Expiration Date", "Not specified"))
        summary_text, _ = validate_metadata_field(metadata.get("Summary Text", "Not specified"))

        # Metadata fields display
        st.markdown(f"<div class='field-a'><h3>Contract Type</h3></div>", unsafe_allow_html=True)
        st.markdown(f"{contract_type}", unsafe_allow_html=True)

        st.markdown(f"<div class='field-a'><h3>Parties Involved</h3></div>", unsafe_allow_html=True)
        st.markdown(f"{parties_involved}", unsafe_allow_html=True)

        st.markdown(f"<div class='field-a'><h3>Effective and Expiration Dates</h3></div>", unsafe_allow_html=True)
        dates = f"Effective: {effective_date}\nExpiration: {expiration_date}"
        st.markdown(f"{dates}", unsafe_allow_html=True)

        st.markdown(f"<div class='field-a'><h3>Summary</h3></div>", unsafe_allow_html=True)
        st.markdown(f"{summary_text}", unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        answer = ""
        answer2 = ""
        answer3 = ""
    
        # Quick Actions section
        st.markdown("### Quick Actions")
        col1, col2, col3, col4, col5 = st.columns(5)

        # Button 1
        with col1:
            clicked1 = st.button("Generate Executive Summary", key="btn1")

        # Button 2
        with col2:
            clicked2 = st.button("Extract Clauses", key="btn2")

        # Button 3
        with col3:
            clicked3 = st.button("Simplify Jargon", key="btn3")

        # Button 4
        with col4:
            clicked4 = st.button("Detect Problematic Clauses", key="btn4")

        # Button 5
        with col5:
            clicked5 = st.button("Glossary of Terms", key="btn5")

        # Quick actions code
        if clicked1:
            with st.spinner("Generating executive summary..."):
                prompt = f"""
                Contract Metadata:
                {metadata_summary}
                Full Contract Text:
                {text}
                Task: Provide an executive summary with main purpose, parties involved, key obligations and timelines, termination conditions.
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer2 = response.choices[0].message.content

        if clicked2:
            with st.spinner("Extracting clauses..."):
                prompt = f"""
                Contract Metadata:
                {metadata_summary}
                Full Contract Text:
                {text}
                Task: Extract main clauses like Termination, Confidentiality, Payment Terms, etc.
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer2 = response.choices[0].message.content
                

        if clicked3:
            with st.spinner("Simplifying legal jargon..."):
                    prompt = f"""
                    Contract Metadata:
                    {metadata_summary}
                    Full Contract Text:
                    {text}
                    Task: Identify complex legal terms, jargon, or phrases in the contract that a small business user or someone not well-versed in legal terminology may not readily understand.
                    For each one, please explain it clearly and concisely in plain English.
                    
                    Please format the output as a bullet-point list such as this:
                    - **Term**: Explanation
                    
                    Also, please title the list as "Jargon Explanations"
                    """
                    response = client.chat.completions.create(
                        model="gpt-4o",
                        messages=[{"role":"user", "content": prompt}]
                    )
                    answer2 = response.choices[0].message.content
    

        if clicked4:
            with st.spinner("Scanning for problematic clauses..."):
                prompt = f"""
                Contract Metadata:
                {metadata_summary}
                Full Contract Text:
                {text}
                Task: Identify any clauses or sections that may pose potential risks, unusual obligations, unclear responsibilities, or any concerning legal implications - especially from the perspective of a small business user or someone not well-versed in legal terminology.

                For each one, provide a simple explanation of why it could be a problematic clause.

                Please format the output as a bullet-point list like this:
                - **Clause Name or Description**: Explanation of concern

                Also, please title the list as "Red Flag Clauses"
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role":"user", "content": prompt}]
                )
                answer2 = response.choices[0].message.content


        if clicked5:
            with st.spinner("Generating glossary..."):
                prompt = f"""
                Contract Metadata:
                {metadata_summary}
                Full Contract Text:
                {text}
                Task: Create a glossary of important terms or key concepts used in the contract. For each term, provide a brief and simple definition or explanation that a small business user or someone not well-versed in legal terminology can understand.

                Please format the output as a bullet-point list like this:
                - **Term**: Definition

                Also, please title the list as "Glossary of Terms"
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role":"user", "content": prompt}]
                )
                answer2 = response.choices[0].message.content
    
        # Display the answer if available
        if answer2:
            st.markdown(
                f"""
                <div style="
                    background-color: white;
                    color: black;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid black !important;">
                    {answer2}
                </div>
                """,
                unsafe_allow_html=True
            )

    
        # Question and Answer section
    
        # Question input
        question = st.text_area(
            "",
            placeholder="Please type here to ask a general question about the contract"
        )

        # Button to get answer
        if st.button("Get Answer") and question:
            with st.spinner("Generating answer..."):
                prompt = f"""
                Contract Metadata:
                {metadata_summary}
                Full Contract Text:
                {text}
                Question:
                {question}
                Provide a clear and concise answer.
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content
    
        # Display the answer if available
        if answer:
            st.markdown("### Answer:")
            st.markdown(
                f"""
                <div style="
                    background-color: white;
                    color: black;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid black !important;">
                    {answer}
                </div>
                """,
                unsafe_allow_html=True
            )


        # Modify section
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown("### Modify Contract")
        edit_instruction = st.text_area(
            "",
            placeholder="Please type here to make changes to the contract"
        )
    
        if st.button("Modify Contract"):
            with st.spinner("Applying modifications..."):
                prompt = f"""
                Original Contract:
                {text}

                Instruction:
                {edit_instruction}

                Task: Apply the requested changes directly to the contract text.
                Return only the modified contract.
                """
                response = client.chat.completions.create(
                    model="gpt-4o",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer3 = response.choices[0].message.content  
    
        if answer3:
            st.markdown("### Modified Contract:")
            st.markdown(
                f"""
                <div style="
                    background-color: white;
                    color: black;
                    padding: 15px;
                    border-radius: 8px;
                    border: 1px solid black !important;">
                    {answer3}
                </div>
                """,
                unsafe_allow_html=True
            )
        

        # Feedback section
        st.markdown("<hr>", unsafe_allow_html=True)  
        st.markdown("### Feedback")
        feedback = st.text_area(
            "",
            placeholder="Please type here to share your feedback or report issues", 
            key="feedback_input"
        )

        if st.button("Submit Feedback"):
            if feedback.strip():
                with open("feedback_log.txt", "a", encoding="utf-8") as f:
                    f.write(f"\n---\nTimestamp: {datetime.datetime.now()}\nFeedback: {feedback.strip()}\n")

                st.markdown(
                    """
                    <div style="
                        background-color: #004d00;
                        color: white;
                        padding: 10px;
                        border-radius: 5px;
                        margin-top: 10px;
                        font-weight: bold;
                    ">
                    Thank you for your feedback!
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("Please enter some feedback before submitting.")


    pass
else:
    # If check_password returned False, stop the execution of the main app
    st.stop() 











