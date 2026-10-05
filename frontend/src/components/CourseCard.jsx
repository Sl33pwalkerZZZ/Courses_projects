import { ArrowUpRight, BookOpen, UserRound } from 'lucide-react'
import { Link } from 'react-router-dom'
import Reveal from './Reveal'
import './CourseCard.css'

const LEVEL_LABELS = {
  beginner: 'Начинающий',
  intermediate: 'Средний',
  advanced: 'Продвинутый',
}

export default function CourseCard({ course, index = 0 }) {
  return (
    <Reveal className="course-card-reveal" delay={Math.min(index, 3) * 0.06}>
      <Link to={`/courses/${course.slug}`} className="academic-course-card">
        <div className={`course-art course-art-${index % 3}`} aria-hidden="true">
          <span className="art-circle art-circle-one" /><span className="art-circle art-circle-two" />
          <span className="art-crosshair" /><BookOpen size={32} strokeWidth={1} />
          <span className="art-caption">БИБЛИОТЕКА / AI</span>
          <span className="art-arrow"><ArrowUpRight size={19} /></span>
        </div>
        <div className="academic-card-body">
          <span className="academic-badge">{course.direction.name}</span>
          <h3>{course.title}</h3>
          <p className="academic-card-description">{course.description}</p>
          <div className="academic-card-meta"><UserRound size={14} aria-hidden="true" /><span>{course.author}</span></div>
          <div className="academic-card-bottom">
            <span>{LEVEL_LABELS[course.level] || course.level}</span>
            <span className="card-open">Открыть курс <ArrowUpRight size={15} aria-hidden="true" /></span>
          </div>
        </div>
      </Link>
    </Reveal>
  )
}
