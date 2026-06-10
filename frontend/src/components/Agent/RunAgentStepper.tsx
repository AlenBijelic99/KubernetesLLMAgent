import { Check, ChevronDown, ChevronUp, CircleMinus } from "lucide-react"
import { useState } from "react"

import type { AgentRunAndEventsPublic, EventPublic } from "@/client"
import AIMessage from "@/components/Agent/AIMessage"
import ErrorMessage from "@/components/Agent/ErrorMessage"
import HumanMessage from "@/components/Agent/HumanMessage"
import ToolMessage from "@/components/Agent/ToolMessage"
import { Button } from "@/components/ui/button"
import type { AgentNodeUpdate, LLMMessage } from "@/lib/agent-types"
import { cn } from "@/lib/utils"

interface RunAgentStepperProps {
  run: AgentRunAndEventsPublic
}

const stepKeys = [
  "metric_analyser",
  "diagnostic",
  "solution",
  "incident_reporter",
]

const groupNames: Record<string, string> = {
  metric_analyser: "Metric Analysis",
  diagnostic: "Diagnostic",
  solution: "Solution",
  incident_reporter: "Incident Report",
}

// Group events by the agent that produced them. Tool events (call_tool) and
// errors are attached to the step that triggered them.
const groupEvents = (events: EventPublic[]) => {
  const groups: Record<string, EventPublic[]> = {
    metric_analyser: [],
    diagnostic: [],
    solution: [],
    incident_reporter: [],
  }

  let lastKey: string | null = null

  for (const event of events) {
    const key = Object.keys(event.event_data)[0]
    if (groups[key]) {
      groups[key].push(event)
      lastKey = key
    } else if (lastKey) {
      // call_tool updates and error events belong to the previous step
      groups[lastKey].push(event)
    }
  }

  return groups
}

const EventMessages = ({ event }: { event: EventPublic }) => {
  const eventData = event.event_data as Record<string, unknown>

  if (typeof eventData.error === "string" || eventData.type === "Error") {
    return <ErrorMessage error={String(eventData.error ?? "Unknown error")} />
  }

  const nodeUpdate = Object.values(eventData)[0] as AgentNodeUpdate | undefined
  const messages: LLMMessage[] = nodeUpdate?.messages ?? []

  return (
    <>
      {messages.map((message, index) => {
        switch (message.type) {
          case "human":
            return <HumanMessage key={index} message={message} />
          case "ai":
            return <AIMessage key={index} message={message} />
          case "tool":
            return <ToolMessage key={index} message={message} />
          default:
            return <ErrorMessage key={index} error="Unknown message type" />
        }
      })}
    </>
  )
}

// NOTE: render with key={run.id} so the expanded state resets when
// another run is selected.
const RunAgentStepper = ({ run }: RunAgentStepperProps) => {
  const eventGroups = groupEvents(run.events)
  const [expandedSteps, setExpandedSteps] = useState<string[]>([])

  const toggleExpand = (key: string) => {
    setExpandedSteps((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key],
    )
  }

  return (
    <div>
      <div className="mb-4 flex gap-2">
        <Button size="sm" onClick={() => setExpandedSteps(stepKeys)}>
          Expand All
        </Button>
        <Button
          size="sm"
          variant="outline"
          onClick={() => setExpandedSteps([])}
        >
          Collapse All
        </Button>
      </div>
      <ol>
        {stepKeys.map((key, index) => {
          const hasData = eventGroups[key].length > 0
          const expanded = expandedSteps.includes(key)
          const isLast = index === stepKeys.length - 1

          return (
            <li key={key} className="relative flex gap-4">
              {/* Indicator column */}
              <div className="flex flex-col items-center">
                <div
                  className={cn(
                    "flex h-8 w-8 shrink-0 items-center justify-center rounded-full border-2",
                    hasData
                      ? "border-primary bg-primary text-primary-foreground"
                      : "border-border bg-muted text-muted-foreground",
                  )}
                >
                  {hasData ? (
                    <Check className="h-4 w-4" />
                  ) : (
                    <CircleMinus className="h-4 w-4" />
                  )}
                </div>
                {!isLast && <div className="w-px grow bg-border" />}
              </div>

              {/* Step content */}
              <div className="min-h-16 w-full pb-6">
                <p className="font-semibold leading-8">{groupNames[key]}</p>
                {hasData && (
                  <div
                    className={cn(
                      "relative overflow-hidden text-sm text-muted-foreground",
                      !expanded && "max-h-28",
                    )}
                  >
                    <div className={cn(expanded && "mb-8")}>
                      {eventGroups[key].map((event) => (
                        <EventMessages key={event.id} event={event} />
                      ))}
                    </div>
                    <button
                      type="button"
                      onClick={() => toggleExpand(key)}
                      className={cn(
                        "absolute inset-x-0 bottom-0 flex cursor-pointer items-end justify-center",
                        expanded
                          ? "h-8"
                          : "h-14 bg-gradient-to-t from-background to-transparent",
                      )}
                      aria-label={expanded ? "Collapse step" : "Expand step"}
                    >
                      {expanded ? (
                        <ChevronUp className="h-6 w-6" />
                      ) : (
                        <ChevronDown className="h-6 w-6" />
                      )}
                    </button>
                  </div>
                )}
              </div>
            </li>
          )
        })}
      </ol>
    </div>
  )
}

export default RunAgentStepper
