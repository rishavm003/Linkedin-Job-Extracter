/**
 * Trending skills list component
 * Shows trending skills with change indicators
 */

import { TrendingSkill } from "@/lib/types"
import { TrendingUp, TrendingDown, Minus } from "lucide-react"

interface TrendingSkillsProps {
  data: TrendingSkill[]
}

export function TrendingSkills({ data }: TrendingSkillsProps) {
  const getChangeIcon = (changePct: number) => {
    if (changePct > 0) {
      return <TrendingUp className="h-4 w-4 text-green-500" />
    } else if (changePct < 0) {
      return <TrendingDown className="h-4 w-4 text-red-500" />
    } else {
      return <Minus className="h-4 w-4 text-gray-500" />
    }
  }

  const getChangeText = (changePct: number) => {
    if (changePct > 0) {
      return `+${changePct}%`
    } else if (changePct < 0) {
      return `${changePct}%`
    } else {
      return "—"
    }
  }

  const getChangeColor = (changePct: number) => {
    if (changePct > 0) {
      return "text-green-500"
    } else if (changePct < 0) {
      return "text-red-500"
    } else {
      return "text-gray-500"
    }
  }

  const topSkills = data.slice(0, 10)

  return (
    <div className="space-y-3">
      {topSkills.map((skill, index) => (
        <div key={skill.skill} className="flex items-center justify-between p-3 rounded-lg border">
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-muted-foreground w-6">
              {index + 1}
            </span>
            <span className="font-medium">{skill.skill}</span>
          </div>
          
          <div className="flex items-center gap-4">
            <div className="text-right">
              <div className="font-medium">{skill.count_this_week}</div>
              <div className="text-xs text-muted-foreground">this week</div>
            </div>
            
            <div className="flex items-center gap-1">
              {getChangeIcon(skill.change_pct)}
              <span className={`text-sm font-medium ${getChangeColor(skill.change_pct)}`}>
                {getChangeText(skill.change_pct)}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
