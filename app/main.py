#first file which will run This file initializes your FastAPI app and includes the routers.
from fastapi import FastAPI
import uvicorn
from app.routers import chat_router
from app.errors import handlers #global exception handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.exceptions import RequestValidationError 


app = FastAPI()

# Register the exception handlers
app.add_exception_handler(StarletteHTTPException, handlers.http_exception_handler)
app.add_exception_handler(RequestValidationError, handlers.validation_exception_handler)
app.add_exception_handler(Exception, handlers.global_exception_handler)

# Include the chat-related routes
app.include_router(chat_router.router)

@app.get("/")
def read_root():
       return {"message": "Welcome to the Chatbot API"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='0.0.0.0', port=8000)
