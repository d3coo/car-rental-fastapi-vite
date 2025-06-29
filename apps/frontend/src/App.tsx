import { Routes, Route } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import HomePage from '@/pages/HomePage'
import ContractsPage from '@/pages/ContractsPage'
import BookingsPage from '@/pages/BookingsPage'
import CarsPage from '@/pages/CarsPage'
import Layout from '@/components/Layout'

function App() {
  return (
    <div className="min-h-screen bg-background">
      <Layout>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/contracts" element={<ContractsPage />} />
          <Route path="/contracts/:id" element={<div>Contract Detail (TODO)</div>} />
          <Route path="/bookings" element={<BookingsPage />} />
          <Route path="/bookings/:id" element={<div>Booking Detail (TODO)</div>} />
          <Route path="/cars" element={<CarsPage />} />
          <Route path="/cars/:id" element={<div>Car Detail (TODO)</div>} />
          <Route path="*" element={<div>404 - Page Not Found</div>} />
        </Routes>
      </Layout>
      <Toaster />
    </div>
  )
}

export default App