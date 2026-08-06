import { useState, useEffect } from 'react'
import { Menu, X, Sprout } from 'lucide-react'

const navLinks = [
  { name: 'Home', href: '#home' },
  { name: 'Research', href: '#research' },
  { name: 'About', href: '#about' },
  { name: 'Contact', href: '#contact' },
]

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false)
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', handleScroll)
    return () => window.removeEventListener('scroll', handleScroll)
  }, [])

  return (
    <nav
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/90 backdrop-blur-md shadow-sm border-b border-earth-200'
          : 'bg-transparent'
      }`}
    >
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <a href="#home" className="flex items-center gap-2 group">
            <div className="w-9 h-9 rounded-lg bg-bora-600 flex items-center justify-center group-hover:bg-bora-700 transition-colors">
              <Sprout className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-earth-900 tracking-tight">
              Balanced<span className="text-bora-600">Bora</span>
            </span>
          </a>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                className="text-sm font-medium text-earth-600 hover:text-bora-700 transition-colors relative group"
              >
                {link.name}
                <span className="absolute -bottom-1 left-0 w-0 h-0.5 bg-bora-600 transition-all group-hover:w-full" />
              </a>
            ))}
            <a
              href="#demo"
              className="ml-2 px-5 py-2.5 text-sm font-semibold text-white bg-bora-600 rounded-full hover:bg-bora-700 transition-all hover:shadow-lg hover:shadow-bora-600/20 active:scale-95"
            >
              Try Demo
            </a>
          </div>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setIsOpen(!isOpen)}
            className="md:hidden p-2 rounded-lg text-earth-600 hover:bg-earth-100 transition-colors"
          >
            {isOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>
      </div>

      {/* Mobile Menu */}
      <div
        className={`md:hidden transition-all duration-300 overflow-hidden ${
          isOpen ? 'max-h-80 opacity-100' : 'max-h-0 opacity-0'
        }`}
      >
        <div className="px-4 pb-6 pt-2 bg-white/95 backdrop-blur-md border-b border-earth-200 space-y-1">
          {navLinks.map((link) => (
            <a
              key={link.name}
              href={link.href}
              onClick={() => setIsOpen(false)}
              className="block px-4 py-3 text-earth-700 hover:text-bora-700 hover:bg-bora-50 rounded-lg font-medium transition-colors"
            >
              {link.name}
            </a>
          ))}
          <a
            href="#demo"
            onClick={() => setIsOpen(false)}
            className="block mx-4 mt-3 px-5 py-3 text-center text-sm font-semibold text-white bg-bora-600 rounded-full hover:bg-bora-700 transition-colors"
          >
            Try Demo
          </a>
        </div>
      </div>
    </nav>
  )
}
