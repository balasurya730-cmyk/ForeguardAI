import { useEffect, useRef, useState, useCallback } from 'react'

/**
 * Connects to /ws/dashboard and dispatches incoming {type, data} messages
 * to registered handlers. Automatically reconnects with backoff if the
 * connection drops (e.g. backend restart), so the dashboard keeps working
 * without a manual page refresh once the backend comes back.
 */
export function useWebSocket() {
  const [connected, setConnected] = useState(false)
  const handlersRef = useRef({})
  const wsRef = useRef(null)
  const retryRef = useRef(1000)

  const on = useCallback((type, handler) => {
    if (!handlersRef.current[type]) handlersRef.current[type] = []
    handlersRef.current[type].push(handler)
    return () => {
      handlersRef.current[type] = handlersRef.current[type].filter((h) => h !== handler)
    }
  }, [])

  useEffect(() => {
    let cancelled = false

    function connect() {
      if (cancelled) return
      const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws'
      const url = `${protocol}://${window.location.host}/ws/dashboard`
      const ws = new WebSocket(url)
      wsRef.current = ws

      ws.onopen = () => {
        setConnected(true)
        retryRef.current = 1000
      }

      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data)
          const handlers = handlersRef.current[message.type] || []
          handlers.forEach((h) => h(message.data))
          const wildcardHandlers = handlersRef.current['*'] || []
          wildcardHandlers.forEach((h) => h(message))
        } catch (err) {
          console.error('Failed to parse WebSocket message', err)
        }
      }

      ws.onclose = () => {
        setConnected(false)
        if (!cancelled) {
          setTimeout(connect, retryRef.current)
          retryRef.current = Math.min(retryRef.current * 1.5, 15000)
        }
      }

      ws.onerror = () => {
        ws.close()
      }
    }

    connect()

    return () => {
      cancelled = true
      wsRef.current?.close()
    }
  }, [])

  return { connected, on }
}
