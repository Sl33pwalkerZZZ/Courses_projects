import { useState } from 'react'
import { Eye, EyeOff, LockKeyhole, Mail, UserRound } from 'lucide-react'
import { useTranslation } from 'react-i18next'

export default function AuthField({ name, type = 'text', label, hint, ...props }) {
  const { t } = useTranslation()
  const [showPassword, setShowPassword] = useState(false)
  const isPassword = type === 'password'
  const Icon = isPassword ? LockKeyhole : type === 'email' ? Mail : UserRound
  const inputId = `auth-${name}`

  return (
    <div className="auth-field">
      <label htmlFor={inputId}>{label}</label>
      <div className="auth-input-wrap">
        <Icon size={17} aria-hidden="true" />
        <input {...props} id={inputId} name={name} type={isPassword && showPassword ? 'text' : type}
          className={isPassword ? 'auth-password-input' : undefined}
          aria-describedby={hint ? `${inputId}-hint` : undefined} />
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
