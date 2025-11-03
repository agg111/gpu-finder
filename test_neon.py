"""
Test script to trigger Neon OAuth and save a sample plan.
"""
import asyncio
from neon_storage import save_plan_to_neon

async def test_neon_oauth():
    """Test Neon OAuth and database save."""
    print("="*80)
    print("Testing Neon Database OAuth and Save")
    print("="*80)

    # Sample GPU plan data
    sample_gpu_config = {
        "provider": "AWS",
        "instance_type": "p3.2xlarge",
        "gpu_type": "V100",
        "gpu_count": 1,
        "gpu_memory": "16GB",
        "cost_per_hour": 3.06,
        "total_cost": 73.44,
        "regions": ["us-east-1", "us-west-2"]
    }

    sample_training_result = {
        "instance_id": "i-test123456",
        "region": "us-east-1",
        "status": "running"
    }

    print("\n📊 Sample Plan to Save:")
    print(f"  Model: test-model-llama2")
    print(f"  Workload: 500GB")
    print(f"  Duration: 24 hours")
    print(f"  Budget: $100")
    print(f"  GPU: {sample_gpu_config['provider']} {sample_gpu_config['instance_type']}")
    print(f"  Cost: ${sample_gpu_config['cost_per_hour']}/hour")
    print()

    # This will trigger OAuth on first run
    success = await save_plan_to_neon(
        model_name="test-model-llama2",
        workload="500GB",
        duration="24",
        budget="100",
        gpu_config=sample_gpu_config,
        training_result=sample_training_result
    )

    if success:
        print("\n" + "="*80)
        print("✅ SUCCESS! Plan saved to Neon database")
        print("="*80)
    else:
        print("\n" + "="*80)
        print("❌ FAILED to save plan")
        print("="*80)

if __name__ == "__main__":
    asyncio.run(test_neon_oauth())
