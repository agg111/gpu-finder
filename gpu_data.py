import asyncio
import nivara as nv
from datetime import datetime, timezone
from config import metorial, openai, MetorialOpenAI
from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

client = OpenAI(
    base_url="https://api.runcaptain.com/v1",
    api_key=os.getenv("CAPTAIN_API_KEY"),
    default_headers={
        "X-Organization-ID": os.getenv("CAPTAIN_ORG_ID")
    }
)

async def get_gpu_data() -> str:
  """
  Fetch detailed GPU availability and pricing information from AWS and GCP.

  Returns:
    str: Structured GPU data with actual pricing, availability, and location details
  """
  print("[GPU Data] ⚠️  Fetching REAL data from AWS/GCP (this may take 60+ seconds)...")
  print("[GPU Data] 🌐 Initializing Metorial web search...")
  detailed_prompt = """Get current AWS and GCP GPU pricing from:
- AWS: https://aws.amazon.com/ec2/instance-types/p5/ and https://aws.amazon.com/ec2/instance-types/p4/
- GCP: https://cloud.google.com/compute/all-pricing#gpus

List three instances of AWS  and GCP each with:
Format:
<AWS/GCP>: <type> - <GPU (model×count)> - <$/hr> - <regions> - <vCPUs> - <RAM>
Examples:
AWS: p5.48xlarge - 8×H100 - $98/hr - us-east-1 - 192vCPU/2TB
GCP: a2-highgpu-8g - 8×A100 - $29/hr - us-central1 - 96vCPU/680GB
Add high quality estimated value for details that might be missing like cost per hour.
"""

  response = await metorial.run(
    message=detailed_prompt,
    server_deployments=["svd_0mhhcboxk0xiq6KBeSqchw"], # tavily search for web content
    client=openai,
    model="gpt-4.1-mini",
    max_steps=30  # Allow more steps for thorough search and extraction
  )

  if hasattr(response, 'usage'):
    total_input_tokens += response.usage.prompt_tokens if response.usage.prompt_tokens else 0
    total_output_tokens += response.usage.completion_tokens if response.usage.completion_tokens else 0

#   messages = [
#     {"role": "user", "content": detailed_prompt}
#   ]
  
#   result = None
#   total_input_tokens = 0
#   total_output_tokens = 0

#   async def session_action(session) -> str:
#     nonlocal result, total_input_tokens, total_output_tokens
#     # Reduced iterations to keep context window manageable
#     for i in range(8):
#         # Keep only the initial prompt and last 4 messages to manage context
#         # This prevents context overflow while maintaining conversation flow
#         if len(messages) > 5:
#             # Keep first message (initial prompt) and last 4 messages
#             messages[:] = [messages[0]] + messages[-4:]

#         response = await openai.chat.completions.create(
#             messages=messages,
#             model="gpt-4.1-mini",
#             tools=session["tools"],
#         )

#         # Track token usage from OpenAI response
        
#         choice = response.choices[0]
#         tool_calls = choice.message.tool_calls

#         if not tool_calls:
#             content = choice.message.content
#             result = content
#             return content

#         tool_responses = await session["callTools"](tool_calls)

#         messages.append({
#             "role": "assistant",
#             "tool_calls": choice.message.tool_calls
#         })
#         messages.extend(tool_responses)

#     # Fallback if loop completes without returning
#     return result or "No GPU data retrieved"

#   try:
#     print("[GPU Data] 📡 Connecting to Metorial servers...")
    
#     await metorial.with_provider_session(
#       MetorialOpenAI.chat_completions,
#       [{"serverDeploymentId": "svd_0mhhcboxk0xiq6KBeSqchw"}],
#       session_action
#     )
    
#     print("[GPU Data] ✓ Successfully retrieved GPU data from Metorial")
    
#   except asyncio.CancelledError:
#     print("[GPU Data] ⚠️  Request was cancelled (client disconnect or server shutdown)")
#     # Don't propagate - return what we have or fallback
#     if not result:
#       result = get_mock_gpu_data()  # Fallback to mock data if cancelled mid-request
#       print("[GPU Data] ℹ️  Using mock data as fallback due to cancellation")
#   except asyncio.TimeoutError:
#     print("[GPU Data] ❌ Metorial timeout")
#     result = get_mock_gpu_data()  # Fallback to mock data on timeout
#     print("[GPU Data] ℹ️  Using mock data as fallback due to timeout")
#   except Exception as e:
#     print(f"[GPU Data] ❌ Error: {type(e).__name__}: {str(e)}")
#     result = get_mock_gpu_data()  # Fallback to mock data on error
#     print(f"[GPU Data] ℹ️  Using mock data as fallback due to error: {str(e)}")
  
  # Record metrics for GPU data retrieval
  try:
    nv.record(
      metric="gpu.finder.gpu_data",
      ts=datetime.now(timezone.utc),
      input_tokens=total_input_tokens if total_input_tokens > 0 else len(str(detailed_prompt)) // 4,
      output_tokens=total_output_tokens if total_output_tokens > 0 else len(response.text) // 4,
    )
  except Exception as e:
    # Non-blocking: log but don't fail workflow if metrics fail
    print(f"Warning: Failed to record metrics for gpu_data: {e}")
  
  return response.text or "No GPU data retrieved"