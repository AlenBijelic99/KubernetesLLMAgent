import { type LLMMessage, messageText } from "@/lib/agent-types"

interface AIMessageProps {
  message: LLMMessage
}

const AIMessage = ({ message }: AIMessageProps) => {
  const text = messageText(message.content)
  const toolCalls = message.tool_calls ?? []
  const modelName = message.response_metadata?.model_name

  if (!text && toolCalls.length === 0) return null

  return (
    <div className="rounded-md border border-primary/50 bg-muted/50 p-4 my-2 shadow-sm">
      {modelName && (
        <p className="text-xs text-muted-foreground">{modelName}</p>
      )}
      {text && (
        <>
          <h3 className="text-sm font-semibold text-primary mb-2">
            AI Message
          </h3>
          <p className="whitespace-pre-wrap break-words rounded-md bg-background p-2 text-sm">
            {text}
          </p>
        </>
      )}
      {toolCalls.length > 0 && (
        <div className="mt-3 flex flex-col gap-2">
          <h4 className="text-xs font-semibold text-chart-3">
            Calling Functions
          </h4>
          {toolCalls.map((toolCall, index) => (
            <div
              key={toolCall.id ?? index}
              className="rounded-md border border-chart-3/50 bg-background p-3 shadow-sm"
            >
              <p className="text-sm font-bold text-chart-3">{toolCall.name}</p>
              <code className="mt-1 block whitespace-pre-wrap break-all text-xs">
                {JSON.stringify(toolCall.args)}
              </code>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default AIMessage
