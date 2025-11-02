"use client"

import { cn } from "@/lib/utils"
import { Calendar, Share2, MoreHorizontal, Cpu, MemoryStick, DollarSign, Clock, AlertTriangle, ChevronLeft, ChevronRight } from "lucide-react"
import type { PlanResponse } from "@/lib/api"
import { useState } from "react"
import GPUPlanCard from "./gpu-plan-card"

interface SpecItem {
  id: string
  title: string
  description?: string
  value: string
  type: "gpu" | "cpu" | "memory" | "cost" | "runtime" | "risk"
}

interface List01Props {
  totalBalance?: string
  specs?: SpecItem[]
  className?: string
  plan?: PlanResponse | null
}

const SPECS: SpecItem[] = [
  {
    id: "1",
    title: "GPU",
    description: "Graphics Processing Unit",
    value: "NVIDIA A100 80GB",
    type: "gpu",
  },
  {
    id: "2",
    title: "CPU",
    description: "Central Processing Unit",
    value: "32 vCPUs",
    type: "cpu",
  },
  {
    id: "3",
    title: "Memory",
    description: "System RAM",
    value: "256 GB",
    type: "memory",
  },
  {
    id: "4",
    title: "Cost",
    description: "Estimated total cost",
    value: "$245.50",
    type: "cost",
  },
  {
    id: "5",
    title: "Expected Runtime",
    description: "Estimated duration",
    value: "4.5 hours",
    type: "runtime",
  },
  {
    id: "6",
    title: "Risk",
    description: "Availability risk",
    value: "Low",
    type: "risk",
  },
]

