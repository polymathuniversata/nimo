import React from 'react'
import Header from '../components/Header'
import Hero from '../components/Hero'
import Features from '../components/Features'
import state from "../components/Stats";
import Footer from '../components/Footer'

const Home = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-950">
      <Header />
      <Hero />
      <Features />
      <state/>
      <Footer />
    </div>
  )
}

export default Home