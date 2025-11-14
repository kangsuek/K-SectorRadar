import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Header from './components/common/Header'
import Dashboard from './pages/Dashboard'
import Detail from './pages/Detail'
import Comparison from './pages/Comparison'
import Settings from './pages/Settings'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white dark:bg-gray-900 transition-colors">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/stocks/:ticker" element={<Detail />} />
            <Route path="/compare" element={<Comparison />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App

