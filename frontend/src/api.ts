import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1',
})

export type Question = {
  id: number
  text: string
  category: 'pickup' | 'tire_service' | 'common'
  type: 'rating' | 'yes_no' | 'text'
  is_required: boolean
  order: number
}

export type SurveyData = {
  token: string
  order_number: string
  service_type: 'pickup' | 'tire_service' | 'both'
  completed: boolean
  point: { id: number; name: string; city: string }
  questions: Question[]
}

export async function fetchSurvey(token: string): Promise<SurveyData> {
  const { data } = await api.get(`/public/surveys/${token}/`)
  return data
}

export async function submitSurvey(token: string, answers: { question_id: number; answer: unknown }[]) {
  const { data } = await api.post(`/public/surveys/${token}/submit/`, { answers })
  return data as { show_review_page: boolean; review_links: null | { '2gis': string; yandex: string } }
}
