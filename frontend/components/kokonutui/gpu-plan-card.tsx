"use client"

import { cn } from "@/lib/utils"
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
} from "lucide-react"
import type { GPUConfig } from "@/lib/api"

interface GPUPlanCardProps {
  config: GPUConfig
  className?: string
}

export default function GPUPlanCard({ config, className }: GPUPlanCardProps) {
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
    </div>
  )
}
