import '@testing-library/jest-dom'
import { expect, afterEach, vi, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend Vitest's expect with jest-dom matchers
expect.extend(matchers)

// Clean up after each test
afterEach(() => {
  cleanup()
})

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(), // deprecated
    removeListener: vi.fn(), // deprecated
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
})

// Mock window.ResizeObserver
global.ResizeObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock IntersectionObserver
global.IntersectionObserver = vi.fn().mockImplementation(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}))

// Mock window.scrollTo
Object.defineProperty(window, 'scrollTo', {
  writable: true,
  value: vi.fn(),
})

// Mock console methods to reduce noise in tests
const originalConsoleError = console.error
const originalConsoleWarn = console.warn

beforeAll(() => {
  console.error = vi.fn()
  console.warn = vi.fn()
})

afterAll(() => {
  console.error = originalConsoleError
  console.warn = originalConsoleWarn
})

// Global test utilities
declare global {
  var testUtils: {
    wait: (ms: number) => Promise<void>
    createMock: <T extends Record<string, unknown>>(defaults: T) => T
    mockApiResponse: <T>(data: T, error?: Error) => ReturnType<typeof vi.fn>
  }
}

global.testUtils = {
  // Helper to wait for a specific amount of time
  wait: (ms: number) => new Promise(resolve => setTimeout(resolve, ms)),

  // Helper to create mock functions with default implementations
  createMock: <T extends Record<string, unknown>>(defaults: T): T => {
    const mock = { ...defaults } as Record<string, unknown>
    Object.keys(mock).forEach(key => {
      if (typeof mock[key] === 'function') {
        mock[key] = vi.fn(mock[key] as (...args: unknown[]) => unknown)
      }
    })
    return mock as T
  },

  // Mock API responses
  mockApiResponse: <T>(data: T, error?: Error) => {
    if (error) {
      return vi.fn().mockRejectedValue(error)
    }
    return vi.fn().mockResolvedValue(data)
  }
}