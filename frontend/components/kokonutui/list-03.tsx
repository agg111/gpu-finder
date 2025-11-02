import { cn } from "@/lib/utils"
import {
  type LucideIcon,
  ArrowRight,
  CheckCircle2,
  AlertCircle,
  PiggyBank,
  TrendingUp,
  CreditCard,
  Clock,
  Calendar,
} from "lucide-react"
import React from "react"

interface ListItem {
  id: string
  title: string
  subtitle: string
  icon: LucideIcon
  iconStyle: string
  status: "scheduled" | "in-progress" | "completed"
  progress?: number
  date: string
  time: string
}

interface List03Props {
  items?: ListItem[]
  className?: string
}

const iconStyles = {
  savings: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
  investment: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
  debt: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
}

const statusConfig = {
  scheduled: {
    icon: Clock,
    class: "text-purple-600 dark:text-purple-400",
    bg: "bg-purple-100 dark:bg-purple-900/30",
  },
  "in-progress": {
    icon: AlertCircle,
    class: "text-blue-600 dark:text-blue-400",
    bg: "bg-blue-100 dark:bg-blue-900/30",
  },
  completed: {
    icon: CheckCircle2,
    class: "text-emerald-600 dark:text-emerald-400",
    bg: "bg-emerald-100 dark:bg-emerald-900/30",
  },
}

const ITEMS: ListItem[] = [
  {
    id: "1",
    title: "GPT-4",
    subtitle: "Workload size: 1.2TB dataset",
    icon: PiggyBank,
    iconStyle: "savings",
    status: "in-progress",
    progress: 65,
    date: "Nov 2, 2025",
    time: "4:00 PM",
  },
  {
    id: "2",
    title: "BERT-Large",
    subtitle: "Workload size: 500GB dataset",
    icon: TrendingUp,
    iconStyle: "investment",
    status: "scheduled",
    progress: 0,
    date: "Nov 4, 2025",
    time: "10:00 AM",
  },
  {
    id: "3",
    title: "ResNet-50",
    subtitle: "Workload size: 800GB dataset",
    icon: CreditCard,
    iconStyle: "debt",
    status: "completed",
    progress: 100,
    date: "Oct 24, 2025",
    time: "4:45 PM",
  },
]

export default function List03({ items = ITEMS, className }: List03Props) {
  return (
    <div className={cn("w-full overflow-x-auto scrollbar-none", className)}>
      <div className="flex gap-3 min-w-full p-1">
        {items.map((item) => (
          <div
            key={item.id}
            className={cn(
              "flex flex-col",
              "w-[280px] shrink-0",
              "bg-white dark:bg-zinc-900/70",
              "rounded-xl",
              "border border-zinc-100 dark:border-zinc-800",
              "hover:border-zinc-200 dark:hover:border-zinc-700",
              "transition-all duration-200",
              "shadow-sm backdrop-blur-xl",
            )}
          >
            <div className="p-4 space-y-3">
              <div className="flex items-start justify-between">
                <div className={cn("p-2 rounded-lg", iconStyles[item.iconStyle as keyof typeof iconStyles])}>
                  <item.icon className="w-4 h-4" />
                </div>
                <div
                  className={cn(
                    "px-2 py-1 rounded-full text-xs font-medium flex items-center gap-1.5",
                    statusConfig[item.status].bg,
                    statusConfig[item.status].class,
                  )}
                >
                  {React.createElement(statusConfig[item.status].icon, { className: "w-3.5 h-3.5" })}
                  {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
                </div>
              </div>

              <div>
                <h3 className="text-sm font-medium text-zinc-900 dark:text-zinc-100 mb-1">{item.title}</h3>
                <p className="text-xs text-zinc-600 dark:text-zinc-400 line-clamp-2">{item.subtitle}</p>
              </div>

              <div className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-400">
                <Calendar className="w-3.5 h-3.5" />
                <span>{item.date}</span>
                <span>•</span>
                <Clock className="w-3.5 h-3.5" />
                <span>{item.time}</span>
              </div>

              {typeof item.progress === "number" && (
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-zinc-600 dark:text-zinc-400">Progress</span>
                    <span className="text-zinc-900 dark:text-zinc-100">{item.progress}%</span>
                  </div>
                  <div className="h-1.5 bg-zinc-100 dark:bg-zinc-800 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-zinc-900 dark:bg-zinc-100 rounded-full"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                </div>
              )}
            </div>

            <div className="mt-auto border-t border-zinc-100 dark:border-zinc-800">
              <button
                className={cn(
                  "w-full flex items-center justify-center gap-2",
                  "py-2.5 px-3",
                  "text-xs font-medium",
                  "text-zinc-600 dark:text-zinc-400",
                  "hover:text-zinc-900 dark:hover:text-zinc-100",
                  "hover:bg-zinc-100 dark:hover:bg-zinc-800/50",
                  "transition-colors duration-200",
                )}
              >
                View Details
                <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
