import { Link } from 'react-router-dom'
import './ui.css'

// Keep navigation as real links and actions as native buttons.
export default function Button({ to, href, variant = 'primary', className = '', children, ...props }) {
  const classes = `v2-button v2-button--${variant} ${className}`.trim()
  if (to) return <Link to={to} className={classes} {...props}>{children}</Link>
  if (href) return <a href={href} className={classes} {...props}>{children}</a>
  return <button type="button" className={classes} {...props}>{children}</button>
}
