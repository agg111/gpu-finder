import asyncio
from config import metorial, openai, MetorialOpenAI


async def get_gpu_data() -> str:
  """
  Fetch GPU availability and pricing information from AWS and GCP.
  
  Returns:
    str: GPU data containing top GPUs with pricing, location, and availability info
  """
  messages = [
    {"role": "user", "content": "Find top 5 gpus, their pricing, location and availability information from aws and gcp"}
  ]
  
  result = None

  async def session_action(session) -> str:
    nonlocal result
    for i in range(25):
      response = await openai.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        tools=session["tools"]
      )

      choice = response.choices[0]
      tool_calls = choice.message.tool_calls

      if not tool_calls:
        content = choice.message.content
        print(f"GPU data retrieved: {content[:200]}...")  # Print preview
        result = content
        return content

      tool_responses = await session["callTools"](tool_calls)

      messages.append({
        "role": "assistant",
        "tool_calls": choice.message.tool_calls
      })
      messages.extend(tool_responses)
    
    # Fallback if loop completes without returning
    return result or "No GPU data retrieved"

  await metorial.with_provider_session(
    MetorialOpenAI.chat_completions,
    [{"serverDeploymentId": "svd_0mhhcboxk0xiq6KBeSqchw"}],
    session_action
  )
  
  return result or "No GPU data retrieved"