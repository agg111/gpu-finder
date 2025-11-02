import asyncio
import os
from datetime import datetime
from typing import Optional, Dict, Any
from dotenv import load_dotenv
from aws_launcher import launch_training_instance

load_dotenv()

async def start_training(
    model_name: str,
    workload: str,
    duration: str,
    budget: Optional[str] = None,
    gpu_config: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Launch an EC2 instance and start training with simple PyTorch script.

    Args:
        model_name: Name of the model to train
        workload: Workload size
        duration: Training duration
        budget: Optional budget constraint
        gpu_config: Optional GPU configuration from the plan

    Returns:
        Dict with instance details and training status
    """
    print("[Training] 🚀 Starting real AWS EC2 training instance...")
    print(f"[Training] 📦 Model: {model_name}")
    print(f"[Training] 💾 Workload: {workload}")
    print(f"[Training] ⏱️  Duration: {duration} hours")

    try:
        # Launch actual EC2 instance with training script
        result = await launch_training_instance(
            model_name=model_name,
            workload=workload,
            duration=duration,
            budget=budget,
            gpu_config=gpu_config
        )

        return result

    except Exception as e:
        print(f"[Training] ❌ Failed to start training: {e}")
        import traceback
        traceback.print_exc()
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to start training: {str(e)}"
        }


if __name__ == "__main__":
    # Test the function
    result = asyncio.run(start_training(
        model_name="any-model",  # Will be overridden
        workload="any-size",  # Will be overridden
        duration="1"
    ))
    print(f"\n📋 Result: {result}")
