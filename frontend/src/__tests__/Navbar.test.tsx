import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BrowserRouter } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { AuthProvider } from '../contexts/AuthContext'
import { ThemeProvider } from '../contexts/ThemeContext'

// Mock the useAuth hook
vi.mock('../hooks/useAuth', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    logout: vi.fn(),
    walletConnected: false
  })
}))

// Mock react-router-dom's useNavigate
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom')
  return {
    ...actual,
    useNavigate: () => vi.fn()
  }
})

const renderNavbar = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Navbar />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  )
}

describe('Navbar', () => {
  it('renders the Nimo logo and title', () => {
    renderNavbar()
    expect(screen.getByText('Nimo')).toBeInTheDocument()
  })

  it('shows sign in and sign up buttons when not authenticated', () => {
    renderNavbar()
    expect(screen.getByText('Sign In')).toBeInTheDocument()
    expect(screen.getByText('Sign Up')).toBeInTheDocument()
  })

  it('does not show dashboard links when not authenticated', () => {
    renderNavbar()
    expect(screen.queryByText('Dashboard')).not.toBeInTheDocument()
    expect(screen.queryByText('Contributions')).not.toBeInTheDocument()
  })
})