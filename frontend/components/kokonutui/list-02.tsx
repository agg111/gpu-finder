import { cn } from "@/lib/utils"
import { ArrowUpRight, ArrowDownLeft, Cpu, Zap, Activity, Database, type LucideIcon, ArrowRight } from "lucide-react"

interface Transaction {
  id: string
  title: string
  modelName: string
  workload: string
  amount: string
  type: "incoming" | "outgoing"
  category: string
  icon: LucideIcon
  timestamp: string
  status: "completed" | "pending" | "failed"
}

interface List02Props {
  plans?: Transaction[]
  className?: string
}

const categoryStyles = {
  shopping: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
  food: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
  transport: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
  entertainment: "bg-zinc-100 dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100",
}

const TRANSACTIONS: Transaction[] = [
  {
    id: "1",
    title: "GPT-4 Training",
    modelName: "GPT-4",
    workload: "Training - Large Dataset",
    amount: "$245.50",
    type: "outgoing",
    category: "shopping",
    icon: Cpu,
    timestamp: "Today, 2:45 PM",
    status: "completed",
  },
  {
    id: "2",
    title: "BERT-Large Inference",
    modelName: "BERT-Large",
    workload: "Inference - Batch Processing",
    amount: "$89.00",
    type: "outgoing",
    category: "transport",
    icon: Zap,
    timestamp: "Today, 9:00 AM",
    status: "completed",
  },
  {
    id: "3",
    title: "ResNet-50 Fine-tuning",
    modelName: "ResNet-50",
    workload: "Fine-tuning - Image Classification",
    amount: "$125.99",
    type: "outgoing",
    category: "entertainment",
    icon: Activity,
    timestamp: "Yesterday",
    status: "pending",
  },
  {
    id: "4",
    title: "LLaMA-2 Training",
    modelName: "LLaMA-2",
    workload: "Training - Custom Dataset",
    amount: "$310.00",
    type: "outgoing",
    category: "shopping",
    icon: Cpu,
    timestamp: "2 days ago",
    status: "completed",
  },
  {
    id: "5",
    title: "Stable Diffusion Inference",
    modelName: "Stable Diffusion",
    workload: "Inference - Image Generation",
    amount: "$67.50",
    type: "outgoing",
    category: "entertainment",
    icon: Database,
    timestamp: "3 days ago",
    status: "pending",
  },
  {
    id: "6",
    title: "YOLO-v8 Training",
    modelName: "YOLO-v8",
    workload: "Training - Object Detection",
    amount: "$198.00",
    type: "outgoing",
    category: "entertainment",
    icon: Activity,
    timestamp: "4 days ago",
    status: "completed",
  },
]

export default function List02({ plans = TRANSACTIONS, className }: List02Props) {
  return (
    <div
      className={cn(
        "w-full",
        "bg-white dark:bg-zinc-900/70",
        "border border-zinc-100 dark:border-zinc-800",
        "rounded-xl shadow-sm backdrop-blur-xl",
        className,
      )}
    >
      <div className="p-4">
        <div className="space-y-1">
          {plans.map((transaction) => (
            <div
              key={transaction.id}
              className={cn(
                "group flex items-center gap-3",
                "p-2 rounded-lg",
                "hover:bg-zinc-100 dark:hover:bg-zinc-800/50",
                "transition-all duration-200",
              )}
            >
              <div
                className={cn(
                  "p-2 rounded-lg",
                  "bg-zinc-100 dark:bg-zinc-800",
                  "border border-zinc-200 dark:border-zinc-700",
                )}
              >
                <transaction.icon className="w-4 h-4 text-zinc-900 dark:text-zinc-100" />
              </div>

              <div className="flex-1 flex items-center justify-between min-w-0">
                <div className="space-y-0.5">
                  <h3 className="text-xs font-medium text-zinc-900 dark:text-zinc-100">{transaction.modelName}</h3>
                  <p className="text-[11px] text-zinc-600 dark:text-zinc-400">{transaction.workload}</p>
                </div>

                <div className="flex items-center gap-1.5 pl-3">
                  <span
                    className={cn(
                      "text-xs font-medium",
                      transaction.type === "incoming"
                        ? "text-emerald-600 dark:text-emerald-400"
                        : "text-red-600 dark:text-red-400",
                    )}
                  >
                    {transaction.type === "incoming" ? "+" : "-"}
                    {transaction.amount}
                  </span>
                  {transaction.type === "incoming" ? (
                    <ArrowDownLeft className="w-3.5 h-3.5 text-emerald-600 dark:text-emerald-400" />
                  ) : (
                    <ArrowUpRight className="w-3.5 h-3.5 text-red-600 dark:text-red-400" />
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="p-2 border-t border-zinc-100 dark:border-zinc-800">
        <button
          type="button"
          className={cn(
            "w-full flex items-center justify-center gap-2",
            "py-2 px-3 rounded-lg",
            "text-xs font-medium",
            "text-zinc-600 dark:text-zinc-400",
            "hover:text-zinc-900 dark:hover:text-zinc-100",
            "hover:bg-zinc-100 dark:hover:bg-zinc-800/50",
            "border border-zinc-200 dark:border-zinc-800",
            "transition-colors duration-200",
          )}
        >
          <span>View All Plans</span>
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  )
}
