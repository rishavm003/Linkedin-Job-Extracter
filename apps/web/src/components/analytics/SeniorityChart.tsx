/**
 * Seniority breakdown vertical bar chart
 * Shows job distribution by experience level
 */

"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { SeniorityBreakdown } from "@/lib/types"
import { SENIORITY_ORDER } from "@/lib/constants"

interface SeniorityChartProps {
  data: SeniorityBreakdown[]
}

export function SeniorityChart({ data }: SeniorityChartProps) {
  const getSeniorityColor = (seniority: string) => {
    switch (seniority.toLowerCase()) {
      case "fresher":
        return "#10b981"
      case "intern":
        return "#14b8a6"
      case "entry level":
        return "#3b82f6"
      case "junior":
        return "#8b5cf6"
      case "mid level":
        return "#f59e0b"
      case "senior":
        return "#f97316"
      default:
        return "#6b7280"
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg p-2 shadow-lg">
          <p className="font-medium">{data.seniority}</p>
          <p className="text-sm text-muted-foreground">
            {data.count} jobs ({data.percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  // Order data by SENIORITY_ORDER
  const orderedData = SENIORITY_ORDER
    .map(level => data.find(item => item.seniority === level))
    .filter(Boolean) as SeniorityBreakdown[]

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={orderedData} margin={{ top: 5, right: 30, left: 5, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="seniority" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[4, 4, 0, 0]}>
            {orderedData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={getSeniorityColor(entry.seniority)} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
