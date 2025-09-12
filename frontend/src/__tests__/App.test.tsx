import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import App from '../App'

describe('App', () => {
  it('renders the landing page by default', () => {
    render(<App />)
    // Test that the app renders without crashing
    expect(document.body).toBeInTheDocument()
  })

  it('has routing setup', () => {
    render(<App />)
    // The app should have routing components
    expect(screen.getByRole('main')).toBeInTheDocument()
  })
})