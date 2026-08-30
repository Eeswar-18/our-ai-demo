import { useState, useEffect } from 'react'
import Hero from '../components/Hero'
import Capabilities from '../components/Capabilities'
import HealthIndicator from '../components/HealthIndicator'

const LandingPage = () => {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20)
    }
    window.addEventListener('scroll', handleScroll, { passive: true })
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <>
      {/* Navigation */}
      <nav className={`navbar${scrolled ? ' scrolled' : ''}`}>
        <a href="/" className="nav-logo">
          <span className="nav-logo-mark">G</span>
          <span style={{color:'var(--text-primary)'}}>Guide</span><span style={{color:'var(--gold)'}}>X</span>
        </a>

        <ul className="nav-links">
          <li><a href="#capabilities" className="nav-link">Capabilities</a></li>
          <li><a href="/chat" className="nav-link">Live Demo</a></li>
        </ul>

        <HealthIndicator />
      </nav>

      {/* Hero */}
      <Hero />

      {/* Capabilities */}
      <Capabilities />

      {/* Footer */}
      <footer className="footer">
        <span className="footer-gold">◈</span>{' '}
        <span style={{color:'var(--text-primary)'}}>Guide</span><span style={{color:'var(--gold)'}}>X</span> — AI Business Intelligence Platform
      </footer>
    </>
  )
}

export default LandingPage
