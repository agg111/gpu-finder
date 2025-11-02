/**
 * API service layer for communicating with the GPU Finder backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export interface PlanRequest {
  modelName: string
  workload: string
  duration: string
  budget?: string
  precision?: string
  framework?: string
}

export interface GPUConfig {
  rank: number
  provider: string
  instance_type: string
  gpu_count: number
  gpu_type: string
  gpu_memory: string
  cpu: string
  memory: string
  storage?: string
  cost_per_hour: number
  total_cost?: number
  expected_runtime: string
  regions: string[]
  availability: string
  risks: string
  recommendation?: string
}

export interface PlanResponse {
  status: string
  configurations: GPUConfig[]
  gpu_data: string
  model_specs: string
  timestamp: string
  duration_seconds: number
}

export interface ApiError {
  error: string
  message: string
}

/**
 * Create a GPU execution plan
 * @param request - Plan request with model, workload, and budget details
 * @returns Promise<PlanResponse>
 * @throws Error if the request fails
 */
export async function createPlan(request: PlanRequest): Promise<PlanResponse> {
  const response = await fetch(`${API_BASE_URL}/api/plan`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  })

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({
      error: 'Unknown error',
      message: 'Failed to create plan. Please try again.',
    }))
    throw new Error(errorData.message || 'Failed to create plan')
  }

  return response.json()
}

/**
 * Check API health status
 * @returns Promise<{status: string, timestamp: string}>
 */
export async function checkHealth(): Promise<{status: string, timestamp: string}> {
  const response = await fetch(`${API_BASE_URL}/api/health`)

  if (!response.ok) {
    throw new Error('API is not healthy')
  }

  return response.json()
}
