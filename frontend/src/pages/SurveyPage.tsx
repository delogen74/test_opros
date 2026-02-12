import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { useNavigate, useParams } from 'react-router-dom'
import { fetchSurvey, Question, submitSurvey } from '../api'

export function SurveyPage() {
  const { token } = useParams<{ token: string }>()
  const navigate = useNavigate()
  const [survey, setSurvey] = useState<null | Awaited<ReturnType<typeof fetchSurvey>>>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const { register, handleSubmit } = useForm<Record<string, unknown>>()

  useEffect(() => {
    if (!token) return
    fetchSurvey(token)
      .then((data) => {
        setSurvey(data)
        if (data.completed) {
          navigate('/thanks', { replace: true })
        }
      })
      .catch(() => setError('Не удалось загрузить опрос'))
      .finally(() => setLoading(false))
  }, [token, navigate])

  const onSubmit = handleSubmit(async (values) => {
    if (!token || !survey) return

    const answers = survey.questions
      .map((q) => {
        const key = `question_${q.id}`
        const raw = values[key]
        if (raw === undefined || raw === '') {
          return null
        }

        if (q.type === 'rating') return { question_id: q.id, answer: Number(raw) }
        if (q.type === 'yes_no') return { question_id: q.id, answer: raw === 'true' }
        return { question_id: q.id, answer: String(raw) }
      })
      .filter(Boolean) as { question_id: number; answer: unknown }[]

    try {
      const result = await submitSurvey(token, answers)
      if (result.show_review_page) {
        if (result.review_links) {
          sessionStorage.setItem('review_links', JSON.stringify(result.review_links))
        }
        navigate('/review')
      } else {
        navigate('/thanks')
      }
    } catch {
      setError('Ошибка отправки. Проверьте ответы и попробуйте снова.')
    }
  })

  if (loading) return <div className="container">Загрузка...</div>
  if (error) return <div className="container">{error}</div>
  if (!survey) return <div className="container">Опрос не найден</div>

  return (
    <div className="container">
      <h1>Опрос по заказу {survey.order_number}</h1>
      <p>
        ПВЗ: {survey.point.city}, {survey.point.name}
      </p>

      <form onSubmit={onSubmit} className="card-list">
        {survey.questions.map((question) => (
          <QuestionCard key={question.id} question={question} register={register} />
        ))}
        <button type="submit" className="big-button">
          Отправить
        </button>
      </form>
    </div>
  )
}

function QuestionCard({ question, register }: { question: Question; register: ReturnType<typeof useForm>['register'] }) {
  const name = `question_${question.id}`
  return (
    <div className="card">
      <h3>
        {question.text} {question.is_required ? '*' : ''}
      </h3>
      {question.type === 'rating' && (
        <div className="rating-row">
          {[1, 2, 3, 4, 5].map((n) => (
            <label key={n}>
              <input type="radio" value={n} {...register(name, { required: question.is_required })} /> {n}
            </label>
          ))}
        </div>
      )}
      {question.type === 'yes_no' && (
        <div className="button-row">
          <label>
            <input type="radio" value="true" {...register(name, { required: question.is_required })} /> Да
          </label>
          <label>
            <input type="radio" value="false" {...register(name, { required: question.is_required })} /> Нет
          </label>
        </div>
      )}
      {question.type === 'text' && <textarea rows={4} {...register(name, { required: question.is_required })} />}
    </div>
  )
}
