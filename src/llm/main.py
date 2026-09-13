import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client=OpenAI(base_url=os.getenv("base_url"),api_key=os.getenv("api_key"))

response=client.chat.completions.create(model="google/gemma-4-26b-a4b-it:free",messages=[{"role":"user","content":"Reply with exactly the word ready"}])

print(response.choices[0].message.content)