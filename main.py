from workload import get_workload_config
from gpu_data import get_gpu_data
import asyncio

def main() -> None:
    workload_config = get_workload_config(model="moonshotai/Kimi-K2-Instruct-0905", 
    data="500GB",  # todo point to some training data
    deadline="50", # assuming hours
    budget=None,
    precision=None)
    gpu_data = asyncio.run(get_gpu_data())

    print("Model specs: ", workload_config["model_specs"])
    print("GPU data: ", gpu_data)

if __name__ == "__main__":
    main()