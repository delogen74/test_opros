import { Navigate, Route, Routes } from 'react-router-dom'
import { ReviewPage } from './pages/ReviewPage'
import { SurveyPage } from './pages/SurveyPage'
import { ThankYouPage } from './pages/ThankYouPage'

export type ReviewLinks = { '2gis': string; yandex: string }

function App() {
  return (
    <Routes>
      <Route path="/s/:token" element={<SurveyPage />} />
      <Route path="/thanks" element={<ThankYouPage />} />
      <Route path="/review" element={<ReviewPage />} />
      <Route path="*" element={<Navigate to="/thanks" replace />} />
    </Routes>
  )
}

export default App
