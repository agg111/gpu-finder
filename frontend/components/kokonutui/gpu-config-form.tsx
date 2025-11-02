"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { ChevronDown, Loader2, AlertCircle, CheckCircle } from "lucide-react"
import { createPlan, type PlanResponse } from "@/lib/api"

interface GPUConfigFormValues {
  modelName: string
  workload: string
  duration: string
  budget: string
  startDateTime: string
  precision: string
  framework: string
}

interface GPUConfigFormProps {
  onPlanCreated?: (plan: PlanResponse) => void
}

export default function GPUConfigForm({ onPlanCreated }: GPUConfigFormProps) {
  const [isOpen, setIsOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [progressMessage, setProgressMessage] = useState<string>("")

  const form = useForm<GPUConfigFormValues>({
    defaultValues: {
      modelName: "",
      workload: "",
      duration: "",
      budget: "",
      startDateTime: "",
      precision: "",
      framework: "",
    },
  })

  async function onSubmit(data: GPUConfigFormValues) {
    setIsLoading(true)
    setError(null)
    setSuccess(null)
    setProgressMessage("Initializing plan creation...")

    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

    try {
      const requestBody = {
        modelName: data.modelName,
        workload: data.workload,
        duration: data.duration,
        budget: data.budget || undefined,
        startDateTime: data.startDateTime || undefined,
        precision: data.precision || undefined,
        framework: data.framework || undefined,
      }

      // Use SSE streaming for real-time progress updates
      const response = await fetch(`${API_BASE_URL}/api/plan/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail?.message || 'Failed to create plan')
      }

      // Read SSE stream
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      if (!reader) {
        throw new Error('No response body')
      }

      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()

        if (done) {
          break
        }

        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true })

        // Process complete SSE messages (ending with \n\n)
        const messages = buffer.split('\n\n')
        buffer = messages.pop() || '' // Keep incomplete message in buffer

        for (const message of messages) {
          if (!message.trim() || !message.startsWith('data: ')) {
            continue
          }

          try {
            const jsonData = JSON.parse(message.slice(6)) // Remove "data: " prefix

            if (jsonData.type === 'status') {
              // Update progress message
              setProgressMessage(`${jsonData.message} (${jsonData.elapsed.toFixed(1)}s elapsed)`)
            } else if (jsonData.type === 'result') {
              // Final result received
              const result = jsonData.data
              setSuccess(`Plan created successfully in ${result.duration_seconds.toFixed(1)}s!`)

              // Notify parent component
              if (onPlanCreated) {
                onPlanCreated(result)
              }
            } else if (jsonData.type === 'error') {
              throw new Error(jsonData.message)
            }
          } catch (parseError) {
            console.error('Error parsing SSE message:', parseError)
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : "Failed to create plan. Please try again."
      setError(errorMessage)
      console.error("Error creating plan:", err)
    } finally {
      setIsLoading(false)
      setProgressMessage("")
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <FormField
            control={form.control}
            name="modelName"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-900 dark:text-white">Model Name</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g., meta-llama/Llama-2-7b-hf"
                    className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="workload"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-900 dark:text-white">Workload Size</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g., 500GB"
                    className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="duration"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-900 dark:text-white">Duration</FormLabel>
                <FormControl>
                  <Input
                    placeholder="e.g., 24"
                    className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="budget"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-900 dark:text-white">Budget</FormLabel>
                <FormControl>
                  <Input
                    type="number"
                    placeholder="e.g., 500"
                    className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />

          <FormField
            control={form.control}
            name="startDateTime"
            render={({ field }) => (
              <FormItem>
                <FormLabel className="text-gray-900 dark:text-white">Start Date & Time</FormLabel>
                <FormControl>
                  <Input
                    type="datetime-local"
                    className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white"
                    {...field}
                  />
                </FormControl>
                <FormMessage />
              </FormItem>
            )}
          />
        </div>

        <Collapsible open={isOpen} onOpenChange={setIsOpen}>
          <CollapsibleTrigger asChild>
            <Button
              type="button"
              variant="ghost"
              className="flex items-center gap-2 text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white p-0"
            >
              <span className="text-sm font-medium">Advanced Options</span>
              <ChevronDown className={`h-4 w-4 transition-transform duration-200 ${isOpen ? "rotate-180" : ""}`} />
            </Button>
          </CollapsibleTrigger>
          <CollapsibleContent className="pt-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="precision"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-900 dark:text-white">Precision</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white">
                          <SelectValue placeholder="Select precision" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="fp32">FP32 (32-bit floating point)</SelectItem>
                        <SelectItem value="fp16">FP16 (16-bit floating point)</SelectItem>
                        <SelectItem value="bf16">BF16 (Brain Float 16)</SelectItem>
                        <SelectItem value="int8">INT8 (8-bit integer)</SelectItem>
                        <SelectItem value="int4">INT4 (4-bit integer)</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="framework"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel className="text-gray-900 dark:text-white">Framework</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger className="bg-white dark:bg-[#18181B] border-gray-200 dark:border-[#27272A] text-gray-900 dark:text-white">
                          <SelectValue placeholder="Select framework" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="pytorch">PyTorch</SelectItem>
                        <SelectItem value="tensorflow">TensorFlow</SelectItem>
                        <SelectItem value="jax">JAX</SelectItem>
                        <SelectItem value="mxnet">MXNet</SelectItem>
                        <SelectItem value="onnx">ONNX Runtime</SelectItem>
                        <SelectItem value="triton">Triton</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>
          </CollapsibleContent>
        </Collapsible>

        {/* Status Messages */}
        {error && (
          <div className="flex items-center gap-2 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
            <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400" />
            <p className="text-sm text-red-600 dark:text-red-400">{error}</p>
          </div>
        )}

        {success && (
          <div className="flex items-center gap-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-md">
            <CheckCircle className="h-4 w-4 text-green-600 dark:text-green-400" />
            <p className="text-sm text-green-600 dark:text-green-400">{success}</p>
          </div>
        )}

        {isLoading && (
          <div className="flex items-center gap-2 p-3 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-md">
            <Loader2 className="h-4 w-4 text-blue-600 dark:text-blue-400 animate-spin" />
            <p className="text-sm text-blue-600 dark:text-blue-400">
              {progressMessage || "Creating your GPU execution plan..."}
            </p>
          </div>
        )}

        <div className="flex justify-end">
          <Button
            type="submit"
            className="bg-blue-600 hover:bg-blue-700 text-white disabled:opacity-50 disabled:cursor-not-allowed"
            disabled={isLoading}
          >
            {isLoading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Building Plan...
              </>
            ) : (
              "Build Plan"
            )}
          </Button>
        </div>
      </form>
    </Form>
  )
}
