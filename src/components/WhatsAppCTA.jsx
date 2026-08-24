import { MessageCircle } from 'lucide-react'

function WhatsAppCTA() {
  return (
    <section className="py-16 px-6 bg-green-600 text-white animate-on-scroll">
      <div className="max-w-3xl mx-auto text-center">
        <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-6">
          <MessageCircle size={32} />
        </div>
        <h2 className="text-3xl md:text-4xl font-bold mb-4">
          Formulate Feed on WhatsApp
        </h2>
        <p className="text-green-100 text-lg mb-8 max-w-xl mx-auto">
          Chat with <strong>BalancedBora</strong> and get AI-powered livestock feed recommendations instantly.
        </p>
        <a
          href="https://wa.me/14155238886?text=join%20BalancedBora"
          target="_blank"
          rel="noopener noreferrer"
          className="inline-flex items-center gap-2 bg-white text-green-700 px-8 py-4 rounded-full font-semibold hover:bg-green-50 transition-colors"
        >
          <MessageCircle size={20} />
          Start on WhatsApp
        </a>
        <p className="mt-4 text-sm text-green-200">
          Send <strong>"join BalancedBora"</strong> to <strong>+1 (415) 523-8886</strong>
        </p>
      </div>
    </section>
  )
}

export default WhatsAppCTA