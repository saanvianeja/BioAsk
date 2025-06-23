import streamlit as st
from openai import OpenAI
import re
import time
import subprocess

# --- App Configuration ---
st.set_page_config(
    page_title="BioAsk",
    page_icon="🧬",
    layout="wide"
)

# --- LLM Client Initialization ---
# Initialize the OpenAI client to connect to the local LLM server
try:
    local_llm_url = st.secrets["LOCAL_LLM_URL"]
    client = OpenAI(
        base_url=local_llm_url,
        api_key="not-needed"  # API key is not needed for local LLMs
    )
except KeyError:
    st.error("LOCAL_LLM_URL not found in secrets.toml. Please add it to connect to your local LLM.")
    st.stop()

# --- Detect available Ollama models ---
def get_first_ollama_model():
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        for line in result.stdout.splitlines():
            if line.strip() and not line.startswith("NAME"):
                return line.split()[0]
    except Exception:
        pass
    return "llama3"  # fallback default

# --- State Management ---
# Initialize session state variables to preserve them across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []
if "response_data" not in st.session_state:
    st.session_state.response_data = None


# --- Helper Functions ---
def parse_llm_response(response_content):
    """
    Parses the structured response from the LLM into a dictionary.
    """
    parsed_data = {
        "answer": "Sorry, I couldn't find a direct answer. Please try rephrasing.",
        "confidence": "0%",
        "topics": []
    }
    
    answer_match = re.search(r"## Answer\s*\n(.*?)(?=\n##|$)", response_content, re.DOTALL)
    if answer_match:
        parsed_data["answer"] = answer_match.group(1).strip()

    confidence_match = re.search(r"## Confidence Score\s*\n(.*?)(?=\n##|$)", response_content, re.DOTALL)
    if confidence_match:
        parsed_data["confidence"] = confidence_match.group(1).strip()

    topics_match = re.search(r"## Related Topics\s*\n(.*)", response_content, re.DOTALL)
    if topics_match:
        topics_list = topics_match.group(1).strip().split('\n')
        parsed_data["topics"] = [topic.strip("- ").strip() for topic in topics_list if topic.strip()]
        
    return parsed_data

def is_diagram_request(question):
    """
    Checks if the user's question is asking for a diagram.
    """
    diagram_keywords = ["diagram", "draw", "chart", "graph", "visualize", "figure"]
    return any(keyword in question.lower() for keyword in diagram_keywords)

# --- UI Rendering ---
st.title("🧬 BioAsk: Your Interactive Biology Q&A Assistant")
st.write(
    "Welcome to BioAsk! Ask any biology question, and I'll help you understand the concept."
)

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Automatically detect the first available model
    detected_model = get_first_ollama_model()
    model_name = st.text_input(
        "Enter the local model name",
        detected_model,
        help="The name of the model you have downloaded in Ollama (e.g., 'llama3', 'mistral')."
    )

    # Dropdown for selecting the expertise level
    explain_level = st.selectbox(
        "Explain it Like I'm...",
        ("a Middle School Student", "a High School Student", "an Undergraduate"),
        index=1  # Default to High School Student
    )

    st.info(f"Connected to local LLM at: `{local_llm_url}`")

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Main App Logic ---

# Get user input
user_question = st.chat_input("Ask your biology question here...")

if user_question:
    # Add user question to chat history
    st.session_state.messages.append({"role": "user", "content": user_question})
    
    # Display user question in chat message container
    with st.chat_message("user"):
        st.markdown(user_question)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        
        try:
            system_prompt = (
                f"You are a helpful biology assistant. Explain the concepts clearly for {explain_level}. "
                "Your response MUST be structured with the following markdown headings: "
                "## Answer, ## Confidence Score, ## Related Topics. "
                "For the Confidence Score, provide a percentage (e.g., 95%). "
                "For Related Topics, provide a bulleted list."
            )

            response_stream = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                stream=True
            )

            # Stream the response to the UI
            full_response_content = ""
            for chunk in response_stream:
                if chunk.choices[0].delta.content:
                    full_response_content += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response_content + "▌")
            
            message_placeholder.markdown(full_response_content)
            st.session_state.messages.append({"role": "assistant", "content": full_response_content})

            # Parse and display the structured data
            response_data = parse_llm_response(full_response_content)
            
            if response_data:
                st.divider()
                st.metric(label="Confidence Score", value=response_data["confidence"])
                if response_data["topics"]:
                    st.subheader("Related Topics to Explore")
                    for topic in response_data["topics"]:
                        st.button(topic)
        except Exception as e:
            st.error(f"An error occurred while communicating with the LLM: {e}")
            st.session_state.messages.append({"role": "assistant", "content": f"Error: {e}"}) 