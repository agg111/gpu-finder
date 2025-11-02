from workload import get_workload_config
from gpu_data import get_gpu_data
import asyncio
import nivara as nv
from datetime import datetime, timezone
from planner import build_plan

async def main() -> None:
    workflow_start = datetime.now(timezone.utc)
    
    print("Fetching model specs...")
    workload_config = await get_workload_config(
        model="moonshotai/Kimi-K2-Instruct-0905", 
        data="500GB",  # todo point to some training data
        deadline="50", # assuming hours
        budget=None,
        precision=None
    )
    print(f"Model specs: {workload_config['model_specs']}\n")

    print("Finding GPUs...")
    gpu_data = await get_gpu_data()
    print(f"GPU data: {gpu_data}\n")
    
    print("Building plan...")
    plan = await build_plan(workload_config, gpu_data)
    print(f"Plan: {plan}\n")
    
    # Record overall workflow metric
    workflow_end = datetime.now(timezone.utc)
    workflow_duration = (workflow_end - workflow_start).total_seconds()
    try:
        res = nv.record(
            metric="gpu.finder.workload",
            ts=workflow_end,
            input_tokens=0,  # Individual metrics tracked in sub-functions
            output_tokens=0,  # Individual metrics tracked in sub-functions
        )
        print(f"Workflow completed in {workflow_duration:.2f}s. Metric recorded: {res}")
    except Exception as e:
        # Non-blocking: log but don't fail workflow if metrics fail
        print(f"Workflow completed in {workflow_duration:.2f}s. Warning: Failed to record metric: {e}")
        print("Note: This is often due to SSL certificate issues. The workflow completed successfully.")

if __name__ == "__main__":
    asyncio.run(main())