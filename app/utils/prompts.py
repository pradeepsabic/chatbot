# Define the prompt for intent detection and response generation
def create_intent_response_prompt(query):
    prompt = f"""
    The following is a conversation between a user and an assistant. 
    The assistant should first determine the user's intent based on their message 
    and then provide an appropriate response.

    User's message: "{query}"

    Assistant's intent: (greeting, farewell, question, complaint, feedback, fallback)

    Assistant's response:
    """
    return prompt

# Define the prompt for intent detection, response generation, and information extraction
def create_intent_response_infoextraction_prompt(query):
    prompt = f"""
    The following is a conversation between a user and an assistant.
    The assistant should first determine the user's intent based on their message,
    extract relevant information like name, issue description, and priority (if any),
    and then provide an appropriate response.

    User's message: "{query}"

    Assistant's intent: (greeting, farewell, question, complaint, feedback, fallback)
    Extracted information (name, issue description, priority):
    Assistant's response:
    """
    return prompt

# Function to get the appropriate prompt
def get_chatbot_prompt(query):
    return create_intent_response_infoextraction_prompt(query)
