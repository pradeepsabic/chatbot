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
from database.db_manager import DBManager  #to store query in sql server
from analysis.sentiment_analyzer import  analyze_sentiment_per_query #for sentiment analysis 

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
        
        # Define the prompt for intent detection and response generation
        prompt = f"""
        The following is a conversation between a user and an assistant. 
        The assistant should first determine the user's intent based on their message 
        and then provide an appropriate response.

        User's message: "{query}"
        
        Assistant's intent: (greeting, farewell, question, complaint, feedback, fallback)

        Assistant's response:
        """
        response = qa_chain.invoke(prompt)
        answer_text = response['result']
        
        
        logger.info("answer_text from  chatbot_service after invoking qa_chain")
        logger.info(answer_text)
        # Extract the assistant's intent from the model's response
        if "Assistant's intent:" in answer_text:
            intent = extract_intent(answer_text)
        else:
            intent = "general"
        
        #finding sentiment of query
        # Step 2: Perform sentiment analysis
        sentiment = analyze_sentiment_per_query(query)
    
        # Save the query and intent and sentiment to the database
        
        logger.info("before hitting db")
        db_manager = DBManager() 
        db_manager.save_query_to_db(query, intent,sentiment)
        logger.info("after hitting db")
        
        
        formatted_response = answer_text.replace("\\n", "\n")
        
         # Check for fallback condition- chatbot do not understand you and fall to understand
        if "I don't understand" in formatted_response or "Can you rephrase" in formatted_response:
            return "I'm sorry, but I didn't quite understand that. Can you please rephrase your question?"
               
        return formatted_response,intent,sentiment #response['result']  # Format the response as needed
    
    # Catching any errors related to invalid query processing
    except ValueError as ve:
        logger.error(f"ValueError in get_chatbot_response: {str(ve)}")
        raise HTTPException (status_code=422,detail=ve)
    
    # Catching any issues related to the retriever or model
    except KeyError  as ke:
       logger.error(f"keyerror in get_chatbot_response: {str(ve)}")
       raise HTTPException(status_code=500, detail=f"Response formatting error: {str(ke)}")
    # Catching any other general exceptions
    except Exception as e:
        logger.error(f"Unexpected error in get_chatbot_response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")
    
# Function to extract the detected intent from the model's response
def extract_intent(response: str) -> str:
    intent_line = [line for line in response.split("\n") if "Assistant's intent:" in line]
    if intent_line:
        intent = intent_line[0].split(":")[1].strip().lower()
        if intent in ["greeting", "farewell", "question", "complaint", "feedback", "fallback"]:
            return intent
        else:
            return "general"
    return "general"

