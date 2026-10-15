import './ui.css'

export default function Badge({ children, className = '', tone = 'neutral' }) {
  return <span className={`v2-badge v2-badge--${tone} ${className}`.trim()}>{children}</span>
}
