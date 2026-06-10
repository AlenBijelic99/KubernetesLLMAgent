interface ErrorMessageProps {
  error: string
}

const ErrorMessage = ({ error }: ErrorMessageProps) => {
  if (!error) return null

  return (
    <div className="rounded-md border border-destructive/60 bg-muted/50 p-4 my-2 shadow-sm">
      <h3 className="text-sm font-semibold text-destructive mb-2">Error</h3>
      <p className="whitespace-pre-wrap break-words rounded-md bg-background p-2 text-sm">
        {error}
      </p>
    </div>
  )
}

export default ErrorMessage
