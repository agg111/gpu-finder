import asyncio
from metorial import Metorial, MetorialOpenAI
from openai import AsyncOpenAI
import os
import dotenv

dotenv.load_dotenv()

metorial= Metorial(api_key=os.getenv("METORIAL_API_KEY"))
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))


async def get_gpu_data():
  messages = [
    {"role": "user", "content": "Find top 5 gpus, their pricing, location and availability information from aws and gcp"}
  ]

  async def session_action(session) -> str:
    for i in range(25):
      response = await openai.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        tools=session["tools"]
      )

      choice = response.choices[0]
      tool_calls = choice.message.tool_calls

      if not tool_calls:
        print(choice.message.content)
        return choice.message.content

      tool_responses = await session["callTools"](tool_calls)

      messages.append({
        "role": "assistant", 
        "tool_calls": choice.message.tool_calls
      })
      messages.extend(tool_responses)

  await metorial.with_provider_session(
    MetorialOpenAI.chat_completions,
    [{"serverDeploymentId": "svd_0mhhcboxk0xiq6KBeSqchw"}],
    session_action
  )