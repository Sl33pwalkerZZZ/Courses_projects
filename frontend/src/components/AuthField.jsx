import { useState } from 'react'
import { Eye, EyeOff, LockKeyhole, Mail, UserRound } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { motion } from 'motion/react'
import { useReducedMotion } from '../hooks/useMotionPreferences'

export default function AuthField({ name, type = 'text', label, hint, ...props }) {
  const { t } = useTranslation()
  const [showPassword, setShowPassword] = useState(false)
  const [focused, setFocused] = useState(false)
  const reducedMotion = useReducedMotion()
  const isPassword = type === 'password'
  const Icon = isPassword ? LockKeyhole : type === 'email' ? Mail : UserRound
  const inputId = `auth-${name}`

  return (
    <div className="auth-field">
      <label htmlFor={inputId}>{label}</label>
      <div className="auth-input-wrap" onFocusCapture={() => setFocused(true)}
        onBlurCapture={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setFocused(false) }}>
        <Icon size={17} aria-hidden="true" />
        <input {...props} id={inputId} name={name} type={isPassword && showPassword ? 'text' : type}
          className={isPassword ? 'auth-password-input' : undefined}
          aria-describedby={hint ? `${inputId}-hint` : undefined} />
        <motion.span className="auth-focus-line" aria-hidden="true" initial={false}
          animate={{ scaleX: focused ? 1 : 0 }} transition={{ duration: reducedMotion ? 0 : 0.16 }} />
        {isPassword && (
          <button className="auth-password-toggle" type="button" disabled={props.disabled}
            aria-label={t(showPassword ? 'auth.hidePassword' : 'auth.showPassword')}
            aria-controls={inputId} aria-pressed={showPassword}
            onClick={() => setShowPassword((value) => !value)}>
            {showPassword ? <EyeOff size={17} aria-hidden="true" /> : <Eye size={17} aria-hidden="true" />}
          </button>
        )}
      </div>
      {hint && <p className="auth-field-hint" id={`${inputId}-hint`}>{hint}</p>}
    </div>
  )
}
