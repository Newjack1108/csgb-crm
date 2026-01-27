import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Layout from './components/Layout'
import LeadInbox from './pages/LeadInbox'
import LeadDetail from './pages/LeadDetail'
import CreateLead from './pages/CreateLead'

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<LeadInbox />} />
          <Route path="/leads/:id" element={<LeadDetail />} />
          <Route path="/leads/new" element={<CreateLead />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  )
}

export default App
