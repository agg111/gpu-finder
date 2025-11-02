from config import openai
from typing import Dict, Any

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
) -> str:
    """
    Build an execution plan for running the workload on available GPUs.
    
    Uses OpenAI directly for pure reasoning (no tools needed).
    For tasks requiring tools, use Metorial instead.
    
    Args:
        workload_config: Dict containing model_specs, data, deadline, budget, precision
        gpu_data: GPU availability and pricing data (only these GPUs will be used in the plan)
    
    Returns:
        str: Structured plan with ranked GPU configurations
    """
    
    # Build a comprehensive prompt for the planning task
    planning_message = f"""You are a GPU allocation planning agent. Create a detailed execution plan for running a machine learning workload.

WORKLOAD REQUIREMENTS:
- Model Specs: {workload_config.get('model_specs', 'Not provided')}
- Data Size: {workload_config.get('data', 'Not specified')}
- Deadline: {workload_config.get('deadline', 'Not specified')} hours
- Budget: ${workload_config.get('budget', 'Not specified')}
- Precision: {workload_config.get('precision', 'Not specified')}

AVAILABLE GPU OPTIONS (USE ONLY THESE - DO NOT ADD OR INVENT OTHER GPUs):
{gpu_data}

CRITICAL CONSTRAINT - READ CAREFULLY:
1. You MUST only use the GPU options provided in the AVAILABLE GPU OPTIONS section above
2. DO NOT add, invent, or reference GPU configurations that are NOT explicitly listed in the AVAILABLE GPU OPTIONS section
3. Your plan should ONLY reference GPUs that appear in the AVAILABLE GPU OPTIONS section above
4. Any GPU configurations in your plan MUST match exactly what's provided in the AVAILABLE GPU OPTIONS section

TASK: Analyze the workload requirements against the available GPU options to create an optimal execution plan.

Your plan should:
1. Calculate compute requirements (FLOPs, memory bandwidth needs) based on the model specs
2. Estimate GPU memory requirements (considering model size, batch size, gradients, optimizer states)
3. From the AVAILABLE GPU OPTIONS listed above, rank the top configurations (up to 5, or fewer if fewer options are available) that best match the requirements
4. For each ranked configuration from the available options, provide:
   - Provider + instance type (must match exactly what's in the available GPU data)
   - GPU count and type (must match exactly what's in the available GPU data)
   - CPU, SSD, memory configuration (use the data provided)
   - Cost estimate (use pricing from the available GPU data)
   - Expected runtime (considering the deadline constraint)
   - Region/availability (from the available GPU data)
   - Risk assessment (availability, deadline feasibility, budget constraints)

STRICT RULES - FOLLOW THESE:
- Only rank and analyze GPUs that appear in the AVAILABLE GPU OPTIONS section
- If fewer than 5 GPUs are available, rank only the available ones
- Do not reference any GPU configurations not explicitly mentioned in the available options
- Every GPU in your plan must be traceable back to the AVAILABLE GPU OPTIONS section above
- Prioritize configurations that meet HARD_GOALS (availability, duration) first, then optimize for SOFT_GOALS (budget)

Format your response as a structured plan with clear sections."""
    
    # Use OpenAI directly for pure reasoning (no tools needed)
    # Note: If you need tools, use metorial.run() instead, which requires server_deployments
    response = await openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are an expert GPU allocation planning agent specializing in machine learning infrastructure."},
            {"role": "user", "content": planning_message}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    
    return response.choices[0].message.content

