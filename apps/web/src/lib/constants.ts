/**
 * Constants for JobExtractor frontend
 * Colors, configurations, and static data
 */

export const DOMAIN_COLORS: Record<string, string> = {
  "Software Development":    "#378ADD",   // blue
  "Data Science & ML":       "#7F77DD",   // purple
  "DevOps & Cloud":          "#EF9F27",   // amber
  "Frontend Development":    "#1D9E75",   // teal
  "Backend Development":     "#639922",   // green
  "Full Stack Development":  "#5DCAA5",   // light teal
  "Mobile Development":      "#D4537E",   // pink
  "Cybersecurity":           "#E24B4A",   // red
  "UI/UX Design":            "#BA7517",   // dark amber
  "Product Management":      "#D85A30",   // coral
  "Data Analysis":           "#AFA9EC",   // light purple
  "Digital Marketing":       "#97C459",   // light green
  "Content Writing":         "#F0997B",   // light coral
  "Finance & Accounting":    "#85B7EB",   // light blue
  "HR & Recruitment":        "#ED93B1",   // light pink
  "Customer Support":        "#9FE1CB",   // light teal
  "Sales":                   "#FAC775",   // light amber
  "Operations":              "#B4B2A9",   // gray
  "Research":                "#534AB7",   // dark purple
  "Other":                   "#888780",   // muted gray
}

export const PORTAL_COLORS: Record<string, string> = {
  linkedin:     "#0A66C2",
  naukri:       "#FF7555",
  internshala:  "#00C4B4",
  remotive:     "#4CAF50",
  remoteok:     "#1A1A1A",
  arbeitnow:    "#6366F1",
  freshersnow:  "#F59E0B",
}

export const SENIORITY_ORDER = [
  "Fresher", "Intern", "Entry Level", "Junior",
  "Mid Level", "Senior"
]

export const SORT_OPTIONS = [
  { label: "Newest first",      value: "scraped_at:desc" },
  { label: "Oldest first",      value: "scraped_at:asc" },
  { label: "Salary (high-low)", value: "salary_min:desc" },
  { label: "Salary (low-high)", value: "salary_min:asc" },
]

export const PAGE_SIZE = 20
export const MAX_SKILLS_DISPLAY = 5
export const SEARCH_DEBOUNCE_MS = 400

// Navigation items for sidebar
export const NAV_ITEMS = [
  { href: "/", label: "Dashboard", icon: "LayoutDashboard" },
  { href: "/jobs", label: "Browse Jobs", icon: "Briefcase" },
  { href: "/analytics", label: "Analytics", icon: "BarChart2" },
  { href: "/saved", label: "Saved Jobs", icon: "Bookmark" },
  { href: "/ai", label: "AI Assistant", icon: "Bot" },
]

// Job types for filters
export const JOB_TYPES = [
  "Full-time",
  "Part-time",
  "Internship", 
  "Contract",
  "Remote",
]

// Seniority levels for filters
export const SENIORITY_LEVELS = [
  { value: "", label: "All" },
  { value: "Fresher", label: "Fresher" },
  { value: "Intern", label: "Intern" },
  { value: "Entry Level", label: "Entry Level" },
  { value: "Junior", label: "Junior" },
]

// Chart colors for analytics
export const CHART_COLORS = {
  primary: "#378ADD",
  secondary: "#7F77DD", 
  success: "#1D9E75",
  warning: "#EF9F27",
  danger: "#E24B4A",
  info: "#639922",
  muted: "#888780",
}
