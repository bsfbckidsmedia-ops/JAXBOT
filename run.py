import asyncio
from aiavatar import AIAvatar

aiavatar_app = AIAvatar(
    openai_api_key="sRwI3y0lRYO5WwYckWkleKBIV4Fi3wvO",  # Replace with your Mistral API key
    base_url="https://api.mistral.ai/v1",  # Mistral AI API endpoint
    model="mistral-large-latest",  # Use Mistral's model
    debug=True
)
asyncio.run(aiavatar_app.start_listening())