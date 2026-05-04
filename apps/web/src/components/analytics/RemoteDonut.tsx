/**
 * Remote vs onsite donut chart
 * Shows remote work distribution
 */

"use client"

import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts"
import { RemoteVsOnsite } from "@/lib/types"

interface RemoteDonutProps {
  data: RemoteVsOnsite
}

export function RemoteDonut({ data }: RemoteDonutProps) {
  const chartData = [
    { name: "Remote", value: data.remote, fill: "#10b981" },
    { name: "On-site", value: data.onsite, fill: "#3b82f6" }
  ]

  return (
    <div className="w-full">
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={40}
            outerRadius={70}
            paddingAngle={2}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.fill} />
            ))}
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      
      {/* Center label */}
      <div className="text-center -mt-16">
        <div className="text-xl font-bold">{data.remote_percentage}%</div>
        <div className="text-sm text-muted-foreground">Work from home</div>
      </div>

      {/* Legend */}
      <div className="mt-4 flex justify-center gap-4">
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-green-500" />
          <span className="text-sm">Remote: {data.remote}</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 rounded-full bg-blue-500" />
          <span className="text-sm">On-site: {data.onsite}</span>
        </div>
      </div>
    </div>
  )
}
