from workload import get_workload_config
from gpu_data import get_gpu_data
import asyncio
import nivara as nv
from datetime import datetime, timezone
from planner import build_plan

async def main() -> None:
    res = nv.record(
        metric="gpu.finder.workload",
        ts=datetime.now(timezone.utc),
        input_tokens=5,
        output_tokens=1,
    )
    print(res)

    print("Fetching model specs...")
    workload_config = await get_workload_config(model="moonshotai/Kimi-K2-Instruct-0905", 
    data="500GB",  # todo point to some training data
    deadline="50", # assuming hours
    budget=None,
    precision=None)
    print(f"Model specs: {workload_config['model_specs']}\n")

    print("Finding GPUs...")
    gpu_data = await get_gpu_data()
    print(f"GPU data: {gpu_data}\n")
    
    print("Building plan...")
    plan = await build_plan(workload_config, gpu_data)
    print(f"Plan: {plan}\n")

if __name__ == "__main__":
    asyncio.run(main())