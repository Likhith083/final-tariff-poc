import * as React from "react"
import { Toaster as ToastPrimitive } from "react-hot-toast"

export function Toaster() {
  return (
    <ToastPrimitive
      position="top-right"
      toastOptions={{
        duration: 4000,
        style: {
          background: "hsl(var(--background))",
          color: "hsl(var(--foreground))",
          border: "1px solid hsl(var(--border))",
        },
      }}
    />
  )
} 