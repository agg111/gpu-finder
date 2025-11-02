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
from gpu_data import get_gpu_data, get_gpu_data_streaming
from planner import build_plan
from notification import add_to_calendar

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
    startDateTime: Optional[str] = None
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




async def plan_generator(request: PlanRequest):
    """
    Async generator that yields SSE events with progress updates during plan creation.
    """
    workflow_start = datetime.now(timezone.utc)

    try:
        # Convert budget to None if not provided or empty
        budget_value = None if not request.budget or request.budget.strip() == "" else request.budget

        # Send initial status
        yield f"data: {json.dumps({'type': 'status', 'message': f'Starting plan creation for {request.modelName}...', 'elapsed': 0})}\n\n"

        # Step 1: Get model specifications
        yield f"data: {json.dumps({'type': 'status', 'message': f'Fetching {request.modelName} specifications from HuggingFace...', 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"

        model_start = datetime.now(timezone.utc)
        workload_config = await asyncio.wait_for(
            get_workload_config(
                model=request.modelName,
                data=request.workload,
                deadline=request.duration,
                budget=budget_value,
                start_datetime=request.startDateTime,
                precision=request.precision
            ),
            timeout=120.0
        )
        model_duration = (datetime.now(timezone.utc) - model_start).total_seconds()
        yield f"data: {json.dumps({'type': 'status', 'message': f'Model specs fetched successfully ({model_duration:.1f}s)', 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"

        # Step 2: Get available GPU options (with streaming updates)
        yield f"data: {json.dumps({'type': 'status', 'message': 'Searching GPU pricing from AWS and GCP...', 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"

        gpu_start = datetime.now(timezone.utc)
        gpu_data = None

        # Stream GPU data updates
        async for gpu_update in get_gpu_data_streaming():
            if gpu_update["type"] == "progress":
                # Forward progress updates to frontend
                progress_msg = f"[GPU Data] {gpu_update['message']}"
                yield f"data: {json.dumps({'type': 'status', 'message': progress_msg, 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"
            elif gpu_update["type"] == "complete":
                gpu_data = gpu_update["data"]
                gpu_duration = (datetime.now(timezone.utc) - gpu_start).total_seconds()
                yield f"data: {json.dumps({'type': 'status', 'message': f'GPU data retrieved successfully ({gpu_duration:.1f}s)', 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"

        if not gpu_data:
            raise Exception("Failed to fetch GPU data")

        # Step 3: Build execution plan
        yield f"data: {json.dumps({'type': 'status', 'message': 'Analyzing workload and generating execution plans...', 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"

        plan_start = datetime.now(timezone.utc)
        plan = await asyncio.wait_for(
            build_plan(workload_config, gpu_data),
            timeout=60.0
        )
        plan_duration = (datetime.now(timezone.utc) - plan_start).total_seconds()
        yield f"data: {json.dumps({'type': 'status', 'message': f'Plan created successfully ({plan_duration:.1f}s)', 'elapsed': (datetime.now(timezone.utc) - workflow_start).total_seconds()})}\n\n"

        # Calculate total workflow duration
        workflow_end = datetime.now(timezone.utc)
        workflow_duration = (workflow_end - workflow_start).total_seconds()

        # Record overall workflow metric
        try:
            res = nv.record(
                metric="gpu.finder.workload",
                ts=workflow_end,
                input_tokens=0,
                output_tokens=0,
            )
            print(f"Workflow completed in {workflow_duration:.2f}s. Metric recorded: {res}")
        except Exception as metric_error:
            print(f"Warning: Failed to record metrics: {metric_error}")

        # Convert plan to list of GPUConfig objects
        configurations = [GPUConfig(**config) for config in plan]

        # Send final result first (don't block on calendar)
        result = {
            "type": "result",
            "data": {
                "status": "success",
                "configurations": [config.model_dump() for config in configurations],
                "gpu_data": str(gpu_data),
                "model_specs": str(workload_config.get("model_specs", "")),
                "timestamp": workflow_end.isoformat(),
                "duration_seconds": workflow_duration
            }
        }
        yield f"data: {json.dumps(result)}\n\n"

        # Create calendar event in background if startDateTime is provided (after response is sent)
        if request.startDateTime:
            try:
                # Parse the datetime string (format: YYYY-MM-DDTHH:MM)
                event_datetime = datetime.fromisoformat(request.startDateTime)

                # Create a descriptive title and description
                event_title = f"Model Training: {request.modelName}"
                event_description = f"""GPU Model Training Session

Model: {request.modelName}
Workload: {request.workload}
Duration: {request.duration} hours
Budget: ${request.budget if request.budget else 'Not specified'}

Scheduled via GPU Finder Platform"""

                # Create calendar event asynchronously (non-blocking, runs in background)
                asyncio.create_task(add_to_calendar(
                    dt=event_datetime,
                    title=event_title,
                    description=event_description
                ))

                print(f"[{datetime.now(timezone.utc)}] Calendar event creation initiated in background for {event_datetime}")
            except Exception as e:
                print(f"Warning: Failed to initiate calendar event: {e}")

    except asyncio.CancelledError:
        print(f"[{datetime.now(timezone.utc)}] SSE stream was cancelled")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Request cancelled'})}\n\n"
    except asyncio.TimeoutError:
        print(f"[{datetime.now(timezone.utc)}] SSE stream timed out")
        yield f"data: {json.dumps({'type': 'error', 'message': 'Request timeout'})}\n\n"
    except Exception as e:
        print(f"[{datetime.now(timezone.utc)}] Error in SSE stream: {str(e)}")
        import traceback
        traceback.print_exc()
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"


@app.post("/api/plan/stream")
async def create_plan_stream(request: PlanRequest):
    """
    Create a GPU execution plan with Server-Sent Events for real-time progress updates.

    This endpoint streams progress updates as the plan is being created:
    - Model specs fetching (30-60 seconds)
    - GPU data fetching (30-60 seconds)
    - Plan building (10-20 seconds)

    Expected total duration: ~2 minutes
    """
    return StreamingResponse(
        plan_generator(request),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )


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
                start_datetime=request.startDateTime,
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

        # Create calendar event in background if startDateTime is provided (non-blocking)
        if request.startDateTime:
            try:
                # Parse the datetime string (format: YYYY-MM-DDTHH:MM)
                event_datetime = datetime.fromisoformat(request.startDateTime)

                # Create a descriptive title and description
                event_title = f"GPU Training: {request.modelName}"
                event_description = f"""GPU Model Training Session

Model: {request.modelName}
Workload: {request.workload}
Duration: {request.duration} hours
Budget: ${request.budget if request.budget else 'Not specified'}

Scheduled via GPU Finder Platform"""

                # Create calendar event asynchronously (non-blocking, runs in background)
                asyncio.create_task(add_to_calendar(
                    dt=event_datetime,
                    title=event_title,
                    description=event_description
                ))

                print(f"[{datetime.now(timezone.utc)}] Calendar event creation initiated in background for {event_datetime}")
            except Exception as e:
                print(f"Warning: Failed to initiate calendar event: {e}")

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
