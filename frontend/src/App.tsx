import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import MainLayout from './components/layout/MainLayout'
import ConfigPage from './components/config/ConfigPage'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MainLayout />} />
        <Route path="/config" element={<ConfigPage />} />
      </Routes>
    </Router>
  )
}

export default App
