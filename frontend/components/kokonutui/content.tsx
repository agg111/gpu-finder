"use client"

import { useState } from "react"
import { Calendar, CreditCard, Cpu, BarChart3 } from "lucide-react"
import List01 from "./list-01"
import List02 from "./list-02"
import List03 from "./list-03"
import GPUConfigForm from "./gpu-config-form"
import type { PlanResponse } from "@/lib/api"

export default function Content() {
  const [currentPlan, setCurrentPlan] = useState<PlanResponse | null>(null)

  const handlePlanCreated = (plan: PlanResponse) => {
    setCurrentPlan(plan)
  }

  return (
    <div className="space-y-4">
      <div className="bg-white dark:bg-[#0F0F12] rounded-xl p-6 flex flex-col border border-gray-200 dark:border-[#1F1F23]">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-left flex items-center gap-2">
          <Cpu className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-50" />
          Workload Configuration
        </h2>
        <GPUConfigForm onPlanCreated={handlePlanCreated} />
      </div>

      <div className="bg-white dark:bg-[#0F0F12] rounded-xl p-6 flex flex-col border border-gray-200 dark:border-[#1F1F23]">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-left flex items-center gap-2 ">
          <BarChart3 className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-50" />
          Plan Specs
        </h2>
        <div className="flex-1">
          <List01 className="h-full" plan={currentPlan} />
        </div>
      </div>

      <div className="bg-white dark:bg-[#0F0F12] rounded-xl p-6 flex flex-col border border-gray-200 dark:border-[#1F1F23]">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-left flex items-center gap-2">
          <CreditCard className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-50" />
          Recent Plans
        </h2>
        <div className="flex-1">
          <List02 className="h-full" />
        </div>
      </div>

      <div className="bg-white dark:bg-[#0F0F12] rounded-xl p-6 flex flex-col items-start justify-start border border-gray-200 dark:border-[#1F1F23]">
        <h2 className="text-lg font-bold text-gray-900 dark:text-white mb-4 text-left flex items-center gap-2">
          <Calendar className="w-3.5 h-3.5 text-zinc-900 dark:text-zinc-50" />
          Plan Status
        </h2>
        <List03 />
        <button className="mt-4 w-full py-2 px-4 text-sm font-medium text-zinc-600 dark:text-zinc-400 hover:text-zinc-900 dark:hover:text-zinc-100 hover:bg-zinc-100 dark:hover:bg-zinc-800/50 rounded-lg transition-colors duration-200 border border-zinc-200 dark:border-zinc-800">
          View All
        </button>
      </div>
    </div>
  )
}
