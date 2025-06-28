import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import HomePage from '@/pages/HomePage'

describe('HomePage', () => {
  it('renders main heading', () => {
    render(<HomePage />)
    
    expect(screen.getByText('Car Rental Management System')).toBeInTheDocument()
  })

  it('displays quick stats section', () => {
    render(<HomePage />)
    
    expect(screen.getByText('Quick Stats')).toBeInTheDocument()
    expect(screen.getByText(/Total Contracts:/)).toBeInTheDocument()
    expect(screen.getByText(/Active Bookings:/)).toBeInTheDocument()
    expect(screen.getByText(/Available Cars:/)).toBeInTheDocument()
  })

  it('shows system status as operational', () => {
    render(<HomePage />)
    
    expect(screen.getByText('System Status')).toBeInTheDocument()
    expect(screen.getByText('All systems operational')).toBeInTheDocument()
  })
})