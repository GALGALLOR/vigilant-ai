import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import VideoPage from './pages/VideoPage'
import BenchmarkPage from './pages/BenchmarkPage'
import './index.css'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/video/:videoId" element={<VideoPage />} />
        <Route path="/benchmarks" element={<BenchmarkPage />} />
      </Routes>
    </BrowserRouter>
  )
}
