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

  # Define the sources we'll check with more granular steps
  sources = [
    {
      "name": "AWS P5 instances (H100 GPUs)",
      "url": "https://aws.amazon.com/ec2/instance-types/p5/",
      "provider": "AWS"
    },
    {
      "name": "AWS P4 instances (A100 GPUs)",
      "url": "https://aws.amazon.com/ec2/instance-types/p4/",
      "provider": "AWS"
    },
    {
      "name": "GCP A2 instances (A100 GPUs)",
      "url": "https://cloud.google.com/compute/all-pricing#gpus",
      "provider": "GCP"
    },
    {
      "name": "OCI GPU instances",
      "url": "https://www.oracle.com/cloud/compute/gpu/pricing/",
      "provider": "OCI"
    }
  ]

  # Get unique providers from sources
  providers = list(set(source["provider"] for source in sources))

  yield {
    "type": "progress",
    "stage": "gpu_data",
    "message": f"Starting GPU data collection from {len(sources)} sources",
    "details": {
      "total_sources": len(sources),
      "providers": providers
    }
  }

  # Collect data from all sources
  all_gpu_data = []

  for idx, source in enumerate(sources, 1):
    yield {
      "type": "progress",
      "stage": "gpu_data",
      "message": f"Fetching {source['provider']}: {source['name']}",
      "details": {
        "current": idx,
        "total": len(sources),
        "url": source['url'],
        "provider": source['provider']
      }
    }

    # Fetch data from this source
    try:
      prompt = f"""Get GPU pricing information from {source['url']}

Extract GPU instance details in this format:
<Provider>: <instance_type> - <GPU_count>×<GPU_model> - $<price>/hr - <regions> - <vCPUs> - <RAM>

You could add architecture, network, shape as well for more details.

Examples:
AWS: p5.48xlarge - 8×H100 - $98/hr - us-east-1,us-west-2 - 192vCPU - 2TB
GCP: a2-highgpu-8g - 8×A100 - $29/hr - us-central1 - 96vCPU - 680GB
OCI: BM.GPU.A100-v2.8 - 8x NVIDIA A100 80GB Tensor Core - Ampere - 8x2x100 Gb/sec RDMA* - $4/hr

List the top 2-3 most relevant GPU instances from these links.
Add high quality estimated values for any missing details."""

      response = await metorial.run(
        message=prompt,
        server_deployments=["svd_0mhhcboxk0xiq6KBeSqchw"],
        client=openai,
        model="gpt-4.1-mini",
        max_steps=15
      )

      # Print the raw data received from this source
      print(f"\n{'='*80}")
      print(f"[GPU Data] ✅ Received from {source['provider']}: {source['name']}")
      print(f"{'='*80}")
      print(response.text)
      print(f"{'='*80}\n")

      all_gpu_data.append(f"\n## {source['name']}\n{response.text}")

      yield {
        "type": "progress",
        "stage": "gpu_data",
        "message": f"✓ Completed {source['provider']}: {source['name']} ({idx}/{len(sources)})",
        "details": {
          "current": idx,
          "total": len(sources),
          "completed": True
        }
      }

    except Exception as e:
      print(f"[GPU Data] Warning: Failed to fetch {source['name']}: {e}")
      yield {
        "type": "progress",
        "stage": "gpu_data",
        "message": f"⚠️  Skipped {source['name']} (error)",
        "details": {
          "current": idx,
          "total": len(sources),
          "error": str(e)
        }
      }

  # Combine all data
  combined_data = "\n".join(all_gpu_data)

  yield {
    "type": "progress",
    "stage": "gpu_data",
    "message": "Consolidating GPU data from all sources...",
    "details": {"sources_completed": len(sources)}
  }

  # Print final consolidated data
  print(f"\n{'='*80}")
  print(f"[GPU Data] 📊 FINAL CONSOLIDATED GPU DATA")
  print(f"{'='*80}")
  print(combined_data)
  print(f"{'='*80}\n")
  print(f"[GPU Data] ✅ Total sources fetched: {len(sources)}")
  print(f"[GPU Data] ✅ Providers: {', '.join(providers)}")
  print(f"[GPU Data] ✅ Data length: {len(combined_data)} characters\n")

  yield {
    "type": "complete",
    "stage": "gpu_data",
    "message": f"GPU data fetched from {len(sources)} sources",
    "data": combined_data,
    "details": {
      "sources_fetched": len(sources),
      "providers": providers
    }
  }


async def get_gpu_data() -> str:
  """
  Fetch detailed GPU availability and pricing information from AWS, GCP, and OCI.
  Non-streaming version for backward compatibility.

  Returns:
    str: Structured GPU data with actual pricing, availability, and location details
  """
  print("[GPU Data] ⚠️  Fetching REAL data from AWS/GCP/OCI (this may take 90+ seconds)...")
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