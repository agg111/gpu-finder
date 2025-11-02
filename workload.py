import asyncio
from metorial import Metorial
from openai import AsyncOpenAI
import os
import dotenv

dotenv.load_dotenv()

metorial= Metorial(api_key=os.getenv("METORIAL_API_KEY"))
openai = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def get_model_specs(model_to_train: str) -> dict[str, any]:
  response = await metorial.run(
    message=f"Look up on https://huggingface.co/models to fetch detailed model specs like model_size, tensor_type, parameters for- {model_to_train}",
    server_deployments=["svd_0mhhcboxk0xiq6KBeSqchw"], # tavily search
    client=openai,
    model="gpt-4o",
    max_steps=25    # optional
  )
  return response.text

# Workload configuration - model, data_size, deadline, budget(optional), precision(optional) 
def get_workload_config(model, data, deadline, budget=None, precision=None):
  model_specs = asyncio.run(get_model_specs(model))
  print("Model specs: ", model_specs)

  return {
    "model_specs": model_specs,
    "data_size": data_size,
    "deadline": deadline,
    "budget": budget,
    "precision": precision
  }
