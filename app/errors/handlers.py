#gloabl exception handling no need to call this 
from fastapi import FastAPI, Request
from loguru import logger
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import traceback  # For traceback logging

app = FastAPI()

# Setup Loguru logger to log errors to a file
logger.add("logs/error.log", level="ERROR")


# 1. Handle Starlette HTTP Exceptions (e.g., 404 Not Found, 403 Forbidden, etc.)
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.error(f"HTTP error: {exc.detail} at {request.url}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


# 2. Handle Request Validation Errors (e.g., data validation errors, wrong types, etc.)
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extract request body (in case of malformed JSON, it might not be valid JSON, so fetch raw)
    #body = await request.body()  # Fetch the raw body data
    body = await request.json()
    
    # Log full validation error including request URL, body, and error details
    logger.error(f"Validation error at {request.url}: {exc.errors()} - Raw Body: {body.decode('utf-8')}")
    
    return JSONResponse(
        status_code=422,
        content={
            "message": "Validation error",
            "details": exc.errors()
        },
    )


# 3. Handle Custom Application-Specific Exceptions
class CustomException(Exception):
    def __init__(self, name: str):
        self.name = name

@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error(f"Custom error at {request.url}: {exc.name}")
    return JSONResponse(
        status_code=400,
        content={"message": f"Custom error: {exc.name}"},
    )


# 4. Handle General Exceptions (Catches everything else) with traceback
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Log the full traceback for detailed debugging
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Log the error message and the URL where it happened
    logger.exception(f"Unexpected error at {request.url}: {exc}")
    
    return JSONResponse(
        status_code=500,
        content={"message": "An internal error occurred. Please try again later."},
    )


# Sample route to test different exceptions
@app.get("/cause_error")
def cause_error(error_type: str):
    if error_type == "http":
        raise StarletteHTTPException(status_code=404, detail="This resource was not found")
    elif error_type == "validation":
        raise RequestValidationError([{"loc": ["query", "param"], "msg": "Invalid value", "type": "value_error"}])
    elif error_type == "custom":
        raise CustomException("Something custom went wrong")
    else:
        raise Exception("Generic error occurred")
