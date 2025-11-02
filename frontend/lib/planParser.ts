/**
 * Parser utility to extract structured data from GPU execution plan text
 */

export interface GPUConfiguration {
  rank: number
  name: string
  provider: string
  instanceType: string
  gpuCount: number
  gpuType: string
  gpuMemory: string
  vcpus: string
  ram: string
  storage?: string
  costPerHour: number
  expectedRuntime: string
  regions: string[]
  availability: string
  totalCost?: number
  riskAssessment: {
    availability: string
    deadlineFeasibility: string
    budgetConstraints: string
  }
  useCase: string
}

export interface ParsedPlan {
  configurations: GPUConfiguration[]
  rawPlan: string
  summary?: string
}

/**
 * Parse the plan text and extract structured GPU configurations
 */
export function parsePlan(planText: string): ParsedPlan {
  const configurations: GPUConfiguration[] = []

  // Split by configuration sections (looking for "Configuration X:")
  const configRegex = /#### Configuration (\d+): (.+?)\n([\s\S]*?)(?=#### Configuration \d+:|### Conclusion|$)/g

  let match
  while ((match = configRegex.exec(planText)) !== null) {
    const rank = parseInt(match[1])
    const name = match[2].trim()
    const content = match[3]

    try {
      const config = parseConfiguration(rank, name, content)
      configurations.push(config)
    } catch (error) {
      console.error(`Failed to parse configuration ${rank}:`, error)
    }
  }

  return {
    configurations,
    rawPlan: planText,
    summary: extractSummary(planText)
  }
}

function parseConfiguration(rank: number, name: string, content: string): GPUConfiguration {
  // Extract provider and instance type from name
  const [provider, ...instanceParts] = name.split(' ')
  const instanceType = instanceParts.join(' ')

  // Extract GPU info
  const gpuMatch = content.match(/GPU Count and Type[:\s]+(.+?)(?:\n|$)/i)
  const gpuInfo = gpuMatch ? gpuMatch[1].trim() : ''
  const [gpuCountStr, ...gpuTypeParts] = gpuInfo.split('x ')
  const gpuCount = parseInt(gpuCountStr) || 1
  const gpuTypeMatch = gpuTypeParts.join('').match(/NVIDIA ([A-Z0-9]+)\s*\(([^)]+)\)/)
  const gpuType = gpuTypeMatch ? gpuTypeMatch[1] : 'Unknown'
  const gpuMemory = gpuTypeMatch ? gpuTypeMatch[2] : 'Unknown'

  // Extract specs
  const specsMatch = content.match(/CPU, SSD, Memory Configuration[:\s]+(.+?)(?:\n|$)/i)
  const specs = specsMatch ? specsMatch[1].trim() : ''
  const vcpusMatch = specs.match(/(\d+)\s*vCPUs?/)
  const ramMatch = specs.match(/(\d+)\s*GB RAM/)
  const storageMatch = specs.match(/(\d+x?\s*\d*\s*GB.*?(?:NVMe|SSD))/)

  const vcpus = vcpusMatch ? vcpusMatch[1] : 'Unknown'
  const ram = ramMatch ? ramMatch[1] + ' GB' : 'Unknown'
  const storage = storageMatch ? storageMatch[1] : undefined

  // Extract cost
  const costMatch = content.match(/Cost Estimate[:\s]+\$?([\d.]+)\s*per hour/i)
  const costPerHour = costMatch ? parseFloat(costMatch[1]) : 0

  const totalCostMatch = content.match(/Total cost estimated at \$?([\d,]+(?:\.\d+)?)/i)
  const totalCost = totalCostMatch ? parseFloat(totalCostMatch[1].replace(',', '')) : undefined

  // Extract runtime
  const runtimeMatch = content.match(/Expected Runtime[:\s]+(?:Estimated )?(.+?)(?:\n|$)/i)
  const expectedRuntime = runtimeMatch ? runtimeMatch[1].trim() : 'Unknown'

  // Extract regions
  const regionsMatch = content.match(/Region\/Availability[:\s]+(.+?)(?:,\s*generally available|,\s*limited availability|\n|$)/i)
  const regionsStr = regionsMatch ? regionsMatch[1].trim() : ''
  const regions = regionsStr.split(/,\s*/).filter(r => r.length > 0)

  // Extract availability
  const availabilityMatch = content.match(/Region\/Availability[:\s]+.+?(generally available|limited availability|high|low risk)/i)
  const availability = availabilityMatch ? availabilityMatch[1].trim() : 'Unknown'

  // Extract risk assessment
  const availabilityRiskMatch = content.match(/Availability[:\s]+(.+?)(?:\n|$)/im)
  const deadlineRiskMatch = content.match(/Deadline Feasibility[:\s]+(.+?)(?:\n|$)/im)
  const budgetRiskMatch = content.match(/Budget Constraints[:\s]+(.+?)(?:\n|$)/im)

  const riskAssessment = {
    availability: availabilityRiskMatch ? availabilityRiskMatch[1].trim() : 'Unknown',
    deadlineFeasibility: deadlineRiskMatch ? deadlineRiskMatch[1].trim() : 'Unknown',
    budgetConstraints: budgetRiskMatch ? budgetRiskMatch[1].trim() : 'Unknown'
  }

  // Extract use case (if mentioned)
  const useCaseMatch = content.match(/Use Case[:\s]+(.+?)(?:\n|$)/i)
  const useCase = useCaseMatch ? useCaseMatch[1].trim() : 'General ML training'

  return {
    rank,
    name,
    provider,
    instanceType,
    gpuCount,
    gpuType,
    gpuMemory,
    vcpus,
    ram,
    storage,
    costPerHour,
    expectedRuntime,
    regions,
    availability,
    totalCost,
    riskAssessment,
    useCase
  }
}

function extractSummary(planText: string): string {
  const conclusionMatch = planText.match(/### Conclusion\n+([\s\S]+?)$/i)
  return conclusionMatch ? conclusionMatch[1].trim() : ''
}

/**
 * Format cost for display
 */
export function formatCost(cost: number): string {
  return `$${cost.toFixed(2)}`
}

/**
 * Get risk level badge color
 */
export function getRiskColor(risk: string): 'green' | 'yellow' | 'red' {
  const lowerRisk = risk.toLowerCase()
  if (lowerRisk.includes('low') || lowerRisk.includes('meets') || lowerRisk.includes('within')) {
    return 'green'
  }
  if (lowerRisk.includes('medium') || lowerRisk.includes('limited')) {
    return 'yellow'
  }
  return 'red'
}
