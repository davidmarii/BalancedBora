import { Cpu, Calculator, BarChart3, Globe, CheckCircle2 } from 'lucide-react'

const features = [
  {
    icon: Cpu,
    title: 'AI Recommendation Engine',
    description: 'Machine learning models analyze your local feed ingredients and recommend optimal rations.',
  },
  {
    icon: Calculator,
    title: 'Cost Optimizer',
    description: 'Linear programming minimizes feed cost while meeting all nutritional requirements (NRC standards).',
  },
  {
    icon: BarChart3,
    title: 'Real-Time Analytics',
    description: 'Track cost per liter of milk, feed efficiency, and nutritional adequacy in one dashboard.',
  },
  {
    icon: Globe,
    title: 'Multilingual Support',
    description: 'Available in English, Swahili, Amharic, and more — built for African farmers first.',
  },
]

const steps = [
  'Select your animal type & production stage',
  'Choose from locally available feed ingredients',
  'Set your budget or nutritional targets',
  'Click "Formulate" — AI builds the optimal ration',
]

export default function Solution() {
  return (
    <section id="solution" className="py-24 bg-gradient-to-b from-earth-50 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 animate-on-scroll">
          <span className="inline-block px-4 py-1.5 bg-bora-100 text-bora-800 rounded-full text-sm font-semibold mb-4">
            Our Solution
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-earth-900 mb-6 text-balance">
            Precision Nutrition, Powered by AI
          </h2>
          <p className="text-lg text-earth-600 leading-relaxed">
            BalancedBora combines cutting-edge artificial intelligence with deep agricultural expertise to deliver feed formulations that are affordable, sustainable, and scientifically sound.
          </p>
        </div>

        {/* Features Grid */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-20">
          {features.map((feature, index) => (
            <div
              key={feature.title}
              className="p-6 rounded-2xl bg-white border border-earth-100 shadow-sm hover:shadow-md hover:border-bora-200 transition-all duration-300 animate-on-scroll"
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              <div className="w-12 h-12 rounded-xl bg-bora-50 flex items-center justify-center mb-4">
                <feature.icon className="w-6 h-6 text-bora-600" />
              </div>
              <h3 className="text-lg font-bold text-earth-900 mb-2">{feature.title}</h3>
              <p className="text-sm text-earth-600 leading-relaxed">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* How It Works */}
        <div className="max-w-4xl mx-auto animate-on-scroll">
          <div className="text-center mb-10">
            <h3 className="text-2xl font-bold text-earth-900">How It Works</h3>
            <p className="text-earth-600 mt-2">From ingredients to optimized ration in four simple steps</p>
          </div>

          <div className="relative">
            {/* Connecting Line */}
            <div className="absolute left-6 top-8 bottom-8 w-0.5 bg-bora-200 hidden sm:block" />

            <div className="space-y-6">
              {steps.map((step, index) => (
                <div
                  key={index}
                  className="flex items-start gap-4 sm:gap-6 group"
                >
                  <div className="relative flex-shrink-0 w-12 h-12 rounded-full bg-bora-600 text-white flex items-center justify-center font-bold text-lg shadow-lg shadow-bora-600/20 z-10 group-hover:scale-110 transition-transform">
                    {index + 1}
                  </div>
                  <div className="flex-1 p-4 rounded-xl bg-white border border-earth-100 shadow-sm group-hover:border-bora-200 group-hover:shadow-md transition-all">
                    <div className="flex items-center gap-3">
                      <CheckCircle2 className="w-5 h-5 text-bora-500 flex-shrink-0" />
                      <p className="text-earth-800 font-medium">{step}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
