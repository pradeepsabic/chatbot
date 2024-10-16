# API Route Handler-This handles the API endpoint for user interactions.
from fastapi import APIRouter
from app.models.user import UserInput
from app.services.chatbot_service import load_and_preprocess_pdf, setup_vector_store, get_chatbot_response
from fastapi import APIRouter,HTTPException
from contextlib import asynccontextmanager
from loguru import logger
from ticketing.service_now import log_ticket_in_service_now # for logging ticket in ticketing system (servicenow)

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
        ticket_status = None # for service now
        ticket_number = None # for service now

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
        
        # Get the chatbot response and intent also
        response,intent,sentiment   = get_chatbot_response(query, retriever) 
        #here response,intent,sentiment,extracted_info we can have extracted info 
        
        # If it's a complaint or high-priority issue, log a ticket
        #if intent == "complaint": #or extracted_info.get("priority", "").lower() == "high":
            #ticket_number = log_ticket_in_service_now(extracted_info)
        #if ticket_number:
            #ticket_status = f"Ticket logged successfully with Ticket Number: {ticket_number}"
        #else:
            #ticket_status = "Failed to log the ticket."
            
        if not response or not intent:
            raise HTTPException(status_code=500, detail="Response or intent generation failed.")
        
        logger.info(f"Chatbot Response in chat_router.py: {response}, Intent: {intent}")

        follow_up_message = "\n\nHope you are satisfied with the answer. Do you have any other queries?"
        
        # Append the follow-up message only if the intent is not a greeting, farewell, or fallback for this we have passed 
        #Assistant's intent: in prompt & calling function to get the intention extract_intent(response: str)
        if intent not in ["greeting", "farewell", "fallback", "complaint"]:
            response += follow_up_message
            
        # Return the final response object with all details
        return {
            "response": response,
            "intent": intent,
            "sentiment": sentiment,
            "query": query
        }
        #in return add ticket status and ticekt number also
        #"ticket_status": ticket_status, 
        #"ticket_number": ticket_number
    
    except Exception as ex:
        logger.error(f"Error processing request: {str(ex)}")
        raise HTTPException(status_code=422, detail=str(ex))
