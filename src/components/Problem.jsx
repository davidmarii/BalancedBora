import { AlertTriangle, DollarSign, ThermometerSun, Users } from 'lucide-react'

const problems = [
  {
    icon: DollarSign,
    title: 'Feed Costs Are Skyrocketing',
    description:
      'Commercial dairy feed prices have risen over 40% in the past 3 years, eating into already thin profit margins for smallholder farmers.',
    stat: '+40%',
    statLabel: 'Price increase',
  },
  {
    icon: Users,
    title: 'Smallholders Are Left Behind',
    description:
      'Most feed formulation tools are designed for industrial farms. Smallholder farmers lack access to affordable, tailored nutritional advice.',
    stat: '80%',
    statLabel: 'Are smallholders',
  },
  {
    icon: ThermometerSun,
    title: 'Climate Change Hits Hard',
    description:
      'Erratic rainfall and heat stress reduce pasture quality and cow productivity, making optimal nutrition even more critical.',
    stat: '30%',
    statLabel: 'Yield loss',
  },
  {
    icon: AlertTriangle,
    title: 'Nutritional Imbalance',
    description:
      'Farmers often overfeed expensive concentrates or underfeed key nutrients, leading to poor milk yield and animal health issues.',
    stat: '60%',
    statLabel: 'Rations imbalanced',
  },
]

export default function Problem() {
  return (
    <section id="about" className="py-24 bg-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="text-center max-w-3xl mx-auto mb-16 animate-on-scroll">
          <span className="inline-block px-4 py-1.5 bg-red-50 text-red-700 rounded-full text-sm font-semibold mb-4">
            The Challenge
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-earth-900 mb-6 text-balance">
            Why Dairy Farming in Africa Needs a New Approach
          </h2>
          <p className="text-lg text-earth-600 leading-relaxed">
            Smallholder dairy farmers face a perfect storm of rising costs, climate pressures, and limited access to expert nutritional guidance.
          </p>
        </div>

        {/* Problem Cards */}
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
          {problems.map((problem, index) => (
            <div
              key={problem.title}
              className="group relative p-6 rounded-2xl bg-earth-50 border border-earth-100 hover:border-bora-200 hover:shadow-lg hover:shadow-bora-600/5 transition-all duration-300 animate-on-scroll"
              style={{ transitionDelay: `${index * 100}ms` }}
            >
              {/* Stat Badge */}
              <div className="absolute -top-3 right-4 px-3 py-1 bg-white rounded-full shadow-sm border border-earth-100">
                <span className="text-sm font-bold text-bora-700">{problem.stat}</span>
                <span className="text-xs text-earth-500 ml-1">{problem.statLabel}</span>
              </div>

              {/* Icon */}
              <div className="w-12 h-12 rounded-xl bg-red-50 flex items-center justify-center mb-4 group-hover:bg-bora-50 transition-colors">
                <problem.icon className="w-6 h-6 text-red-500 group-hover:text-bora-600 transition-colors" />
              </div>

              {/* Content */}
              <h3 className="text-lg font-bold text-earth-900 mb-2">{problem.title}</h3>
              <p className="text-sm text-earth-600 leading-relaxed">{problem.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  )
}
