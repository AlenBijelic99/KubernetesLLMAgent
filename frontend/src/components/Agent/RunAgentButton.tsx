import { useQueryClient } from "@tanstack/react-query"
import { toast } from "sonner"

import { AgentService } from "@/client"
import { Button } from "@/components/ui/button"

const RunAgentButton = () => {
  const queryClient = useQueryClient()

  const handleClick = () => {
    const promise = AgentService.runAgent().finally(() => {
      queryClient.invalidateQueries({ queryKey: ["agent-runs"] })
      queryClient.invalidateQueries({ queryKey: ["agent-run"] })
    })

    toast.promise(promise, {
      loading: "Running agent, please wait...",
      success: "Agent ran successfully",
      error: (error: any) => {
        if (error?.status === 429) {
          return "You exceeded your current quota, please check your plan and billing details."
        }
        return (
          error?.body?.detail ||
          error?.message ||
          "An unexpected error occurred."
        )
      },
    })
  }

  return <Button onClick={handleClick}>Run Agent</Button>
}

export default RunAgentButton
