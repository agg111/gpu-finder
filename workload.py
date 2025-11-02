import asyncio
import nivara as nv
from datetime import datetime, timezone
from config import metorial, openai
import os
import dotenv

dotenv.load_dotenv()

async def get_model_specs(model_to_train: str) -> str:
  """
  Fetch detailed model specifications from HuggingFace.

  Extracts key information needed for GPU planning including:
  - Total and activated parameters
  - Architecture details
  - Memory requirements
  - Context length
  - Model size
  """
  print(f"[Model Specs] 🌐 Fetching REAL data from HuggingFace for {model_to_train}...")
  print(f"[Model Specs] 📡 This will take 30-60 seconds...")
  # Construct the direct HuggingFace URL for the model
  model_url = f"https://huggingface.co/{model_to_train}"
  
  detailed_prompt = f"""Go to the HuggingFace model page at {model_url} and extract the complete model specifications.

CRITICAL: Look for the "Model Summary" section which contains a detailed table with all technical specifications.

Extract ALL of the following information if available:

**ARCHITECTURE & STRUCTURE:**
- Architecture type (e.g., Transformer, MoE/Mixture-of-Experts, etc.)
- Number of layers (total and dense layers if specified)
- Attention mechanism type

**PARAMETERS:**
- Total parameters (e.g., "1T" for 1 trillion, "32B" for 32 billion)
- Activated parameters (important for MoE models)
- Number of dense layers

**DIMENSIONS:**
- Attention hidden dimension
- MoE hidden dimension (per expert)
- Number of attention heads
- Vocabulary size
- Context length (in tokens, e.g., "256K" = 256,000)

**MoE-SPECIFIC (if applicable):**
- Number of experts
- Selected experts per token
- Number of shared experts

**STORAGE & MEMORY:**
- Tensor types available (FP32, BF16, FP8_E4M3, etc.)
- Model size information
- Memory requirements for inference

**INSTRUCTIONS:**
1. Navigate to the exact model page URL: {model_url}
2. Locate the "Model Summary" section (usually section 2 on HuggingFace model pages)
3. Read the specification table completely
4. Extract ALL values from the table
5. Also check the "Model Introduction" section for additional context
6. Include any memory/compute requirements mentioned

**OUTPUT FORMAT:**
Provide a structured JSON-like summary with all extracted values. If you cannot find certain information, explicitly state "Not found" for that field.

Example format:
{{
  "architecture": "...",
  "total_parameters": "...",
  "activated_parameters": "...",
  "layers": "...",
  "context_length": "...",
  "hidden_dimension": "...",
  "attention_heads": "...",
  "vocabulary_size": "...",
  "experts": "...",
  "tensor_types": "...",
  ...
}}"""
  
  response = await metorial.run(
    message=detailed_prompt,
    server_deployments=["svd_0mhhcboxk0xiq6KBeSqchw"], # tavily search for web content
    client=openai,
    model="gpt-4.1-mini",
    max_steps=30  # Allow more steps for thorough search and extraction
  )
  
  # Record metrics for model specs retrieval
  # Note: metorial.run() doesn't expose token counts directly, so we estimate or use response length
  try:
    nv.record(
      metric="gpu.finder.model_specs",
      ts=datetime.now(timezone.utc),
      input_tokens=len(detailed_prompt) // 4,  # Rough estimate: ~4 chars per token
      output_tokens=len(response.text) // 4,
    )
  except Exception as e:
    # Non-blocking: log but don't fail workflow if metrics fail
    print(f"Warning: Failed to record metrics for model_specs: {e}")
  
  return response.text

# Workload configuration - model, data_size, deadline, budget(optional), precision(optional) 
async def get_workload_config(model, data, deadline, budget=None, precision=None):
    model_specs = await get_model_specs(model)

    # TODO: add precision, framework, region_preference 
    
    return {
    "model_specs": model_specs,
    "data": data,
    "deadline": deadline,
    "budget": budget,
    "precision": precision
}
