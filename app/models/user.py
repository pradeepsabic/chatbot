# Pydantic Models-This file defines the data model for incoming requests.
from pydantic import BaseModel

class UserInput(BaseModel):
    query: str