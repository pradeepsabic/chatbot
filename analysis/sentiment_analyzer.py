from openai import OpenAI
from loguru import logger

def analyze_sentiment_per_query(query):
    prompt_sentiment_template = f"""Analyze the sentiment of the following query:
    
    "{query}"
    
    Please categorize the sentiment as Positive, Negative, or Neutral. Only respond with the sentiment label.
    """

    # Prepare the messages for the OpenAI API
    messages = [
        {"role": "user", "content": prompt_sentiment_template}
    ]
    
    client = OpenAI()
    
     # Step 4: Call OpenAI's API to perform trend analysis
    try:
        response = client.chat.completions.create(
        model="gpt-4o-mini",  # or other available models
        messages=messages,
        max_tokens=300
    )
        sentiment_response = response.choices[0].message.content.strip()
        logger.info(f"Extracted sentiment: {sentiment_response}")
     
        
        
        return sentiment_response

    except Exception as e:
        logger.error(f"Error during sentiment analysis: {str(e)}")
        return "Unknown"