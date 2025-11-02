"""
FastAPI server to expose GPU planning functionality to the frontend.
"""
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
from datetime import datetime, timezone
import nivara as nv
import json

from workload import get_workload_config
from gpu_data import get_gpu_data
from planner import build_plan

app = FastAPI(title="GPU Finder API", version="1.0.0")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Next.js default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PlanRequest(BaseModel):
    """Request model for GPU planning endpoint"""
    modelName: str
    workload: str
    duration: str
    budget: Optional[str] = None
    precision: Optional[str] = None
    framework: Optional[str] = None


class GPUConfig(BaseModel):
    """Individual GPU configuration model"""
    rank: int
    provider: str
    instance_type: str
    gpu_count: int
    gpu_type: str
    gpu_memory: str
    cpu: str
    memory: str
    storage: Optional[str] = None
    cost_per_hour: float
    total_cost: Optional[float] = None
    expected_runtime: str
    regions: List[str]
    availability: str
    risks: str
    recommendation: Optional[str] = None


class PlanResponse(BaseModel):
    """Response model for GPU planning endpoint"""
    status: str
    configurations: List[GPUConfig]
    gpu_data: str
    model_specs: str
    timestamp: str
    duration_seconds: float


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "ok", "message": "GPU Finder API is running"}


@app.get("/api/health")
async def health():
    """Health check endpoint for the API"""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}




@app.post("/api/plan", response_model=PlanResponse)
async def create_plan(request: PlanRequest):
    """
    Create a GPU execution plan based on workload requirements.

    Note: This is the non-streaming version. Use /api/plan/stream for real-time updates.

    Expected duration: ~2 minutes (60s for model specs, 60s for GPU data, 10-20s for planning)
    """
    workflow_start = datetime.now(timezone.utc)

    try:
        # Convert budget to None if not provided or empty
        budget_value = None if not request.budget or request.budget.strip() == "" else request.budget

        print(f"[{datetime.now(timezone.utc)}] Starting plan creation for model: {request.modelName}")

        # Step 1: Get model specifications and workload configuration
        print(f"[{datetime.now(timezone.utc)}] Fetching model specs...")
        workload_config = await asyncio.wait_for(
            get_workload_config(
                model=request.modelName,
                data=request.workload,
                deadline=request.duration,
                budget=budget_value,
                precision=request.precision
            ),
            timeout=120.0  # 2 minutes timeout
        )
        print(f"[{datetime.now(timezone.utc)}] Model specs fetched successfully")

        # Step 2: Get available GPU options
        print(f"[{datetime.now(timezone.utc)}] Finding available GPUs...")
        gpu_data = await asyncio.wait_for(
            get_gpu_data(),
            timeout=120.0  # 2 minutes timeout
        )
        print(f"[{datetime.now(timezone.utc)}] GPU data retrieved successfully")

        # Step 3: Build execution plan
        print(f"[{datetime.now(timezone.utc)}] Building execution plan...")
        plan = await asyncio.wait_for(
            build_plan(workload_config, gpu_data),
            timeout=60.0  # 1 minute timeout
        )
        print(f"[{datetime.now(timezone.utc)}] Plan created successfully")

        # Calculate total workflow duration
        workflow_end = datetime.now(timezone.utc)
        workflow_duration = (workflow_end - workflow_start).total_seconds()

        # Record overall workflow metric
        try:
            res = nv.record(
                metric="gpu.finder.workload",
                ts=workflow_end,
                input_tokens=0,  # Individual metrics tracked in sub-functions
                output_tokens=0,  # Individual metrics tracked in sub-functions
            )
            print(f"Workflow completed in {workflow_duration:.2f}s. Metric recorded: {res}")
        except Exception as metric_error:
            print(f"Warning: Failed to record metrics: {metric_error}")

        print("plan ->", plan)
        # Convert plan (List[Dict]) to list of GPUConfig objects
        configurations = [GPUConfig(**config) for config in plan]

        # Return successful response
        return PlanResponse(
            status="success",
            configurations=configurations,
            gpu_data=str(gpu_data),
            model_specs=str(workload_config.get("model_specs", "")),
            timestamp=workflow_end.isoformat(),
            duration_seconds=workflow_duration
        )

    except asyncio.CancelledError:
        print(f"[{datetime.now(timezone.utc)}] Request was cancelled by client or server shutdown")
        # Don't raise HTTPException for CancelledError - just log and return error
        # This prevents the server from crashing when client disconnects
        from fastapi.responses import JSONResponse
        return JSONResponse(
            status_code=499,  # Client Closed Request
            content={
                "status": "cancelled",
                "error": "Request cancelled",
                "message": "The request was cancelled. This can happen if the client disconnected or the server is shutting down."
            }
        )
    except asyncio.TimeoutError:
        print(f"[{datetime.now(timezone.utc)}] Request timed out")
        raise HTTPException(
            status_code=504,  # Gateway Timeout
            detail={
                "error": "Request timeout",
                "message": "The operation took too long to complete. Please try again or use mock data mode for faster responses."
            }
        )
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Error during plan creation: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "message": "Failed to create execution plan. Please try again or contact support."
            }
        )


if __name__ == "__main__":
    import uvicorn
    import os

    print("=" * 60)
    print("🚀 Starting GPU Finder API server...")
    print("=" * 60)
    print("📍 API URL: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("=" * 60)

    # Disable uvloop to avoid conflicts with Metorial's async operations
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info", loop="asyncio")
