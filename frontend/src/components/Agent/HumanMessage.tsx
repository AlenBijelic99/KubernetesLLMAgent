import { type LLMMessage, messageText } from "@/lib/agent-types"

interface HumanMessageProps {
  message: LLMMessage
}

const HumanMessage = ({ message }: HumanMessageProps) => {
  const text = messageText(message.content)
  if (!text) return null

  return (
    <div className="rounded-md border border-primary/50 bg-muted/50 p-4 my-2 shadow-sm">
      <h3 className="text-sm font-semibold text-primary mb-2">Instruction</h3>
      <p className="whitespace-pre-wrap break-words rounded-md bg-background p-2 text-sm">
        {text}
      </p>
    </div>
  )
}

export default HumanMessage
