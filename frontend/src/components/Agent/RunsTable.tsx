import { useNavigate } from "@tanstack/react-router"

import type { AgentRunPublic } from "@/client"
import RunStatusIcon from "@/components/Agent/RunStatusIcon"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { cn } from "@/lib/utils"

interface RunsTableProps {
  runs: AgentRunPublic[]
  selectedRunId?: string
}

const RunsTable = ({ runs, selectedRunId }: RunsTableProps) => {
  const navigate = useNavigate()

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead className="w-12">Status</TableHead>
          <TableHead>Start Time</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {runs.map((run) => (
          <TableRow
            key={run.id}
            onClick={() => navigate({ to: "/", search: { run: run.id } })}
            className={cn(
              "cursor-pointer",
              selectedRunId === run.id && "bg-muted",
            )}
          >
            <TableCell>
              <RunStatusIcon status={run.status} />
            </TableCell>
            <TableCell>
              {run.start_time ? new Date(run.start_time).toLocaleString() : "-"}
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}

export default RunsTable
