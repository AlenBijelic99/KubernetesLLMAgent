import { useQuery, useQueryClient } from "@tanstack/react-query"
import { createFileRoute, useNavigate } from "@tanstack/react-router"
import { toast } from "sonner"

import { AgentService } from "@/client"
import RunAgentButton from "@/components/Agent/RunAgentButton"
import RunAgentStepper from "@/components/Agent/RunAgentStepper"
import RunStatusIcon from "@/components/Agent/RunStatusIcon"
import RunsTable from "@/components/Agent/RunsTable"
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet"
import { useAgentWebSocket } from "@/hooks/useAgentWebSocket"
import useAuth from "@/hooks/useAuth"

type DashboardSearch = {
  run?: string
}

export const Route = createFileRoute("/_layout/")({
  component: Dashboard,
  validateSearch: (search: Record<string, unknown>): DashboardSearch => ({
    run: typeof search.run === "string" ? search.run : undefined,
  }),
  head: () => ({
    meta: [
      {
        title: "Dashboard - Kubernetes AI Agent",
      },
    ],
  }),
})

function Dashboard() {
  const { user: currentUser } = useAuth()
  const { run: selectedRunId } = Route.useSearch()
  const navigate = useNavigate()
  const queryClient = useQueryClient()

  const { data: runs } = useQuery({
    queryKey: ["agent-runs"],
    queryFn: () => AgentService.getRuns(),
  })

  const { data: selectedRun } = useQuery({
    queryKey: ["agent-run", selectedRunId],
    queryFn: () => AgentService.getRun({ id: selectedRunId! }),
    enabled: !!selectedRunId,
  })

  // Events are persisted before being broadcast, so refetching on every
  // websocket message keeps the runs list and the open run detail live.
  useAgentWebSocket((message) => {
    if (message && typeof message === "object" && "error" in message) {
      toast.error(`Agent run failed: ${(message as { error: string }).error}`)
    }
    queryClient.invalidateQueries({ queryKey: ["agent-runs"] })
    queryClient.invalidateQueries({ queryKey: ["agent-run"] })
  })

  const closeRunDetails = () => {
    navigate({ to: "/", search: {} })
  }

  return (
    <div className="flex flex-col gap-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl truncate max-w-sm">
            Hi, {currentUser?.full_name || currentUser?.email} 👋
          </h1>
          <p className="text-muted-foreground">
            Welcome back, nice to see you again!
          </p>
        </div>
        <RunAgentButton />
      </div>
      <RunsTable runs={runs?.data ?? []} selectedRunId={selectedRunId} />
      <Sheet
        open={!!selectedRunId}
        onOpenChange={(open) => {
          if (!open) closeRunDetails()
        }}
      >
        <SheetContent
          side="right"
          className="w-full overflow-y-auto sm:max-w-xl"
        >
          <SheetHeader>
            <SheetTitle className="flex items-center gap-2">
              {selectedRun && <RunStatusIcon status={selectedRun.status} />}
              Agent Run Details
            </SheetTitle>
          </SheetHeader>
          <div className="px-4 pb-8">
            {selectedRun && (
              <RunAgentStepper key={selectedRun.id} run={selectedRun} />
            )}
          </div>
        </SheetContent>
      </Sheet>
    </div>
  )
}
