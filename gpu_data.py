import asyncio
import nivara as nv
from datetime import datetime, timezone
from config import metorial, openai, MetorialOpenAI


async def get_gpu_data() -> str:
  """
  Fetch GPU availability and pricing information from AWS and GCP.
  For aws gpus, refer - https://docs.aws.amazon.com/dlami/latest/devguide/gpu.html
  For gcp gpus, refer - https://cloud.google.com/compute/gpus-pricing?hl=en
  
  Returns:
    str: GPU data containing top GPUs with pricing, location, and availability info
  """
  messages = [
    {"role": "user", "content": "Find top 5 gpus, their pricing, location and availability information from aws and gcp"}
  ]
  
  result = None
  total_input_tokens = 0
  total_output_tokens = 0

  async def session_action(session) -> str:
    nonlocal result, total_input_tokens, total_output_tokens
    for i in range(25):
      response = await openai.chat.completions.create(
        messages=messages,
        model="gpt-4o",
        tools=session["tools"]
      )

      # Track token usage from OpenAI response
      if hasattr(response, 'usage'):
        total_input_tokens += response.usage.prompt_tokens if response.usage.prompt_tokens else 0
        total_output_tokens += response.usage.completion_tokens if response.usage.completion_tokens else 0

      choice = response.choices[0]
      tool_calls = choice.message.tool_calls

      if not tool_calls:
        content = choice.message.content
        # print(f"GPU data retrieved: {content[:200]}...")  # Print preview
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
  
  # Record metrics for GPU data retrieval
  try:
    nv.record(
      metric="gpu.finder.gpu_data",
      ts=datetime.now(timezone.utc),
      input_tokens=total_input_tokens if total_input_tokens > 0 else len(str(messages)) // 4,
      output_tokens=total_output_tokens if total_output_tokens > 0 else len(result or "") // 4,
    )
  except Exception as e:
    # Non-blocking: log but don't fail workflow if metrics fail
    print(f"Warning: Failed to record metrics for gpu_data: {e}")
  
  return result or "No GPU data retrieved"