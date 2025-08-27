# Nimo Frontend - React.js Application

**Modern React.js frontend for the Nimo Decentralized Youth Identity & Proof of Contribution Network**

[![React](https://img.shields.io/badge/React-19.1.1-blue.svg)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-7.1.2-purple.svg)](https://vitejs.dev/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-3.3.4-teal.svg)](https://tailwindcss.com/)

## Overview

This is the modern React.js frontend for the Nimo platform, providing a fast, responsive user interface for decentralized identity creation, contribution tracking, and token management. Built with the latest React 19.1.1 and Vite for optimal development experience.

## Technology Stack

- **React 19.1.1** - Latest React with modern hooks and performance optimizations
- **Vite 7.1.2** - Lightning-fast build tool and development server
- **Tailwind CSS 3.3.4** - Utility-first CSS framework for rapid UI development
- **React Router DOM 7.8.2** - Client-side routing for single-page application
- **React Context API** - State management for user authentication and wallet connection
- **React Icons 5.5.0** - Icon system for consistent UI elements

## Project Structure

```
frontend/
├── public/                 # Static assets
│   └── vite.svg           # Vite favicon
├── src/
│   ├── components/        # Reusable React components
│   │   ├── AuthModal.jsx      # User authentication modal
│   │   ├── ContributionCard.jsx # Contribution display card
│   │   ├── Features.jsx       # Platform features section
│   │   ├── Footer.jsx         # Site footer
│   │   ├── Header.jsx         # Site header
│   │   ├── Hero.jsx           # Landing page hero section
│   │   ├── Navbar.jsx         # Navigation bar
│   │   ├── SkillCard.jsx      # User skills display
│   │   ├── Stats.jsx          # Platform statistics
│   │   └── UserCard.jsx       # User profile card
│   ├── pages/             # Page components
│   │   ├── Contributions.jsx  # Contributions management
│   │   ├── Dashboard.jsx      # User dashboard
│   │   ├── Home.jsx           # Landing page
│   │   ├── Profile.jsx        # User profile page
│   │   └── Skills.jsx         # Skills management
│   ├── contexts/          # React Context providers
│   │   └── UserContext.jsx    # User state management
│   ├── hooks/             # Custom React hooks
│   │   └── useReputation.js   # Reputation calculation hook
│   ├── assets/            # Static assets
│   │   └── react.svg          # React logo
│   ├── App.jsx            # Main application component
│   ├── main.jsx           # React application entry point
│   ├── App.css            # Application styles
│   └── index.css          # Global styles and Tailwind imports
├── package.json           # Dependencies and scripts
├── vite.config.js         # Vite configuration
├── tailwind.config.js     # Tailwind CSS configuration
├── postcss.config.js      # PostCSS configuration
├── eslint.config.js       # ESLint configuration
└── README.md              # This file
```

## Getting Started

### Prerequisites

- Node.js 16+ and npm
- The Nimo backend running (see backend README)

### Installation

1. **Clone and navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```

4. **Open your browser:**
   Navigate to `http://localhost:5173`

### Available Scripts

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build locally
npm run preview

# Run ESLint for code quality
npm run lint
```

## Development

### Key Features

- **Modern React Patterns**: Uses functional components, hooks, and modern JavaScript
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **State Management**: React Context API for global state
- **Routing**: Client-side routing with React Router
- **Performance**: Optimized with Vite's fast HMR and tree-shaking

### Component Architecture

The application follows a component-based architecture:

- **Pages**: Top-level route components (`Home`, `Dashboard`, etc.)
- **Components**: Reusable UI elements (`Header`, `Hero`, `AuthModal`, etc.)
- **Contexts**: Global state providers (`UserContext`)
- **Hooks**: Custom logic extractors (`useReputation`)

### Styling

Uses Tailwind CSS for utility-first styling:

```jsx
// Example component styling
const Hero = () => (
  <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950">
    <div className="container mx-auto px-4 pt-20">
      <h1 className="text-5xl font-bold text-center text-white mb-6">
        Welcome to Nimo
      </h1>
    </div>
  </div>
);
```

## Integration with Backend

### API Integration

The frontend connects to the Flask backend API for:

- User authentication and registration
- Contribution submission and verification
- Token balance and transaction history
- MeTTa AI verification results
- Impact bond management

### Web3 Integration

Future integration points for Web3 functionality:

- Wallet connection (MetaMask, WalletConnect)
- NFT identity creation and management
- Smart contract interactions
- Blockchain transaction monitoring

## Building for Production

```bash
# Create optimized production build
npm run build

# The build artifacts will be stored in the `dist/` directory
```

## Deployment

The built files in `dist/` can be deployed to any static hosting service:

- Vercel
- Netlify
- AWS S3 + CloudFront
- GitHub Pages

## Contributing

1. Follow the existing code style and patterns
2. Use functional components with hooks
3. Implement responsive design with Tailwind CSS
4. Test components across different screen sizes
5. Follow React best practices and performance optimizations

## Related Documentation

- [Main Project README](../README.md) - Overall project overview
- [Backend API Documentation](../backend/README.md) - Backend integration details
- [Technical Documentation](../docs/technical.md) - System architecture
- [User Guide](../docs/user_guide.md) - End-user documentation

---

**Last Updated: August 27, 2025**
