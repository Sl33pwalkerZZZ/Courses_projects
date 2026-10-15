import { useEffect, useRef } from 'react'
import './ui.css'

// Native dialog provides focus containment, background inertness and Escape.
export default function Dialog({ children, onClose, labelledBy, className = '' }) {
  const ref = useRef(null)
  useEffect(() => {
    const dialog = ref.current
    const trigger = document.activeElement
    dialog.showModal()
    return () => {
      dialog.close()
      if (trigger?.isConnected) trigger.focus({ preventScroll: true })
    }
  }, [])

  return (
    <dialog ref={ref} className={`v2-dialog ${className}`} aria-labelledby={labelledBy}
      onCancel={(event) => { event.preventDefault(); onClose() }}
      onClick={(event) => {
        if (event.target !== event.currentTarget) return
        const bounds = event.currentTarget.getBoundingClientRect()
        if (event.clientX < bounds.left || event.clientX > bounds.right
          || event.clientY < bounds.top || event.clientY > bounds.bottom) onClose()
      }}>
      {children}
    </dialog>
  )
}
