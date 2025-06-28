import { render, screen } from '@testing-library/react'
import { BrowserRouter } from 'react-router-dom'
import { describe, it, expect } from 'vitest'
import Layout from '@/components/Layout'

const MockedLayout = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <Layout>{children}</Layout>
  </BrowserRouter>
)

describe('Layout', () => {
  it('renders app title', () => {
    render(
      <MockedLayout>
        <div>Test content</div>
      </MockedLayout>
    )
    
    expect(screen.getByText('Car Rental')).toBeInTheDocument()
  })

  it('renders navigation items', () => {
    render(
      <MockedLayout>
        <div>Test content</div>
      </MockedLayout>
    )
    
    expect(screen.getByText('Home')).toBeInTheDocument()
    expect(screen.getByText('Contracts')).toBeInTheDocument() 
    expect(screen.getByText('Bookings')).toBeInTheDocument()
  })

  it('renders children content', () => {
    render(
      <MockedLayout>
        <div>Test content</div>
      </MockedLayout>
    )
    
    expect(screen.getByText('Test content')).toBeInTheDocument()
  })
})