export default function List01({ totalBalance = "$26,540.25", specs = SPECS, className, plan }: List01Props) {
  // If a plan is available, display it instead of default specs
  if (plan) {
    return (
      <div
        className={cn(
          "w-full mx-auto",
          "bg-white dark:bg-zinc-900/70",
          "border border-zinc-100 dark:border-zinc-800",
          "rounded-xl shadow-sm backdrop-blur-xl",
          className,
        )}
      >
        {/* Plan Header */}
        <div className="p-4 border-b border-zinc-100 dark:border-zinc-800">
          <div className="flex items-center gap-2 mb-1">
            <FileText className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />
            <p className="text-xs text-zinc-600 dark:text-zinc-400">GPU Execution Plan</p>
          </div>
          <h1 className="text-lg font-semibold text-zinc-900 dark:text-zinc-50">Plan Generated Successfully</h1>
          <p className="text-xs text-zinc-500 dark:text-zinc-400 mt-1">
            Completed in {plan.duration_seconds.toFixed(1)}s
          </p>
        </div>

        {/* Plan Content */}
        <div className="p-4 max-h-[600px] overflow-y-auto">
          <div className="prose prose-sm dark:prose-invert max-w-none">
            <pre className="whitespace-pre-wrap text-xs text-zinc-700 dark:text-zinc-300 font-mono bg-zinc-50 dark:bg-zinc-800/50 p-4 rounded-lg border border-zinc-200 dark:border-zinc-700">
              {plan.plan}
            </pre>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="p-2 border-t border-zinc-100 dark:border-zinc-800">
          <div className="grid grid-cols-3 gap-2">
            <button
              type="button"
              className={cn(
                "flex items-center justify-center gap-2",
                "py-2 px-3 rounded-lg",
                "text-xs font-medium",
                "bg-zinc-900 dark:bg-zinc-50",
                "text-zinc-50 dark:text-zinc-900",
                "hover:bg-zinc-800 dark:hover:bg-zinc-200",
                "shadow-sm hover:shadow",
                "transition-all duration-200",
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
                "bg-zinc-900 dark:bg-zinc-50",
                "text-zinc-50 dark:text-zinc-900",
                "hover:bg-zinc-800 dark:hover:bg-zinc-200",
                "shadow-sm hover:shadow",
                "transition-all duration-200",
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
                "bg-zinc-900 dark:bg-zinc-50",
                "text-zinc-50 dark:text-zinc-900",
                "hover:bg-zinc-800 dark:hover:bg-zinc-200",
                "shadow-sm hover:shadow",
                "transition-all duration-200",
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

  // Default view when no plan is available
  return (
    <div
      className={cn(
        "w-full max-w-xl mx-auto",
        "bg-white dark:bg-zinc-900/70",
        "border border-zinc-100 dark:border-zinc-800",
        "rounded-xl shadow-sm backdrop-blur-xl",
        className,
      )}
    >
      {/* Total Balance Section */}
      <div className="p-4 border-b border-zinc-100 dark:border-zinc-800">
        <p className="text-xs text-zinc-600 dark:text-zinc-400">Total Balance</p>
        <h1 className="text-2xl font-semibold text-zinc-900 dark:text-zinc-50">{totalBalance}</h1>
      </div>

      {/* Specs List */}
      <div className="p-3">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-xs font-medium text-zinc-900 dark:text-zinc-100">Plan Specifications</h2>
        </div>

        <div className="space-y-2">
          {specs.map((spec) => (
            <div
              key={spec.id}
              className={cn(
                "group flex items-center justify-between",
                "p-3 rounded-lg",
                "bg-zinc-50 dark:bg-zinc-800/50",
                "hover:bg-zinc-100 dark:hover:bg-zinc-800",
                "border border-zinc-200 dark:border-zinc-700",
                "transition-all duration-200",
              )}
            >
              <div className="flex items-center gap-3">
                <div
                  className={cn("p-2 rounded-lg", {
                    "bg-purple-100 dark:bg-purple-900/30": spec.type === "gpu",
                    "bg-blue-100 dark:bg-blue-900/30": spec.type === "cpu",
                    "bg-cyan-100 dark:bg-cyan-900/30": spec.type === "memory",
                    "bg-emerald-100 dark:bg-emerald-900/30": spec.type === "cost",
                    "bg-orange-100 dark:bg-orange-900/30": spec.type === "runtime",
                    "bg-amber-100 dark:bg-amber-900/30": spec.type === "risk",
                  })}
                >
                  {spec.type === "gpu" && <Cpu className="w-4 h-4 text-purple-600 dark:text-purple-400" />}
                  {spec.type === "cpu" && <Cpu className="w-4 h-4 text-blue-600 dark:text-blue-400" />}
                  {spec.type === "memory" && <MemoryStick className="w-4 h-4 text-cyan-600 dark:text-cyan-400" />}
                  {spec.type === "cost" && <DollarSign className="w-4 h-4 text-emerald-600 dark:text-emerald-400" />}
                  {spec.type === "runtime" && <Clock className="w-4 h-4 text-orange-600 dark:text-orange-400" />}
                  {spec.type === "risk" && <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400" />}
                </div>
                <div>
                  <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100">{spec.title}</h3>
                  {spec.description && <p className="text-xs text-zinc-600 dark:text-zinc-400">{spec.description}</p>}
                </div>
              </div>
              <span className="text-sm font-semibold text-zinc-900 dark:text-zinc-100">{spec.value}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="p-2 border-t border-zinc-100 dark:border-zinc-800">
        <div className="grid grid-cols-3 gap-2">
          <button
            type="button"
            className={cn(
              "flex items-center justify-center gap-2",
              "py-2 px-3 rounded-lg",
              "text-xs font-medium",
              "bg-zinc-900 dark:bg-zinc-50",
              "text-zinc-50 dark:text-zinc-900",
              "hover:bg-zinc-800 dark:hover:bg-zinc-200",
              "shadow-sm hover:shadow",
              "transition-all duration-200",
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
              "bg-zinc-900 dark:bg-zinc-50",
              "text-zinc-50 dark:text-zinc-900",
              "hover:bg-zinc-800 dark:hover:bg-zinc-200",
              "shadow-sm hover:shadow",
              "transition-all duration-200",
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
              "bg-zinc-900 dark:bg-zinc-50",
              "text-zinc-50 dark:text-zinc-900",
              "hover:bg-zinc-800 dark:hover:bg-zinc-200",
              "shadow-sm hover:shadow",
              "transition-all duration-200",
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
