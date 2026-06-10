// Shapes of the agent run events streamed over the websocket and stored in
// EventPublic.event_data. They mirror langchain-core's message model_dump()
// output and are not part of the OpenAPI schema.

export interface ToolCall {
  name: string
  args: Record<string, unknown>
  id?: string | null
  type?: string
}

export interface LLMMessage {
  type: "human" | "ai" | "tool" | string
  content: unknown
  name?: string | null
  tool_calls?: ToolCall[]
  tool_call_id?: string
}

// A graph update event: one key per node that produced an update
// (metric_analyser, diagnostic, solution, incident_reporter, call_tool),
// or an error payload emitted when the run fails.
export interface AgentNodeUpdate {
  messages: LLMMessage[]
  sender?: string
}

export type AgentEventData = Record<string, AgentNodeUpdate> & {
  error?: string
}

export function messageText(content: unknown): string {
  // langchain message content can be a plain string or a list of typed blocks
  if (typeof content === "string") return content
  if (Array.isArray(content)) {
    return content
      .map((block) =>
        typeof block === "string"
          ? block
          : ((block as { text?: string }).text ?? ""),
      )
      .join("")
  }
  return ""
}
