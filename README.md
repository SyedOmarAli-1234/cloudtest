# AI-Powered Agreement Assistant

An intelligent web application designed to help non-expert users, such as small business owners and professionals, understand, analyze, and modify legal contracts with ease. This tool leverages the power of OpenAI's GPT-4o to provide instant insights, saving users time and reducing the costs associated with legal consultations.

## Features

* **Automated Metadata Extraction:** Instantly pulls key details from any uploaded PDF contract, including Contract Type, Parties Involved, Effective/Expiration Dates, and a brief Summary.
* **One-Click Analysis Tools:** A suite of "Quick Actions" to:
    * **Generate Executive Summary:** Get a high-level overview of the contract's purpose and obligations.
    * **Extract Key Clauses:** Isolate important sections like Confidentiality, Termination, or Payment Terms.
    * **Simplify Legal Jargon:** Translate complex legal terms into plain, easy-to-understand English.
    * **Detect Problematic Clauses:** Flag potentially risky or one-sided provisions.
    * **Create a Glossary:** Define key terms used throughout the document.
* **Interactive Q&A:** Ask any specific question about the contract in natural language and receive a direct, context-aware answer.
* **Smart Contract Modification:** Request changes or edits to the contract using simple instructions (e.g., "Change the notice period to 30 days"), and the AI will rewrite the relevant clauses.

## Technology Stack

* **Backend:** Python
* **Web Framework:** Streamlit
* **AI & NLP:** OpenAI GPT-4o API
* **PDF Parsing:** PyMuPDF (`fitz`)

## Setup and Installation

Follow these steps to set up and run the project on your local machine.

### 1. Prerequisites

* Python 3.9 or higher installed on your system.
* An OpenAI API key. You can get one from the [OpenAI Platform](https://platform.openai.com/).

### 2. Clone the Repository

Clone this repository to your local machine using your preferred method (HTTPS or SSH).
```bash
git clone [https://github.com/your-username/your-repository-name.git](https://github.com/your-username/your-repository-name.git)
cd your-repository-name
```

### 3. Create a Virtual Environment (Recommended)

It's best practice to create a virtual environment to manage project dependencies.
```bash
# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

Create a `requirements.txt` file with the following content:
```
streamlit
openai
PyMuPDF
```
Then, install all the required libraries using pip:
```bash
pip install -r requirements.txt
```

### 5. Configure API Key

The application needs your OpenAI API key to function. You can set it directly in the `app.py` file.

**Important:** For better security, it is highly recommended to use environment variables to store your API key instead of hardcoding it.

In your `app.py` file, find this line:
```python
client = OpenAI(api_key="sk-...")
```
And replace `"sk-..."` with your actual OpenAI API key.

## How to Run the Application

Once you have completed the setup, you can run the application with a single command from your terminal.

1.  Make sure you are in the project's root directory.
2.  Ensure your virtual environment is activated.
3.  Run the following command:
    ```bash
    streamlit run app.py
    ```
4.  Your web browser should automatically open a new tab with the running application. If not, the terminal will provide a local URL (usually `http://localhost:8501`) that you can navigate to.

## Usage

1.  **Upload a PDF:** Use the file uploader at the top of the page to select a legal contract in PDF format.
2.  **View Automated Analysis:** Once uploaded, the application will automatically display the extracted metadata.
3.  **Use Quick Actions:** Click any of the "Quick Actions" buttons to perform a deeper analysis. The results will appear below the buttons.
4.  **Ask Questions:** Type any question into the Q&A text box and click "Get Answer."
5.  **Modify the Contract:** Use the "Modify Contract" section to request changes to the document.

## Contact

Syed Omar Ali
Email: `omar@aliandfamily.com` | `soa443@student.bham.ac.uk`