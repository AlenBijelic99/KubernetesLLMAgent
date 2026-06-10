import { useCallback, useEffect, useRef, useState } from "react"

function websocketUrl(): string {
  // Derive the websocket URL from the API URL; the backend authenticates
  // the connection with the access token passed as a query parameter.
  const apiUrl = import.meta.env.VITE_API_URL as string
  const url = new URL("/ws", apiUrl)
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:"
  url.searchParams.set("token", localStorage.getItem("access_token") || "")
  return url.toString()
}

export type AgentSocketStatus = "connecting" | "open" | "closed" | "error"

export function useAgentWebSocket(onMessage: (data: unknown) => void) {
  const socketRef = useRef<WebSocket | null>(null)
  const onMessageRef = useRef(onMessage)
  const [status, setStatus] = useState<AgentSocketStatus>("connecting")

  onMessageRef.current = onMessage

  const connect = useCallback(() => {
    socketRef.current?.close()
    const socket = new WebSocket(websocketUrl())
    socketRef.current = socket
    setStatus("connecting")

    socket.onopen = () => setStatus("open")
    socket.onerror = () => setStatus("error")
    socket.onclose = () => setStatus("closed")
    socket.onmessage = (event) => {
      try {
        onMessageRef.current(JSON.parse(event.data))
      } catch {
        // Ignore malformed frames
      }
    }
  }, [])

  useEffect(() => {
    connect()
    return () => socketRef.current?.close()
  }, [connect])

  return { status, reconnect: connect }
}
