import { CheckCircle2, CircleAlert, Loader2 } from "lucide-react"

import { cn } from "@/lib/utils"

interface RunStatusIconProps {
  status: string
  className?: string
}

const RunStatusIcon = ({ status, className }: RunStatusIconProps) => {
  if (status === "failed") {
    return <CircleAlert className={cn("h-5 w-5 text-destructive", className)} />
  }
  if (status === "running") {
    return (
      <Loader2 className={cn("h-5 w-5 animate-spin text-primary", className)} />
    )
  }
  return <CheckCircle2 className={cn("h-5 w-5 text-primary", className)} />
}

export default RunStatusIcon
