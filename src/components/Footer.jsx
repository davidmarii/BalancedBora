import { Sprout, Github, MessageCircle, Mail, ExternalLink } from 'lucide-react'

const footerLinks = {
  Product: ['Features', 'Demo', 'Pricing', 'API'],
  Company: ['About', 'Research', 'Team', 'Careers'],
  Resources: ['Documentation', 'Blog', 'Case Studies', 'Support'],
  Legal: ['Privacy', 'Terms', 'Cookies'],
}

export default function Footer() {
  return (
    <footer id="contact" className="bg-earth-900 text-earth-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid sm:grid-cols-2 lg:grid-cols-5 gap-12">
          {/* Brand */}
          <div className="lg:col-span-2">
            <a href="#home" className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-lg bg-bora-600 flex items-center justify-center">
                <Sprout className="w-5 h-5 text-white" />
              </div>
              <span className="text-xl font-bold text-white tracking-tight">
                Balanced<span className="text-bora-400">Bora</span>
              </span>
            </a>
            <p className="text-earth-400 text-sm leading-relaxed max-w-sm mb-6">
              Empowering African dairy farmers with AI-driven feed formulation for sustainable, profitable farming.
            </p>
            <div className="flex gap-3">
              <a
                href="https://github.com"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-earth-800 flex items-center justify-center hover:bg-bora-700 transition-colors"
              >
                <Github className="w-5 h-5" />
              </a>
              <a
                href="https://wa.me/"
                target="_blank"
                rel="noopener noreferrer"
                className="w-10 h-10 rounded-lg bg-earth-800 flex items-center justify-center hover:bg-green-600 transition-colors"
              >
                <MessageCircle className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@balancedbora.com"
                className="w-10 h-10 rounded-lg bg-earth-800 flex items-center justify-center hover:bg-bora-700 transition-colors"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Links */}
          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category}>
              <h4 className="text-white font-semibold mb-4">{category}</h4>
              <ul className="space-y-3">
                {links.map((link) => (
                  <li key={link}>
                    <a
                      href="#"
                      className="text-sm text-earth-400 hover:text-bora-400 transition-colors inline-flex items-center gap-1"
                    >
                      {link}
                      <ExternalLink className="w-3 h-3 opacity-0 -translate-y-0.5 group-hover:opacity-100 transition-all" />
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Bottom Bar */}
        <div className="mt-16 pt-8 border-t border-earth-800 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-sm text-earth-500">
            © 2024 BalancedBora AI. All rights reserved.
          </p>
          <p className="text-sm text-earth-500">
            Made with 💚 for African dairy farmers
          </p>
        </div>
      </div>
    </footer>
  )
}
