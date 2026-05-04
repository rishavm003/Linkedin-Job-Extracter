/**
 * Top skills horizontal bar chart
 * Shows most in-demand skills
 */

"use client"

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts"
import { SkillInfo } from "@/lib/types"
import { useRouter } from "next/navigation"

interface TopSkillsBarProps {
  data: SkillInfo[]
  limit?: number
}

export function TopSkillsBar({ data, limit = 15 }: TopSkillsBarProps) {
  const router = useRouter()

  const handleBarClick = (entry: any) => {
    if (entry && entry.skill) {
      router.push(`/jobs?skills=${encodeURIComponent(entry.skill)}`)
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg p-2 shadow-lg">
          <p className="font-medium">{data.skill}</p>
          <p className="text-sm text-muted-foreground">
            {data.count} jobs
          </p>
        </div>
      )
    }
    return null
  }

  const chartData = data.slice(0, limit)

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={400}>
        <BarChart
          data={chartData}
          layout="horizontal"
          margin={{ top: 5, right: 30, left: 80, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
          <XAxis type="number" />
          <YAxis 
            dataKey="skill" 
            type="category"
            tick={{ fontSize: 12 }}
            width={70}
          />
          <Tooltip content={<CustomTooltip />} />
          <Bar 
            dataKey="count" 
            fill="#378ADD"
            onClick={handleBarClick}
            className="cursor-pointer"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill="#378ADD" />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
