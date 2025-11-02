"use client"

import { useState } from "react"
import { checkHealth, createPlan } from "@/lib/api"

export default function TestPage() {
  const [status, setStatus] = useState<string>("Not tested")
  const [error, setError] = useState<string | null>(null)
  const [apiUrl, setApiUrl] = useState<string>("")

  const testHealth = async () => {
    setStatus("Testing health...")
    setError(null)
    try {
      const response = await checkHealth()
      setStatus(`Health check passed: ${response.status}`)
      console.log("Health response:", response)
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Unknown error"
      setError(errMsg)
      setStatus("Health check failed")
      console.error("Health error:", err)
    }
  }

  const testPlan = async () => {
    setStatus("Testing plan creation...")
    setError(null)
    try {
      const response = await createPlan({
        modelName: "meta-llama/Llama-2-7b-hf",
        workload: "500GB",
        duration: "24",
        budget: "500",
      })
      setStatus("Plan created successfully!")
      console.log("Plan response:", response)
    } catch (err) {
      const errMsg = err instanceof Error ? err.message : "Unknown error"
      setError(errMsg)
      setStatus("Plan creation failed")
      console.error("Plan error:", err)
    }
  }

  // Check API URL on mount
  useState(() => {
    const url = process.env.NEXT_PUBLIC_API_URL || "NOT SET"
    setApiUrl(url)
    console.log("API URL:", url)
  })

  return (
    <div className="p-8 max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold mb-6">API Connection Test</h1>

      <div className="space-y-4">
        <div className="p-4 bg-gray-100 rounded">
          <p className="text-sm font-mono">
            <strong>API URL:</strong> {apiUrl}
          </p>
        </div>

        <div className="p-4 bg-gray-100 rounded">
          <p className="text-sm">
            <strong>Status:</strong> {status}
          </p>
        </div>

        {error && (
          <div className="p-4 bg-red-100 text-red-800 rounded">
            <p className="text-sm">
              <strong>Error:</strong> {error}
            </p>
          </div>
        )}

        <div className="space-x-4">
          <button
            onClick={testHealth}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            Test Health Endpoint
          </button>

          <button
            onClick={testPlan}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
          >
            Test Plan Endpoint (Takes 2 min)
          </button>
        </div>

        <div className="mt-6 p-4 bg-gray-50 rounded">
          <h2 className="font-bold mb-2">Instructions:</h2>
          <ol className="list-decimal list-inside space-y-1 text-sm">
            <li>Check that the API URL is correct (should be http://localhost:8000)</li>
            <li>Ensure the backend server is running (python server.py)</li>
            <li>Click "Test Health Endpoint" to verify connection</li>
            <li>Check browser console (F12) for detailed error messages</li>
          </ol>
        </div>
      </div>
    </div>
  )
}
