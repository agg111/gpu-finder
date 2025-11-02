import nivara as nv
from datetime import datetime, timezone
from config import metorial as metorial_client, openai as openai_client
from openai import AsyncOpenAI
from typing import Dict, Any, List
import json
import os
import asyncio
import dotenv

dotenv.load_dotenv()

HARD_GOALS = {
    "availability",
    "duration",
}

SOFT_GOALS = {
    "budget",
}

async def build_plan(
    workload_config: Dict[str, Any],
    gpu_data: Any
) -> List[Dict[str, Any]]:
    """
    Build an execution plan for running the workload on available GPUs.

    Returns a list of GPU configurations ranked by suitability.

    Args:
        workload_config: Dict containing model_specs, data, deadline, budget, precision
        gpu_data: GPU availability and pricing data (only these GPUs will be used in the plan)

    Returns:
        List[Dict]: List of ranked GPU configurations with structured fields
    """
    print("[Build Plan] 🤖 Generating REAL plan using OpenAI GPT-4o...")
    print("[Build Plan] 📊 Analyzing workload requirements and GPU options...")
    print("[Build Plan] ⏱️  This will take 10-20 seconds...")

    # Build a comprehensive prompt for the planning task
    start_datetime_str = f"- Start Date & Time: {workload_config.get('start_datetime', 'Not specified')}" if workload_config.get('start_datetime') else ""

    planning_message = f"""You are a GPU allocation planning agent. Analyze the workload requirements and create a ranked list of GPU configurations.

WORKLOAD REQUIREMENTS:
- Model Specs: {workload_config.get('model_specs', 'Not provided')}
- Data Size: {workload_config.get('data', 'Not specified')}
- Deadline: {workload_config.get('deadline', 'Not specified')} hours
- Budget: ${workload_config.get('budget', 'Not specified')}
{start_datetime_str}
- Precision: {workload_config.get('precision', 'Not specified')}

AVAILABLE GPU OPTIONS (USE ONLY THESE):
{gpu_data}

TASK: Analyze and rank GPU configurations top three that best match the requirements.

IMPORTANT:
- Only use GPUs from the AVAILABLE GPU OPTIONS above
- Prioritize configurations that meet availability and deadline (HARD_GOALS)
- Consider budget as a soft constraint (SOFT_GOALS)

Return a JSON object with this exact structure:
{{
  "configurations": [
    {{
      "rank": 1,
      "provider": "GCP",
      "instance_type": "a2-highgpu-8g",
      "gpu_count": 8,
      "gpu_type": "NVIDIA A100",
      "gpu_memory": "40GB",
      "cpu": "96 vCPUs",
      "memory": "680 GB",
      "storage": "8x 1000 GB NVMe SSD (optional field, omit if not available)",
      "cost_per_hour": 29.39,
      "total_cost": 1469.50,
      "expected_runtime": "48-50 hours",
      "regions": ["us-central1", "us-east4", "europe-west4"],
      "availability": "Generally available",
      "risks": "Low risk. Generally available, meets deadline, within budget.",
      "recommendation": "Optimal choice - best balance of performance, cost, and availability"
    }},
    {{
      "rank": 2,
      ...
    }}
  ]
}}

Return ONLY valid JSON, no additional text or markdown.
Create a calendar invite if start_datetime is provided."""
    asyncOpenAI = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Use OpenAI directly for pure reasoning (no tools needed)
    # Note: If you need tools, use metorial.run() instead, which requires server_deployments
    plan_response = await asyncOpenAI.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "You are an expert GPU allocation planning agent. Return only valid JSON, no markdown or additional text."},
            {"role": "user", "content": planning_message}
        ],
        temperature=0.7,
        max_tokens=3000,
        response_format={"type": "json_object"}
    )
    
    # Record metrics for plan building
    usage = plan_response.usage if hasattr(plan_response, 'usage') else None
    try:
      nv.record(
          metric="gpu.finder.build_plan",
          ts=datetime.now(timezone.utc),
          input_tokens=usage.prompt_tokens if usage and usage.prompt_tokens else len(planning_message) // 4,
          output_tokens=usage.completion_tokens if usage and usage.completion_tokens else len(plan_response.choices[0].message.content) // 4,
      )
    except Exception as e:
      # Non-blocking: log but don't fail workflow if metrics fail
      print(f"Warning: Failed to record metrics for build_plan: {e}")

    # Parse JSON response
    content = plan_response.choices[0].message.content
    try:
        # Try to parse as JSON
        parsed = json.loads(content)

        # Handle both array and object with array
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict) and 'configurations' in parsed:
            return parsed['configurations']
        elif isinstance(parsed, dict) and 'plans' in parsed:
            return parsed['plans']
        else:
            # If it's a single object, wrap it in a list
            return [parsed]
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON response: {e}")
        print(f"Response content: {content[:500]}")
        # Return a fallback structure
        return [{
            "rank": 1,
            "provider": "Error",
            "instance_type": "Failed to parse plan",
            "gpu_count": 0,
            "gpu_type": "N/A",
            "gpu_memory": "N/A",
            "cpu": "N/A",
            "memory": "N/A",
            "cost_per_hour": 0,
            "expected_runtime": "Unknown",
            "regions": [],
            "availability": "Unknown",
            "risks": "Failed to generate plan. Please try again.",
            "recommendation": "Error occurred"
        }]


