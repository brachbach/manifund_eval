from anthropic import AsyncAnthropic
from dotenv import load_dotenv
import os

load_dotenv()

client = AsyncAnthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY"),  # This is the default and can be omitted
)

async def call_claude_3_7(prompt: str):
    # breakpoint()
    response = await client.messages.create(
        model="claude-3-7-sonnet-20250219",
        max_tokens=9999,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(response)
    return response