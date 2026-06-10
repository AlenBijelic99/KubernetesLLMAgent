import { Separator } from "@/components/ui/separator"
import { type LLMMessage, messageText } from "@/lib/agent-types"

interface ToolMessageProps {
  message: LLMMessage
}

const ToolMessage = ({ message }: ToolMessageProps) => {
  const lines = messageText(message.content).split("\n")

  return (
    <div className="rounded-md border border-chart-3/50 bg-muted/50 p-4 my-2 shadow-sm">
      <p className="text-sm font-bold text-chart-3">{message.name}</p>
      <Separator className="my-2" />
      <div className="flex flex-col gap-1">
        {lines.map((line, index) => (
          <code
            key={index}
            className="block whitespace-pre-wrap break-all rounded-md bg-background p-2 text-xs"
          >
            {line}
          </code>
        ))}
      </div>
    </div>
  )
}

export default ToolMessage
