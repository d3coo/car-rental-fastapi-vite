// Simple placeholder toaster component
import { ReactNode } from 'react'

interface ToasterProps {
  children?: ReactNode
}

export function Toaster({ children }: ToasterProps) {
  return (
    <div id="toast-container" className="fixed bottom-4 right-4 z-50">
      {children}
    </div>
  )
}