/**
 * Browse Jobs page
 * Full job listing with filters, search, sorting, and pagination
 * useSearchParams is used inside a Suspense-wrapped child component
 */

import { Suspense } from "react"
import { JobsBrowser } from "./JobsBrowser"

export default function JobsPage() {
  return (
    <Suspense
      fallback={
        <div className="space-y-4">
          <div className="h-10 w-full bg-muted rounded animate-pulse" />
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Array.from({ length: 6 }).map((_, i) => (
              <div key={i} className="h-48 bg-muted rounded-lg animate-pulse" />
            ))}
          </div>
        </div>
      }
    >
      <JobsBrowser />
    </Suspense>
  )
}
