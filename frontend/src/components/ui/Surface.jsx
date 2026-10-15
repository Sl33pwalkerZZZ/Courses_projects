import './ui.css'

export default function Surface({ as: Tag = 'div', className = '', children, ...props }) {
  return <Tag className={`v2-surface ${className}`.trim()} {...props}>{children}</Tag>
}
