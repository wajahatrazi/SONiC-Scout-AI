import os
import openai
import streamlit as st
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain.chains import RetrievalQA
from datetime import datetime
import logging
 
openai_api_key = st.secrets["OPENAI_API_KEY"]
openai.api_key = openai_api_key

 
# Initialize logging for error tracking
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')
 
# Load FAISS vector store
def load_vector_store():
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        return vector_store
    except Exception as e:
        logging.error("Error loading vector store: %s", e)
        st.error("There was an issue loading the knowledge base.")
        return None
 

vector_store = load_vector_store()
sonic_model = ChatOpenAI(model="gpt-4o", temperature=0.5)
 
 
# Prompt template for context-based responses
prompt_template = """
You are SONiC Scout, a knowledgeable, friendly, and supportive assistant for both SONiC Network Engineers and newcomers. When responding to user queries, ensure the following:
1. Provide answers in a clear, structured, and easy-to-understand manner.
2. Maintain a warm, approachable tone, especially for users who are new to SONiC.
3. If unsure about the answer, openly acknowledge your limitations and provide guidance or direct them to alternative resources as best as you can.
 
Context:
{context}
 
<user_query> {question} </user_query>
 
<chain_of_thought>
- Carefully analyze the user's question to understand their intent.
- Determine whether the question is relevant to SONiC, the provided context, or the current domain (such as SONiC configuration, architecture, troubleshooting, etc.).
- If the question is irrelevant to SONiC or the current context, acknowledge that the assistant is still learning and politely inform the user that it cannot provide
an answer outside the given scope.
- If the question is about SONiC or related to the context, break it down into key components and think through each part logically.
- If the answer involves multiple points or steps, organize the response into bullet points or numbered steps.
</chain_of_thought>
 
<analysis>
- Analyze the relevance of the user's question and check if it fits within the provided context or if it's related to SONiC technologies.
- If the question is about SONiC or the context, proceed with generating a structured, clear, and actionable answer.
- If the question is irrelevant, prepare a response that politely explains the assistant's limitations and provides guidance.
</analysis>
 
<output_response>
- If the question is relevant, start with a concise summary of the answer, keeping it brief and to the point.
- For complex questions, provide clear and actionable steps or information in bullet points or numbered steps for clarity and structure.
- For simple questions, provide a direct and brief response without unnecessary complexity.
- If the question is irrelevant or out of scope, say: "I'm still learning, but I’m here to help as best I can! It seems like your question isn’t within the scope of SONiC
or the current context, but I encourage you to explore other resources or rephrase your query related to SONiC."
- Ensure that the answer is actionable and helps the user proceed with the next steps or understanding.
</output_response>
"""
 
# Set up the RetrievalQA chain
prompt = PromptTemplate(template=prompt_template, input_variables=["context", "question"])
 
qa_chain = RetrievalQA.from_chain_type(
    llm=sonic_model,
    chain_type="stuff",
    retriever=vector_store.as_retriever() if vector_store else None,
    chain_type_kwargs={"prompt": prompt}
)
 
# Retrieve response based on user query
def get_sonic_scout_response(query):
    try:
        user_input_embedding = vector_store.embeddings.embed_query(query)
        docs = vector_store.similarity_search_by_vector(user_input_embedding, k=5)  # Reduce chunks to 5
 
        if not docs:
            return "I’m still learning, but I’m here to help as best I can!"
 
        context = "\n".join([doc.page_content for doc in docs])
        response = qa_chain.invoke({"query": query, "context": context})
 
        # Extract only the answer section from the response
        answer = response.get("result", "I couldn't find an answer.")
        
        # You can process the response to only return the final answer if needed
        # For example, extracting the part after "<answer>" tag
        start = answer.find('<answer>') + len('<answer>')
        end = answer.find('</answer>')
 
        if start != -1 and end != -1:
            final_answer = answer[start:end].strip()
        else:
            final_answer = answer.strip()
 
        return final_answer
    except Exception as e:
        logging.warning("Issue with response generation: %s", e)
        return "I’m experiencing a technical issue right now."
 
 

st.set_page_config(
    page_title="SONiC Scout",
    page_icon="assets/sonic_logo.png",  # Path to the SONiC logo
    layout="centered",
    initial_sidebar_state="expanded"
)
 
st.title("SONiC Scout")
st.write("Welcome to SONiC Scout – your go-to assistant for all things SONiC, developed by xFlow Engineers!")
 
