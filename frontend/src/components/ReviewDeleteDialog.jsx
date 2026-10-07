import { useEffect, useId, useRef } from 'react'
import { useTranslation } from 'react-i18next'

export default function ReviewDeleteDialog({ busy, error, onCancel, onConfirm }) {
  const { t } = useTranslation()
  const dialogRef = useRef(null)
  const id = useId()

  useEffect(() => {
    const dialog = dialogRef.current
    dialog.showModal()
    return () => { dialog.close() }
  }, [])

  function handleCancel(event) {
    event.preventDefault()
    if (!busy) onCancel()
  }

  return (
    <dialog ref={dialogRef} className="review-delete-dialog" aria-labelledby={`${id}-title`}
      aria-describedby={`${id}-description`} aria-busy={busy} onCancel={handleCancel}>
      <h2 id={`${id}-title`}>{t('reviews.confirmDeletion')}</h2>
      <p id={`${id}-description`}>{t('reviews.deleteQuestion')}</p>
      <p className="review-delete-hint">{t('reviews.deleteHint')}</p>
      {error && <p className="reviews-error" role="alert">{t(error)}</p>}
      <div className="review-dialog-actions">
        <button className="review-secondary-button" type="button" disabled={busy} onClick={onCancel}>{t('reviews.cancel')}</button>
        <button className="academic-button" type="button" disabled={busy} onClick={onConfirm}>
          {t(busy ? 'reviews.deleting' : 'reviews.confirmDeletion')}
        </button>
      </div>
    </dialog>
  )
}
