# This file handles loading PDFs, chunking, embedding, and querying ChromaDB. (Business Logic)
from langchain_community.document_loaders import PyPDFLoader
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.chains import RetrievalQA
from langchain_openai import ChatOpenAI
from langchain.chains.question_answering import load_qa_chain
from app.utils.text_utils import clean_text,chunk_text #from text_utils.py
import os
from fastapi import HTTPException
from loguru import logger

# Load PDF and preprocess here we call our method from text_utils chunk_text
def load_and_preprocess_pdf(pdf_path:str):
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"File path {pdf_path} does not exist")
        
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        processed_chunks = chunk_text(documents)
        return processed_chunks
    
    except ValueError as ve:
        raise HTTPException(status_code=422, detail=str(ve))

    # Catching any other errors, like FileNotFoundError
    except FileNotFoundError as fnf_error:
        raise HTTPException(status_code=404, detail=str(fnf_error))
    
    
# Embedding and Retrieval using ChromaDB
def setup_vector_store(processed_chunks):
    logger.info("Inside setup_vector_store")
    
    if not processed_chunks:
        raise ValueError("Processed chunks cannot be empty.")
    
    try:
        # Initialize embeddings
        embeddings = OpenAIEmbeddings()  
        
        # Create vector store from processed chunks
        vector_store = Chroma.from_texts(processed_chunks, embeddings)  
        
        if not vector_store:
            raise ValueError("Failed to create vector store.")
        
        # Create a retriever from the vector store
        retriever = vector_store.as_retriever()
        
        if not retriever:
            raise ValueError("Failed to create a valid retriever.")
        
        logger.info("Vector store and retriever successfully created.")
        return retriever
    
    except ValueError as ve:
        logger.error(f"ValueError: {str(ve)}")
        raise HTTPException(status_code=422, detail=str(ve))

    except Exception as e:
        logger.error(f"Unexpected error in vector store setup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error in vector store setup: {str(e)}")

# Chatbot response using LangChain's RetrievalQA
def get_chatbot_response(query: str, retriever):
    try:
        llm = ChatOpenAI()
        qa_chain = RetrievalQA.from_llm(llm=llm, retriever=retriever)
        response = qa_chain.invoke(query)
        answer_text = response['result']
        formatted_response = answer_text.replace("\\n", "\n")
        return formatted_response #response['result']  # Format the response as needed
    
    # Catching any errors related to invalid query processing
    except ValueError as ve:
        raise HTTPException (status_code=422,detail=ve)
    
    # Catching any issues related to the retriever or model
    except KeyError  as ke:
       raise HTTPException(status_code=500, detail=f"Response formatting error: {str(ke)}")
    # Catching any other general exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
