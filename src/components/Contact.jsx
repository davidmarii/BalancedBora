import { Phone, Mail, MessageCircle } from 'lucide-react'

function Contact() {
  return (
    <section id="contact" className="py-20 px-6 bg-emerald-50 animate-on-scroll">
      <div className="max-w-4xl mx-auto text-center">
        <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
          Get in Touch
        </h2>
        <p className="text-gray-600 mb-12 max-w-xl mx-auto">
          Have questions about feed formulation? Reach out — we're here to help.
        </p>

        <div className="grid md:grid-cols-3 gap-6 max-w-3xl mx-auto">
          {/* WhatsApp Bot */}
          <a
            href="https://wa.me/14155238886?text=join%20 BalancedBora"
            target="_blank"
            rel="noopener noreferrer"
            className="flex flex-col items-center gap-4 p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow md:col-span-1"
          >
            <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center text-green-600">
              <MessageCircle size={24} />
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 font-medium">WhatsApp Bot</p>
              <p className="text-gray-900 font-semibold">BalancedBora</p>
              <p className="text-xs text-gray-400 mt-1">+1 (415) 523-8886</p>
            </div>
          </a>

          {/* Phone */}
          <a
            href="tel:+254703709346"
            className="flex flex-col items-center gap-4 p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600">
              <Phone size={24} />
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 font-medium">Phone</p>
              <p className="text-gray-900 font-semibold">+254 703 709 346</p>
            </div>
          </a>

          {/* Email */}
          <a
            href="mailto:davidmarii013@gmail.com"
            className="flex flex-col items-center gap-4 p-6 bg-white rounded-2xl shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600">
              <Mail size={24} />
            </div>
            <div className="text-center">
              <p className="text-sm text-gray-500 font-medium">Email</p>
              <p className="text-gray-900 font-semibold text-sm">davidmarii013@gmail.com</p>
            </div>
          </a>
        </div>

        <div className="mt-10 p-4 bg-green-50 border border-green-200 rounded-xl max-w-lg mx-auto">
          <p className="text-sm text-green-800 font-medium">
            ?? Try our AI feed formulation bot on WhatsApp — send <strong>"join BalancedBora"</strong> to <strong>+1 (415) 523-8886</strong>
          </p>
        </div>

        <p className="mt-6 text-sm text-gray-500">
          Based in Kenya · Serving farmers across Africa
        </p>
      </div>
    </section>
  )
}

export default Contact