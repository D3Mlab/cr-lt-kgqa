from openai import OpenAI
from dotenv import load_dotenv
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
)

load_dotenv()
client = OpenAI()

class LLM:

    @retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(6))
    def __call__(self, messages, model="gpt-3.5-turbo-1106"):
        completion = client.chat.completions.create(
            model=model, messages=messages)

        return completion.choices[0].message