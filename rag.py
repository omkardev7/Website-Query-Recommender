#rag.py
import os
import warnings
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain import PromptTemplate
from langchain.chains import RetrievalQA
from werkzeug.utils import secure_filename

# Load environment variables
load_dotenv()
groq_api_key = os.getenv("GROQ_API_KEY")

# Suppress warnings
warnings.filterwarnings("ignore")

# Paths for PDF storage and vector database
DATA_PATH = 'input_pdfs/'
DB_FAISS_PATH = 'vectorstore/db_faiss'

# Ensure directories exist
os.makedirs(DATA_PATH, exist_ok=True)
os.makedirs(os.path.dirname(DB_FAISS_PATH), exist_ok=True)

class RAGPipeline:
    def __init__(self):
        # Initialize embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'}
        )
        
        # Custom prompt template
        self.prompt_template = """
        You are an expert designed to assist with answering questions related to the Codebuddy 2.0 learning platform, which offers programming courses, software testing tutorials, data structures, algorithms, and additional resources such as articles, blogs, and other educational materials.
        Please refer to the context provided below to answer the question as accurately and specifically as possible. If the answer to the question is not found in the context, respond with: "I couldn't find the answer in the uploaded document."

        Context:
        {context}

        Question: 
        {question}

        Helpful Answer:
        """
        
        self.prompt = PromptTemplate(
            template=self.prompt_template, 
            input_variables=["context", "question"]
        )

    def upload_and_process_pdf(self, file):
        """Process uploaded PDF and create vector store"""
        # Secure filename and save
        filename = secure_filename(file.filename)
        filepath = os.path.join(DATA_PATH, filename)
        file.save(filepath)

        # Load and split PDF
        loader = PyPDFLoader(filepath)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500, 
            chunk_overlap=50
        )
        texts = text_splitter.split_documents(documents)

        # Create vector store
        db = FAISS.from_documents(texts, self.embeddings)
        db.save_local(DB_FAISS_PATH)

        return filename

    def create_qa_chain(self):
        """Create Question Answering Chain"""
        # Load vector store
        db = FAISS.load_local(
            DB_FAISS_PATH, 
            self.embeddings, 
            allow_dangerous_deserialization=True
        )

        # Initialize LLM
        llm = ChatGroq(
            temperature=0.4, 
            model_name="llama3-8b-8192", 
            groq_api_key=groq_api_key
        )

        # Create QA Chain
        qa_chain = RetrievalQA.from_chain_type(
            llm=llm,
            chain_type='stuff',
            retriever=db.as_retriever(
                search_type="similarity_score_threshold", 
                search_kwargs={"score_threshold": 0.3, "k": 4}
            ),
            chain_type_kwargs={"prompt": self.prompt},
            return_source_documents=True
        )

        return qa_chain

    def search_pdf(self, query):
        """Search and retrieve answer from PDF"""
        try:
            # Create QA chain
            qa_chain = self.create_qa_chain()
            
            # Get response
            response = qa_chain({"query": query})
            print("LLM Response:", response)
            
            return {
                "response": response['result'],
                "sources": [doc.page_content for doc in response.get('source_documents', [])]
            }
        except Exception as e:
            return {"error": str(e)}

# Global RAG pipeline instance
rag_pipeline = RAGPipeline()