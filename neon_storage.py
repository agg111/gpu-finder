"""
Neon database storage for GPU execution plans.
Uses Metorial MCP server to interact with Neon database.
"""
import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from config import metorial, openai
import dotenv

dotenv.load_dotenv()

# Global OAuth session cache
_neon_oauth_session = None


async def ensure_neon_oauth() -> Optional[str]:
    """
    Ensure Neon OAuth session is active.
    First time: Creates OAuth session and waits for user authentication.
    Later: Reuses existing session.

    Returns:
        OAuth session ID if successful, None if not configured
    """
    global _neon_oauth_session

    neon_deployment_id = os.getenv("NEON_MCP")
    if not neon_deployment_id:
        print("[Neon] ⚠️  NEON_MCP not configured, skipping database storage")
        return None

    # Return cached session if available
    if _neon_oauth_session:
        print(f"[Neon] ✅ Using cached OAuth session")
        return _neon_oauth_session

    try:
        print("[Neon] 🔗 Creating OAuth session for Neon database...")
        oauth_session = metorial.oauth.sessions.create(
            server_deployment_id=neon_deployment_id
        )

        print(f"[Neon] 🌐 OAuth URL: {oauth_session.url}")
        print(f"[Neon] ⏳ Please authenticate via the URL above...")
        print(f"[Neon] ⏳ Waiting for OAuth completion...")

        await metorial.oauth.wait_for_completion([oauth_session])
        print("[Neon] ✅ OAuth session completed!")

        # Cache the session ID for future use
        _neon_oauth_session = oauth_session.id
        return _neon_oauth_session

    except Exception as e:
        print(f"[Neon] ❌ OAuth setup failed: {e}")
        import traceback
        traceback.print_exc()
        return None


async def save_plan_to_neon(
    model_name: str,
    workload: str,
    duration: str,
    budget: Optional[str],
    gpu_config: Dict[str, Any],
    training_result: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Save GPU execution plan to Neon database when user clicks "Run Now".

    Args:
        model_name: Name of the model being trained
        workload: Workload size
        duration: Training duration in hours
        budget: Optional budget constraint
        gpu_config: Selected GPU configuration
        training_result: Optional training result (instance ID, etc.)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure OAuth is set up
        oauth_session_id = await ensure_neon_oauth()
        if not oauth_session_id:
            return False

        neon_deployment_id = os.getenv("NEON_MCP")

        # Prepare the plan data
        instance_id = training_result.get("instance_id") if training_result else None
        aws_region = training_result.get("region") if training_result else None
        status = "running" if training_result else "planned"

        # First, ensure table exists
        create_table_sql = """
CREATE TABLE IF NOT EXISTS gpu_execution_plans (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255),
    workload VARCHAR(100),
    duration_hours VARCHAR(50),
    budget VARCHAR(50),
    provider VARCHAR(100),
    instance_type VARCHAR(100),
    gpu_type VARCHAR(100),
    gpu_count INTEGER,
    gpu_memory VARCHAR(100),
    cost_per_hour DECIMAL(10, 2),
    total_cost DECIMAL(10, 2),
    instance_id VARCHAR(100),
    aws_region VARCHAR(50),
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);
"""

        # Then insert the plan
        insert_sql = f"""
INSERT INTO gpu_execution_plans
(model_name, workload, duration_hours, budget, provider, instance_type, gpu_type, gpu_count, gpu_memory, cost_per_hour, total_cost, instance_id, aws_region, status)
VALUES
('{model_name}', '{workload}', '{duration}', '{budget or "N/A"}', '{gpu_config.get("provider", "N/A")}', '{gpu_config.get("instance_type", "N/A")}', '{gpu_config.get("gpu_type", "N/A")}', {gpu_config.get("gpu_count", 0)}, '{gpu_config.get("gpu_memory", "N/A")}', {gpu_config.get("cost_per_hour", 0)}, {gpu_config.get("total_cost", 0)}, '{instance_id or "N/A"}', '{aws_region or "N/A"}', '{status}');
"""

        print(f"[Neon] 💾 Saving plan to database...")
        print(f"[Neon] 📊 Plan: {model_name} on {gpu_config.get('provider')} {gpu_config.get('instance_type')}")

        # Execute table creation first
        print(f"[Neon] 🔧 Creating table if not exists...")
        result1 = await metorial.run(
            message=f"""I need you to execute this SQL query on the Neon database project 'still-bread-45277964':

{create_table_sql}

Use the Neon MCP tools to create this table if it doesn't already exist. Just execute the query and confirm it was successful.""",
            server_deployments=[
                {
                    "serverDeploymentId": neon_deployment_id,
                    "oauthSessionId": oauth_session_id
                }
            ],
            client=openai,
            model="gpt-4o-mini",
            max_steps=15,
        )
        print(f"[Neon] ✅ Table created/verified")

        # Then insert the data
        print(f"[Neon] 📝 Inserting plan data...")
        result = await metorial.run(
            message=f"""Execute this INSERT query on the Neon database project 'still-bread-45277964':

{insert_sql}

Use the Neon MCP tools to insert this GPU execution plan into the gpu_execution_plans table.""",
            server_deployments=[
                {
                    "serverDeploymentId": neon_deployment_id,
                    "oauthSessionId": oauth_session_id
                }
            ],
            client=openai,
            model="gpt-4o-mini",
            max_steps=15,
        )

        print(f"[Neon] ✅ Plan saved to database!")
        print(f"[Neon] 📝 Response: {result.text[:200]}...")

        return True

    except Exception as e:
        print(f"[Neon] ❌ Failed to save plan: {e}")
        import traceback
        traceback.print_exc()
        return False
