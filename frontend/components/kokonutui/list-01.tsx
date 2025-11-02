"use client"

import { cn } from "@/lib/utils"
import { ChevronLeft, ChevronRight, Calendar, Share2, MoreHorizontal } from "lucide-react"
import type { PlanResponse } from "@/lib/api"
import { useState } from "react"
import GPUPlanCard from "./gpu-plan-card"

interface List01Props {
  className?: string
  plan?: PlanResponse | null
  formData?: {
    modelName: string
    workload: string
    duration: string
    budget?: string
    startDateTime?: string
  }
}

export default function List01({ className, plan, formData }: List01Props) {
  const [currentIndex, setCurrentIndex] = useState(0)

  const handleSchedule = async (config: any) => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    if (!formData?.startDateTime) {
      alert('Please provide a start date and time to schedule')
      return { status: 'error', message: 'No start date/time provided' }
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/training/schedule`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          modelName: formData.modelName,
          workload: formData.workload,
          duration: formData.duration,
          budget: formData.budget,
          startDateTime: formData.startDateTime,
          gpuConfig: config
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to schedule training')
      }

      const result = await response.json()
      return result

    } catch (error) {
      console.error("Error scheduling training:", error)
      throw error
    }
  }

  const handleRunNow = async (config: any) => {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    try {
      const response = await fetch(`${API_BASE_URL}/api/training/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          modelName: formData?.modelName || "minimal-model",
          workload: formData?.workload || "10MB",
          duration: formData?.duration || "1",
          budget: formData?.budget,
          gpuConfig: config
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to start training')
      }

      const result = await response.json()
      return result

    } catch (error) {
      console.error("Error starting training:", error)
      throw error
    }
  }

  // If no plan, show placeholder
  if (!plan || !plan.configurations || plan.configurations.length === 0) {
    return (
      <div
        className={cn(
          "w-full mx-auto",
          "bg-white dark:bg-zinc-900/70",
          "border border-zinc-100 dark:border-zinc-800",
          "rounded-xl shadow-sm backdrop-blur-xl",
          "p-8",
          className
        )}
      >
        <div className="text-center text-zinc-500 dark:text-zinc-400">
          <p className="text-sm">No plan generated yet</p>
          <p className="text-xs mt-1">Submit the form above to generate a GPU execution plan</p>
        </div>
      </div>
    )
  }

  const currentConfig = plan.configurations[currentIndex]
  const totalConfigs = plan.configurations.length

  return (
    <div
      className={cn(
        "w-full mx-auto",
        "bg-white dark:bg-zinc-900/70",
        "border border-zinc-100 dark:border-zinc-800",
        "rounded-xl shadow-sm backdrop-blur-xl",
        className
      )}
    >
      {/* Header */}
      <div className="p-4 border-b border-zinc-100 dark:border-zinc-800">
        <div className="flex items-center justify-between mb-2">
          <div>
            <h2 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">
              GPU Configuration #{currentConfig.rank}
            </h2>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-0.5">
              Plan generated in {plan.duration_seconds.toFixed(1)}s
            </p>
          </div>
          <div className="text-right">
            <span className="text-sm font-medium text-zinc-600 dark:text-zinc-400">
              {currentIndex + 1} of {totalConfigs}
            </span>
          </div>
        </div>
      </div>

      {/* Configuration Card */}
      <div className="p-4">
        <GPUPlanCard
          config={currentConfig}
          onSchedule={handleSchedule}
          onRunNow={handleRunNow}
          hasStartDateTime={!!formData?.startDateTime}
        />
      </div>

      {/* Navigation & Actions */}
      <div className="p-4 border-t border-zinc-100 dark:border-zinc-800 space-y-3">
        {/* Navigation buttons if multiple configs */}
        {totalConfigs > 1 && (
          <div className="flex items-center gap-2">
            <button
              onClick={() => setCurrentIndex(Math.max(0, currentIndex - 1))}
              disabled={currentIndex === 0}
              className={cn(
                "flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-sm font-medium transition-all",
                currentIndex === 0
                  ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-600 cursor-not-allowed"
                  : "bg-zinc-900 dark:bg-zinc-50 text-zinc-50 dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200 shadow-sm hover:shadow"
              )}
            >
              <ChevronLeft className="w-4 h-4" />
              <span>Previous</span>
            </button>
            <button
              onClick={() => setCurrentIndex(Math.min(totalConfigs - 1, currentIndex + 1))}
              disabled={currentIndex === totalConfigs - 1}
              className={cn(
                "flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg text-sm font-medium transition-all",
                currentIndex === totalConfigs - 1
                  ? "bg-zinc-100 dark:bg-zinc-800 text-zinc-400 dark:text-zinc-600 cursor-not-allowed"
                  : "bg-zinc-900 dark:bg-zinc-50 text-zinc-50 dark:text-zinc-900 hover:bg-zinc-800 dark:hover:bg-zinc-200 shadow-sm hover:shadow"
              )}
            >
              <span>Next Plan</span>
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}

        {/* Action buttons */}
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            className={cn(
              "flex items-center justify-center gap-2",
              "py-2 px-3 rounded-lg",
              "text-xs font-medium",
              "bg-zinc-100 dark:bg-zinc-800",
              "text-zinc-700 dark:text-zinc-300",
              "hover:bg-zinc-200 dark:hover:bg-zinc-700",
              "transition-all duration-200"
            )}
          >
            <Calendar className="w-3.5 h-3.5" />
            <span>Schedule</span>
          </button>
          <button
            type="button"
            className={cn(
              "flex items-center justify-center gap-2",
              "py-2 px-3 rounded-lg",
              "text-xs font-medium",
              "bg-zinc-100 dark:bg-zinc-800",
              "text-zinc-700 dark:text-zinc-300",
              "hover:bg-zinc-200 dark:hover:bg-zinc-700",
              "transition-all duration-200"
            )}
          >
            <Share2 className="w-3.5 h-3.5" />
            <span>Share</span>
          </button>
          <button
            type="button"
            className={cn(
              "flex items-center justify-center gap-2",
              "py-2 px-3 rounded-lg",
              "text-xs font-medium",
              "bg-zinc-100 dark:bg-zinc-800",
              "text-zinc-700 dark:text-zinc-300",
              "hover:bg-zinc-200 dark:hover:bg-zinc-700",
              "transition-all duration-200"
            )}
          >
            <MoreHorizontal className="w-3.5 h-3.5" />
            <span>More</span>
          </button>
        </div>
      </div>
    </div>
  )
}
