import { ArrowRight, Play, Brain, Leaf, TrendingDown } from 'lucide-react'

export default function Hero() {
  return (
    <section
      id="home"
      className="relative min-h-screen flex items-center pt-20 overflow-hidden bg-gradient-to-br from-bora-50 via-white to-earth-50"
    >
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute top-20 left-10 w-72 h-72 bg-bora-200 rounded-full blur-3xl" />
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-bora-100 rounded-full blur-3xl" />
      </div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 lg:py-32">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Text Content */}
          <div className="space-y-8 animate-fade-in-up">
            {/* Badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-bora-100 text-bora-800 rounded-full text-sm font-medium">
              <Brain className="w-4 h-4" />
              <span>Powered by Artificial Intelligence</span>
            </div>

            {/* Headline */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-earth-900 leading-tight text-balance">
              BalancedBora{' '}
              <span className="text-bora-600">AI</span>
            </h1>

            {/* Subtitle */}
            <p className="text-lg sm:text-xl text-earth-600 leading-relaxed max-w-xl">
              AI-powered livestock feed formulation for affordable, climate-smart dairy farming in Africa.
            </p>

            {/* CTAs */}
            <div className="flex flex-wrap gap-4">
              <a
                href="#demo"
                className="inline-flex items-center gap-2 px-8 py-4 bg-bora-600 text-white font-semibold rounded-full hover:bg-bora-700 transition-all hover:shadow-xl hover:shadow-bora-600/20 active:scale-95"
              >
                <Play className="w-5 h-5" />
                Try the Demo
              </a>
              <a
                href="#solution"
                className="inline-flex items-center gap-2 px-8 py-4 bg-white text-earth-800 font-semibold rounded-full border-2 border-earth-200 hover:border-bora-300 hover:text-bora-700 transition-all active:scale-95"
              >
                Learn More
                <ArrowRight className="w-5 h-5" />
              </a>
            </div>

            {/* Trust Indicators */}
            <div className="flex items-center gap-6 pt-4 text-sm text-earth-500">
              <div className="flex items-center gap-2">
                <Leaf className="w-4 h-4 text-bora-500" />
                <span>Climate-Smart</span>
              </div>
              <div className="flex items-center gap-2">
                <TrendingDown className="w-4 h-4 text-bora-500" />
                <span>Cost Optimized</span>
              </div>
            </div>
          </div>

          {/* Hero Illustration */}
          <div className="relative lg:h-[500px] flex items-center justify-center animate-float">
            <div className="relative w-full max-w-md aspect-square">
              {/* Main Circle */}
              <div className="absolute inset-0 rounded-full bg-gradient-to-br from-bora-100 to-bora-50 border-2 border-bora-200" />

              {/* Inner Content */}
              <div className="absolute inset-8 rounded-full bg-white shadow-xl flex flex-col items-center justify-center p-8 text-center">
                <div className="w-20 h-20 rounded-2xl bg-bora-600 flex items-center justify-center mb-4 shadow-lg shadow-bora-600/30">
                  <Brain className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold text-earth-900 mb-2">Smart Formulation</h3>
                <p className="text-earth-500 text-sm leading-relaxed">
                  Optimized rations tailored to your herd's needs using advanced AI algorithms
                </p>
              </div>

              {/* Orbiting Elements */}
              <div className="absolute -top-2 left-1/2 -translate-x-1/2 w-14 h-14 bg-white rounded-xl shadow-lg flex items-center justify-center border border-earth-100">
                <Leaf className="w-7 h-7 text-bora-500" />
              </div>
              <div className="absolute top-1/2 -right-2 -translate-y-1/2 w-14 h-14 bg-white rounded-xl shadow-lg flex items-center justify-center border border-earth-100">
                <TrendingDown className="w-7 h-7 text-bora-500" />
              </div>
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-14 h-14 bg-white rounded-xl shadow-lg flex items-center justify-center border border-earth-100">
                <svg className="w-7 h-7 text-bora-500" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-.62.08-1.21.21-1.79L9 15v1c0 1.1.9 2 2 2v1.93zm6.9-2.54c-.26-.81-1-1.39-1.9-1.39h-1v-3c0-.55-.45-1-1-1H8v-2h2c.55 0 1-.45 1-1V7h2c1.1 0 2-.9 2-2v-.41c2.93 1.19 5 4.06 5 7.41 0 2.08-.8 3.97-2.1 5.39z"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Wave */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 120" fill="none" xmlns="http://www.w3.org/2000/svg" className="w-full">
          <path
            d="M0 120L60 110C120 100 240 80 360 70C480 60 600 60 720 65C840 70 960 80 1080 85C1200 90 1320 90 1380 90L1440 90V120H1380C1320 120 1200 120 1080 120C960 120 840 120 720 120C600 120 480 120 360 120C240 120 120 120 60 120H0Z"
            fill="white"
          />
        </svg>
      </div>
    </section>
  )
}
