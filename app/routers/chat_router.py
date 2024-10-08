# API Route Handler-This handles the API endpoint for user interactions.
from fastapi import APIRouter
from app.models.user import UserInput
from app.services.chatbot_service import load_and_preprocess_pdf, setup_vector_store, get_chatbot_response
from fastapi import APIRouter,HTTPException
from contextlib import asynccontextmanager
from loguru import logger

router = APIRouter()

# Global variable for the retriever
retriever = None

# Specify the path to your PDF file
pdf_path = 'Docs//userguidesamsunggalaxys7.pdf'  # Use forward slashes

def load_pdf():
    global retriever
    try:
        logger.info(f"Processing PDF: {pdf_path}")
        processed_chunks = load_and_preprocess_pdf(pdf_path)
        logger.info("processed chunks done.")
        
        if processed_chunks:
            retriever = setup_vector_store(processed_chunks)
            logger.info("setup_vector_store call-PDF processed and vector store set up.")
        else:
            logger.warning("No processed chunks found in the PDF.")
    
    except Exception as ex:
        logger.error(f"Error loading PDF: {str(ex)}")
        retriever = None  # Ensure retriever is None on error

# Call the function to load the PDF at startup
load_pdf()

@router.post("/chat")
def chat_with_bot(user_input: UserInput):
    global retriever
    
    if retriever is None:
        # If retriever is not set, raise an error and do not attempt to load the PDF again
        raise HTTPException(status_code=400, detail="No documents have been processed. Please check the PDF files in the directory.")
    
    try:
        logger.info(f"User input received: {user_input.query}")
        query = user_input.query
        
        # Get the chatbot response
        response = get_chatbot_response(query, retriever)
        if not response:
            raise HTTPException(status_code=500, detail="No response generated.")
        
        follow_up_message = "\n\nHope you are satisfied with the answer. Do you have any other queries?"
        return {"response": response + follow_up_message}
    
    except Exception as ex:
        logger.error(f"Error processing request: {str(ex)}")
        raise HTTPException(status_code=422, detail=str(ex))
