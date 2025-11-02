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

async def get_gpu_data_streaming():
  """
  Streaming generator that fetches GPU data and yields progress updates.

  Yields:
    dict: Progress updates with type 'progress' or 'complete'
  """
  print("[GPU Data] 🌐 Starting streaming GPU data fetch...")

  # Define the URLs we'll check
  urls_to_check = [
    ("AWS P5 instances (H100 GPUs)", "https://aws.amazon.com/ec2/instance-types/p5/"),
    ("AWS P4 instances (A100 GPUs)", "https://aws.amazon.com/ec2/instance-types/p4/"),
    ("GCP GPU pricing", "https://cloud.google.com/compute/all-pricing#gpus")
  ]

  yield {
    "type": "progress",
    "stage": "gpu_data",
    "message": f"Checking {len(urls_to_check)} pricing sources...",
    "details": {"total_sources": len(urls_to_check)}
  }

  detailed_prompt = """Get current AWS and GCP GPU pricing from:
- AWS: https://aws.amazon.com/ec2/instance-types/p5/ and https://aws.amazon.com/ec2/instance-types/p4/
- GCP: https://cloud.google.com/compute/all-pricing#gpus

List three instances of AWS and GCP each with:
Format:
<AWS/GCP>: <type> - <GPU (model×count)> - <$/hr> - <regions> - <vCPUs> - <RAM>
Examples:
AWS: p5.48xlarge - 8×H100 - $98/hr - us-east-1 - 192vCPU/2TB
GCP: a2-highgpu-8g - 8×A100 - $29/hr - us-central1 - 96vCPU/680GB
Add high quality estimated value for details that might be missing like cost per hour.

Stream your progress as you search each URL.
"""

  yield {
    "type": "progress",
    "stage": "gpu_data",
    "message": "Initializing Metorial search agent...",
    "details": {}
  }

  # Start the search
  response = await metorial.run(
    message=detailed_prompt,
    server_deployments=["svd_0mhhcboxk0xiq6KBeSqchw"], # tavily search for web content
    client=openai,
    model="gpt-4.1-mini",
    max_steps=30  # Allow more steps for thorough search and extraction
  )

  # Track token usage if available
  total_input_tokens = 0
  total_output_tokens = 0
  if hasattr(response, 'usage'):
    total_input_tokens = response.usage.prompt_tokens if response.usage.prompt_tokens else 0
    total_output_tokens = response.usage.completion_tokens if response.usage.completion_tokens else 0

  yield {
    "type": "complete",
    "stage": "gpu_data",
    "message": "GPU data fetched successfully",
    "data": response.text,
    "details": {
      "input_tokens": total_input_tokens,
      "output_tokens": total_output_tokens
    }
  }


async def get_gpu_data() -> str:
  """
  Fetch detailed GPU availability and pricing information from AWS and GCP.
  Non-streaming version for backward compatibility.

  Returns:
    str: Structured GPU data with actual pricing, availability, and location details
  """
  print("[GPU Data] ⚠️  Fetching REAL data from AWS/GCP (this may take 60+ seconds)...")
  print("[GPU Data] 🌐 Initializing Metorial web search...")

  result = None
  async for update in get_gpu_data_streaming():
    if update["type"] == "complete":
      result = update["data"]
      break
    else:
      print(f"[GPU Data] {update['message']}")

  # Record metrics for GPU data retrieval
  if result:
    try:
      nv.record(
        metric="gpu.finder.gpu_data",
        ts=datetime.now(timezone.utc),
        input_tokens=0,  # Tracked in streaming version
        output_tokens=0,  # Tracked in streaming version
      )
    except Exception as e:
      # Non-blocking: log but don't fail workflow if metrics fail
      print(f"Warning: Failed to record metrics for gpu_data: {e}")

  return result if result else "No GPU data retrieved"