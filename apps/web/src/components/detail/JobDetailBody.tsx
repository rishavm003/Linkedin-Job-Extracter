/**
 * Job detail body component
 * Shows job description, skills, and qualifications
 */

import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"
import { JobDetail } from "@/lib/types"
import { SkillPill } from "@/components/ui/SkillPill"

interface JobDetailBodyProps {
  job: JobDetail
}

export function JobDetailBody({ job }: JobDetailBodyProps) {
  const handleSkillClick = (skill: string) => {
    window.location.href = `/jobs?skills=${encodeURIComponent(skill)}`
  }

  return (
    <div className="space-y-8">
      {/* About this role */}
      <section>
        <h2 className="text-xl font-semibold mb-4">About this role</h2>
        <div className="prose prose-sm max-w-none">
          {job.description_clean.split('\n\n').map((paragraph, index) => (
            <p key={index} className="mb-4 text-muted-foreground leading-relaxed">
              {paragraph}
            </p>
          ))}
        </div>
      </section>

      <Separator />

      {/* Required Skills */}
      <section>
        <h2 className="text-xl font-semibold mb-4">Required Skills</h2>
        <div className="flex flex-wrap gap-2">
          {job.skills.map((skill) => (
            <SkillPill
              key={skill}
              skill={skill}
              onClick={() => handleSkillClick(skill)}
            />
          ))}
        </div>
      </section>

      {/* Qualifications */}
      {job.qualifications && job.qualifications.length > 0 && (
        <>
          <Separator />
          <section>
            <h2 className="text-xl font-semibold mb-4">Qualifications</h2>
            <ul className="space-y-2">
              {job.qualifications.map((qualification, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-primary mr-2">•</span>
                  <span className="text-muted-foreground">{qualification}</span>
                </li>
              ))}
            </ul>
          </section>
        </>
      )}

      {/* Soft Skills */}
      {job.soft_skills && job.soft_skills.length > 0 && (
        <>
          <Separator />
          <section>
            <h2 className="text-xl font-semibold mb-4">Nice to have</h2>
            <div className="text-muted-foreground">
              {job.soft_skills.join(", ")}
            </div>
          </section>
        </>
      )}
    </div>
  )
}