# Initialize session state for message history
if 'messages' not in st.session_state:
    st.session_state.messages = []
    st.session_state.session_title = f"Session {len(st.session_state.messages) + 1}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
 
# Sidebar implementation
with st.sidebar:
    # Title and Logos
    st.image(["assets/sonic_logo.png"], width=80)
    st.markdown("<h2 style='text-align: left; color: #004aad;'>SONiC Scout</h2>", unsafe_allow_html=True)
 
    # Description
    st.markdown("""
        <div style="text-align: left-align; font-size: 14px; color: #333333;">
            <strong>SONiC Scout</strong> is an interactive platform designed to support both seasoned SONiC engineers
            and newcomers in navigating the SONiC ecosystem. It provides quick access to SONiC's Command Line Interface,
            architecture insights, release schedules, installation guides, community contribution tips, and in-depth
            details about SONiC's core components, including key containers like SWSS, Build Image, YANG, Utilities, and more.
        </div>
        """, unsafe_allow_html=True)
 
    # Divider
    st.markdown("---")
 
    # Clear Chat Button
    if st.button("Clear Chat"):
        st.session_state.messages = []  # Clear chat history
 
    # Divider
    st.markdown("---")
 
    # Footer with built by and LinkedIn link
    st.markdown("""
        <div style="text-align: center; font-size: 13px; color: #555;">
            Developed by
            <a href="https://pk.linkedin.com/company/xflow-research-inc" target="_blank" style="color: #0073e6; text-decoration: none;">
            <strong>SONiC xFlow Engineers</strong></a>
        </div>
        <div style="text-align: center; font-size: 12px; color: #888; margin-top: 5px;">
            ©  <a href="https://pk.linkedin.com/company/xflow-research-inc" target="_blank" style="color: #0073e6; text-decoration: none;">xFlow Research Inc
        </div>
        """, unsafe_allow_html=True)
 
# Add custom CSS for styling
st.markdown("""
    <style>
        /* Sidebar styling */
        .sidebar .sidebar-content {
            padding: 1.5rem;
            background-color: white;
            border-radius: 0.75rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
            margin: 1rem 0;
        }
        
        /* Title styling */
        .sidebar .title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        /* Description styling */
        .sidebar .description {
            font-size: 0.875rem;
            color: #666;
            margin-bottom: 1.5rem;
            line-height: 1.5;
        }
        
        /* Built by section styling */
        .built-by {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            font-size: 0.9rem;
            color: #666;
        }
        
        .built-by strong {
            color: #2196F3;
            display: block;
            margin-top: 0.5rem;
        }
        
        /* Social links styling */
        .social-links {
            text-align: center;
            margin-top: 1rem;
        }
        
        .social-links a {
            display: inline-block;
            padding: 0.5rem 1.5rem;
            border: 1px solid #2196F3;
            border-radius: 9999px;
            color: #2196F3;
            text-decoration: none;
            font-size: 0.875rem;
            transition: all 0.3s ease;
        }
        
        .social-links a:hover {
            background-color: #2196F3;
            color: white;
        }
        
        /* Clear Chat button styling */
        .stButton > button {
            width: 100%;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 0.5rem;
            color: #666;
            font-weight: 500;
            padding: 0.5rem 1rem;
            transition: all 0.3s ease;
        }
        
        .stButton > button:hover {
            background-color: #e9ecef;
            border-color: #dee2e6;
            color: #333;
        }
        
        /* Logo styling */
        img {
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
        }
        
        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Footer link styling */
        .footer {
            text-align: center;
            margin-top: 2rem;
            padding-top: 1rem;
            border-top: 1px solid #eee;
            font-size: 0.8rem;
            color: #666;
        }
        
        .footer a {
            color: #2196F3;
            text-decoration: none;
        }
        
        /* Main content area styling */
        .main {
            padding: 2rem;
            max-width: 1200px;
            margin: 0 auto;
        }
    </style>
""", unsafe_allow_html=True)
 
# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["message"])
 
# User input processing
if prompt := st.chat_input("Ask your question about SONiC:"):
    st.session_state.messages.append({"role": "user", "message": prompt})
    st.chat_message("user").write(prompt)
 
    with st.spinner("Thinking..."):
        response = get_sonic_scout_response(prompt)
 
    st.chat_message("assistant").write(response)
    st.session_state.messages.append({"role": "assistant", "message": response})
