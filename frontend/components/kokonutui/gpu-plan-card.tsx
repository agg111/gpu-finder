"use client"

import { cn } from "@/lib/utils"
import { useState } from "react"
import {
  Server,
  Cpu,
  MemoryStick,
  DollarSign,
  Clock,
  MapPin,
  AlertTriangle,
  CheckCircle,
  HardDrive,
  Play,
  Loader2,
  ExternalLink,
  Calendar,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import type { GPUConfig } from "@/lib/api"

interface GPUPlanCardProps {
  config: GPUConfig
  className?: string
  onSchedule?: (config: GPUConfig) => Promise<any>
  onRunNow?: (config: GPUConfig) => Promise<any>
  hasStartDateTime?: boolean
}

export default function GPUPlanCard({ config, className, onSchedule, onRunNow, hasStartDateTime }: GPUPlanCardProps) {
  const [isScheduling, setIsScheduling] = useState(false)
  const [isRunning, setIsRunning] = useState(false)
  const [scheduleStatus, setScheduleStatus] = useState<any>(null)
  const [trainingStatus, setTrainingStatus] = useState<any>(null)

  const handleSchedule = async () => {
    if (!onSchedule) return

    setIsScheduling(true)
    try {
      const result = await onSchedule(config)
      setScheduleStatus(result)
    } catch (error) {
      console.error("Failed to schedule training:", error)
      setScheduleStatus({ status: "error", message: "Failed to schedule training" })
    } finally {
      setIsScheduling(false)
    }
  }

  const handleRunNow = async () => {
    if (!onRunNow) return

    setIsRunning(true)
    try {
      const result = await onRunNow(config)
      setTrainingStatus(result)
    } catch (error) {
      console.error("Failed to start training:", error)
      setTrainingStatus({ status: "error", message: "Failed to start training" })
    } finally {
      setIsRunning(false)
    }
  }

  const getRiskColor = () => {
    const lowerRisk = config.risks.toLowerCase()
    if (lowerRisk.includes("low risk") || lowerRisk.includes("within budget")) {
      return "text-green-600 dark:text-green-400"
    }
    if (lowerRisk.includes("medium") || lowerRisk.includes("limited")) {
      return "text-yellow-600 dark:text-yellow-400"
    }
    return "text-red-600 dark:text-red-400"
  }

  const getAvailabilityBadge = () => {
    if (config.availability.toLowerCase().includes("generally")) {
      return "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
    }
    if (config.availability.toLowerCase().includes("limited")) {
      return "bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300"
    }
    return "bg-gray-100 dark:bg-gray-900/30 text-gray-700 dark:text-gray-300"
  }

  return (
    <div className={cn("space-y-3", className)}>
      {/* Provider & Instance */}
      <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-700/50">
            <Server className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
          </div>
          <div>
            <p className="text-xs text-zinc-600 dark:text-zinc-400">Provider & Instance</p>
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{config.provider}</p>
          </div>
        </div>
        <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">{config.instance_type}</span>
      </div>

      {/* GPU Configuration */}
      <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-700/50">
            <Cpu className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
          </div>
          <div>
            <p className="text-xs text-zinc-600 dark:text-zinc-400">GPU Configuration</p>
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              {config.gpu_count}x {config.gpu_type}
            </p>
          </div>
        </div>
        <span className="text-sm font-medium text-zinc-700 dark:text-zinc-300">{config.gpu_memory}</span>
      </div>

      {/* System Specs */}
      <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-700/50">
            <MemoryStick className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
          </div>
          <div>
            <p className="text-xs text-zinc-600 dark:text-zinc-400">System Specs</p>
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              {config.cpu} • {config.memory}
            </p>
          </div>
        </div>
        {config.storage && (
          <div className="flex items-center gap-1 text-xs text-zinc-700 dark:text-zinc-300">
            <HardDrive className="w-3 h-3" />
            <span>{config.storage}</span>
          </div>
        )}
      </div>

      {/* Cost */}
      <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-700/50">
            <DollarSign className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
          </div>
          <div>
            <p className="text-xs text-zinc-600 dark:text-zinc-400">Cost Estimate</p>
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              ${config.cost_per_hour.toFixed(2)}/hour
            </p>
          </div>
        </div>
        {config.total_cost && (
          <div className="text-right">
            <p className="text-xs text-zinc-600 dark:text-zinc-400">Total</p>
            <p className="text-sm font-semibold text-zinc-700 dark:text-zinc-300">
              ${config.total_cost.toFixed(2)}
            </p>
          </div>
        )}
      </div>

      {/* Runtime */}
      <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-700/50">
            <Clock className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
          </div>
          <div>
            <p className="text-xs text-zinc-600 dark:text-zinc-400">Expected Runtime</p>
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{config.expected_runtime}</p>
          </div>
        </div>
      </div>

      {/* Regions */}
      <div className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-zinc-100 dark:bg-zinc-700/50">
            <MapPin className="w-4 h-4 text-zinc-600 dark:text-zinc-400" />
          </div>
          <div className="flex-1">
            <p className="text-xs text-zinc-600 dark:text-zinc-400">Regions</p>
            <p className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">
              {config.regions.join(", ") || "Multiple regions"}
            </p>
          </div>
        </div>
        <span className={cn("text-xs px-2 py-1 rounded-full font-medium whitespace-nowrap ml-2", getAvailabilityBadge())}>
          {config.availability}
        </span>
      </div>

      {/* Risk Assessment */}
      <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
        <div className="flex items-start gap-2 mb-2">
          <AlertTriangle className={cn("w-4 h-4 mt-0.5", getRiskColor())} />
          <div className="flex-1">
            <p className="text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1">Risk Assessment</p>
            <p className={cn("text-xs", getRiskColor())}>{config.risks}</p>
          </div>
        </div>
      </div>

      {/* Recommendation */}
      {config.recommendation && (
        <div className="p-3 bg-zinc-50 dark:bg-zinc-800/50 rounded-lg border border-zinc-200 dark:border-zinc-700">
          <div className="flex items-start gap-2">
            <CheckCircle className="w-4 h-4 mt-0.5 text-zinc-600 dark:text-zinc-400" />
            <div className="flex-1">
              <p className="text-xs font-medium text-zinc-700 dark:text-zinc-300 mb-1">Recommendation</p>
              <p className="text-xs text-zinc-600 dark:text-zinc-400">{config.recommendation}</p>
            </div>
          </div>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex gap-2">
        {/* Run Now Button */}
        {onRunNow && (
          <Button
            onClick={handleRunNow}
            disabled={isRunning || trainingStatus?.status === "success"}
            className="w-full bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50"
          >
            {isRunning ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Starting...
              </>
            ) : trainingStatus?.status === "success" ? (
              <>
                <CheckCircle className="mr-2 h-4 w-4" />
                Training Started
              </>
            ) : (
              <>
                <Play className="mr-2 h-4 w-4" />
                Run Now
              </>
            )}
          </Button>
        )}
      </div>

      {/* Training Status */}
      {trainingStatus && trainingStatus.status === "success" && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
              <p className="text-sm font-semibold text-green-900 dark:text-green-100">Training Started Successfully!</p>
            </div>
            {trainingStatus.selected_plan && (
              <div className="space-y-1 text-xs text-green-800 dark:text-green-200">
                <p><span className="font-medium">Provider:</span> {trainingStatus.selected_plan.provider}</p>
                <p><span className="font-medium">Instance:</span> {trainingStatus.selected_plan.instance_type}</p>
                <p><span className="font-medium">GPU:</span> {trainingStatus.selected_plan.gpu_count}x {trainingStatus.selected_plan.gpu_type}</p>
                <p><span className="font-medium">GPU Memory:</span> {trainingStatus.selected_plan.gpu_memory}</p>
                <p><span className="font-medium">Cost:</span> ${trainingStatus.selected_plan.cost_per_hour.toFixed(2)}/hour</p>
                {trainingStatus.selected_plan.total_cost > 0 && (
                  <p><span className="font-medium">Total Est. Cost:</span> ${trainingStatus.selected_plan.total_cost.toFixed(2)}</p>
                )}
              </div>
            )}
            {trainingStatus.dashboard_url && (
              <a
                href={trainingStatus.dashboard_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400 hover:underline mt-2"
              >
                <ExternalLink className="w-3 h-3" />
                View in AWS Console
              </a>
            )}
            {trainingStatus.s3_logs_url && (
              <a
                href={trainingStatus.s3_logs_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1 text-xs text-green-600 dark:text-green-400 hover:underline"
              >
                <ExternalLink className="w-3 h-3" />
                View Training Logs
              </a>
            )}
          </div>
        </div>
      )}

      {trainingStatus && trainingStatus.status === "error" && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />
            <p className="text-sm text-red-900 dark:text-red-100">{trainingStatus.message}</p>
          </div>
        </div>
      )}

      {/* Schedule Status */}
      {scheduleStatus && scheduleStatus.status === "success" && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <div className="flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-green-600 dark:text-green-400" />
            <p className="text-sm font-semibold text-green-900 dark:text-green-100">{scheduleStatus.message || 'Training scheduled successfully!'}</p>
          </div>
        </div>
      )}

      {scheduleStatus && scheduleStatus.status === "error" && (
        <div className="p-3 bg-red-50 dark:bg-red-900/20 rounded-lg border border-red-200 dark:border-red-800">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600 dark:text-red-400" />
            <p className="text-sm text-red-900 dark:text-red-100">{scheduleStatus.message}</p>
          </div>
        </div>
      )}
    </div>
  )
}
