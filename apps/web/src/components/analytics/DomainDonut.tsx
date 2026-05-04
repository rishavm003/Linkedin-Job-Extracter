/**
 * Domain distribution donut chart
 * Shows job distribution by domain
 */

"use client"

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from "recharts"
import { DomainDistribution } from "@/lib/types"
import { domainColor } from "@/lib/utils"
import { useRouter } from "next/navigation"

interface DomainDonutProps {
  data: DomainDistribution[]
}

export function DomainDonut({ data }: DomainDonutProps) {
  const router = useRouter()

  const handleSliceClick = (entry: any) => {
    if (entry && entry.domain) {
      router.push(`/jobs?domain=${encodeURIComponent(entry.domain)}`)
    }
  }

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-background border rounded-lg p-2 shadow-lg">
          <p className="font-medium">{data.domain}</p>
          <p className="text-sm text-muted-foreground">
            {data.count} jobs ({data.percentage}%)
          </p>
        </div>
      )
    }
    return null
  }

  const totalJobs = data.reduce((sum, item) => sum + item.count, 0)

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={100}
            paddingAngle={2}
            dataKey="count"
            onClick={handleSliceClick}
            className="cursor-pointer"
          >
            {data.map((entry, index) => (
              <Cell 
                key={`cell-${index}`} 
                fill={domainColor(entry.domain)}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>
      
      {/* Center label */}
      <div className="text-center -mt-20">
        <div className="text-2xl font-bold">{totalJobs}</div>
        <div className="text-sm text-muted-foreground">Total Jobs</div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-2 justify-center">
        {data.map((entry) => (
          <div
            key={entry.domain}
            className="flex items-center gap-2 cursor-pointer hover:opacity-80"
            onClick={() => handleSliceClick(entry)}
          >
            <div
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: domainColor(entry.domain) }}
            />
            <span className="text-sm">{entry.domain}</span>
            <span className="text-xs text-muted-foreground">
              ({entry.count})
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}
