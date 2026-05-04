/**
 * Salary range grouped bar chart
 * Shows average salary ranges by domain
 */

"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts"
import { SalaryRange } from "@/lib/types"

interface SalaryRangeChartProps {
  data: SalaryRange[]
}

export function SalaryRangeChart({ data }: SalaryRangeChartProps) {
  // Filter out domains with no salary data
  const chartData = data.filter(item => item.avg_min !== null)

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-background border rounded-lg p-2 shadow-lg">
          <p className="font-medium">{payload[0].payload.domain}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm text-muted-foreground">
              {entry.name}: {entry.currency} {entry.value}L
            </p>
          ))}
        </div>
      )
    }
    return null
  }

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis 
            dataKey="domain" 
            tick={{ fontSize: 12 }}
            angle={-45}
            textAnchor="end"
            height={60}
          />
          <YAxis 
            tick={{ fontSize: 12 }}
            label={{ value: "Salary (LPA)", angle: -90, position: "insideLeft" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend />
          <Bar 
            dataKey="avg_min" 
            fill="#93c5fd" 
            name="Min Salary"
            radius={[4, 4, 0, 0]}
          />
          <Bar 
            dataKey="avg_max" 
            fill="#3b82f6" 
            name="Max Salary"
            radius={[4, 4, 0, 0]}
          />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
