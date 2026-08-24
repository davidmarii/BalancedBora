import { useState } from 'react'
import { 
  Beef, 
  Rabbit, 
  Dog, 
  Sprout, 
  Leaf, 
  Droplets, 
  Flame,
  Fish,
  Star,
  Circle,
  Calculator,
  CheckCircle2,
  ArrowRight,
  ArrowLeft,
  RefreshCw,
  TrendingDown,
  TrendingUp,
  DollarSign,
  Scale
} from 'lucide-react'

const animals = [
  { id: 'dairy-cow', name: 'Dairy Cow', icon: Beef, desc: 'Lactating (20L/day)', stage: 'Early Lactation' },
  { id: 'goat', name: 'Dairy Goat', icon: Rabbit, desc: 'Lactating (3L/day)', stage: 'Mid Lactation' },
  { id: 'sheep', name: 'Meat Sheep', icon: Dog, desc: 'Growing (30kg)', stage: 'Finishing' },
]

const feeds = [
  { id: 'napier', name: 'Napier Grass', type: 'Forage', price: 8, dm: 18, cp: 10, energy: 1.8, icon: Leaf },
  { id: 'maize-silage', name: 'Maize Silage', type: 'Forage', price: 12, dm: 30, cp: 8, energy: 2.0, icon: Sprout },
  { id: 'dairy-meal', name: 'Dairy Meal', type: 'Concentrate', price: 45, dm: 88, cp: 18, energy: 3.2, icon: Circle },
  { id: 'sunflower', name: 'Sunflower Cake', type: 'Protein', price: 35, dm: 90, cp: 32, energy: 2.5, icon: Star },
  { id: 'wheat-bran', name: 'Wheat Bran', type: 'Concentrate', price: 22, dm: 89, cp: 15, energy: 2.6, icon: Sprout },
  { id: 'fish-meal', name: 'Fish Meal', type: 'Protein', price: 85, dm: 92, cp: 55, energy: 3.8, icon: Fish },
  { id: 'molasses', name: 'Molasses', type: 'Energy', price: 18, dm: 75, cp: 4, energy: 2.9, icon: Droplets },
  { id: 'lucerne', name: 'Lucerne Hay', type: 'Forage', price: 25, dm: 90, cp: 18, energy: 1.9, icon: Leaf },
]

const requirements = {
  'dairy-cow': { dm: 18, cp: 16, energy: 2.8, name: 'Dairy Cow' },
  'goat': { dm: 3.5, cp: 14, energy: 2.6, name: 'Dairy Goat' },
  'sheep': { dm: 2.0, cp: 13, energy: 2.4, name: 'Meat Sheep' },
}

export default function Demo() {
  const [step, setStep] = useState(1)
  const [selectedAnimal, setSelectedAnimal] = useState(null)
  const [selectedFeeds, setSelectedFeeds] = useState([])
  const [budget, setBudget] = useState(200)
  const [result, setResult] = useState(null)
  const [formulating, setFormulating] = useState(false)

  const toggleFeed = (feedId) => {
    setSelectedFeeds(prev => 
      prev.includes(feedId) 
        ? prev.filter(id => id !== feedId)
        : [...prev, feedId]
    )
  }

  const handleFormulate = () => {
    setFormulating(true)
    setTimeout(() => {
      const animalReq = requirements[selectedAnimal]
      const chosenFeeds = feeds.filter(f => selectedFeeds.includes(f.id))

      let totalCost = 0
      let totalDM = 0
      let totalCP = 0
      let totalEnergy = 0
      const ration = []

      const sortedFeeds = [...chosenFeeds].sort((a, b) => (b.energy/b.price) - (a.energy/a.price))

      let remainingDM = animalReq.dm

      for (const feed of sortedFeeds) {
        if (remainingDM <= 0) break
        const amount = Math.min(remainingDM * 0.4, remainingDM)
        const cost = (amount / feed.dm * 100) * (feed.price / 100)

        ration.push({
          ...feed,
          amount: Math.round(amount * 10) / 10,
          cost: Math.round(cost * 10) / 10,
          percentage: Math.round((amount / animalReq.dm) * 100)
        })

        totalCost += cost
        totalDM += amount
        totalCP += (amount * feed.cp / 100)
        totalEnergy += (amount * feed.energy)
        remainingDM -= amount
      }

      setResult({
        ration,
        totalCost: Math.round(totalCost * 10) / 10,
        totalDM: Math.round(totalDM * 10) / 10,
        totalCP: Math.round(totalCP * 10) / 10,
        totalEnergy: Math.round(totalEnergy * 10) / 10,
        req: animalReq,
        cpPct: Math.round((totalCP / totalDM) * 100 * 10) / 10,
        energyDensity: totalDM > 0 ? Math.round((totalEnergy / totalDM) * 10) / 10 : 0,
        savings: Math.round((budget - totalCost) * 10) / 10
      })
      setFormulating(false)
      setStep(4)
    }, 2000)
  }

  const reset = () => {
    setStep(1)
    setSelectedAnimal(null)
    setSelectedFeeds([])
    setBudget(200)
    setResult(null)
  }

  return (
    <section id="demo" className="py-24 bg-white">
      <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center max-w-3xl mx-auto mb-12">
          <span className="inline-block px-4 py-1.5 bg-bora-100 text-bora-800 rounded-full text-sm font-semibold mb-4">
            <Calculator className="w-4 h-4 inline mr-1" />
            Interactive Demo
          </span>
          <h2 className="text-3xl sm:text-4xl font-bold text-earth-900 mb-4">
            Try the Feed Formulator
          </h2>
          <p className="text-earth-600">
            Experience how BalancedBora AI optimizes rations in real-time. Select your animal, choose available feeds, and see the magic.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="flex items-center justify-center gap-4 mb-12">
          {[1, 2, 3, 4].map((s) => (
            <div key={s} className="flex items-center gap-4">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all ${
                step >= s 
                  ? 'bg-bora-600 text-white shadow-lg shadow-bora-600/20' 
                  : 'bg-earth-100 text-earth-400'
              }`}>
                {step > s ? <CheckCircle2 className="w-5 h-5" /> : s}
              </div>
              {s < 4 && (
                <div className={`w-12 h-0.5 transition-all ${step > s ? 'bg-bora-600' : 'bg-earth-200'}`} />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Select Animal */}
        {step === 1 && (
          <div className="animate-on-scroll visible">
            <h3 className="text-xl font-bold text-earth-900 text-center mb-8">Select Your Animal</h3>
            <div className="grid sm:grid-cols-3 gap-6">
              {animals.map((animal) => {
                const Icon = animal.icon
                const isSelected = selectedAnimal === animal.id
                return (
                  <button
                    key={animal.id}
                    onClick={() => setSelectedAnimal(animal.id)}
                    className={`p-6 rounded-2xl border-2 text-left transition-all hover:shadow-lg ${
                      isSelected 
                        ? 'border-bora-600 bg-bora-50 shadow-md' 
                        : 'border-earth-100 bg-white hover:border-bora-200'
                    }`}
                  >
                    <div className={`w-14 h-14 rounded-xl flex items-center justify-center mb-4 ${
                      isSelected ? 'bg-bora-600' : 'bg-earth-100'
                    }`}>
                      <Icon className={`w-7 h-7 ${isSelected ? 'text-white' : 'text-earth-500'}`} />
                    </div>
                    <h4 className="text-lg font-bold text-earth-900 mb-1">{animal.name}</h4>
                    <p className="text-sm text-earth-500 mb-2">{animal.desc}</p>
                    <span className="inline-block px-3 py-1 bg-earth-100 text-earth-600 rounded-full text-xs font-medium">
                      {animal.stage}
                    </span>
                  </button>
                )
              })}
            </div>
            <div className="flex justify-end mt-8">
              <button
                onClick={() => selectedAnimal && setStep(2)}
                disabled={!selectedAnimal}
                className="inline-flex items-center gap-2 px-6 py-3 bg-bora-600 text-white font-semibold rounded-full hover:bg-bora-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next Step
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Select Feeds */}
        {step === 2 && (
          <div className="animate-on-scroll visible">
            <h3 className="text-xl font-bold text-earth-900 text-center mb-8">Available Feed Ingredients</h3>
            <p className="text-center text-earth-500 mb-8">Select the feeds you have access to on your farm</p>

            <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
              {feeds.map((feed) => {
                const Icon = feed.icon
                const isSelected = selectedFeeds.includes(feed.id)
                return (
                  <button
                    key={feed.id}
                    onClick={() => toggleFeed(feed.id)}
                    className={`relative p-4 rounded-xl border-2 text-left transition-all hover:shadow-md ${
                      isSelected 
                        ? 'border-bora-600 bg-bora-50' 
                        : 'border-earth-100 bg-white hover:border-bora-200'
                    }`}
                  >
                    {isSelected && (
                      <div className="absolute top-3 right-3 w-6 h-6 bg-bora-600 rounded-full flex items-center justify-center">
                        <CheckCircle2 className="w-4 h-4 text-white" />
                      </div>
                    )}
                    <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-3 ${
                      isSelected ? 'bg-bora-600' : 'bg-earth-100'
                    }`}>
                      <Icon className={`w-5 h-5 ${isSelected ? 'text-white' : 'text-earth-500'}`} />
                    </div>
                    <h4 className="font-semibold text-earth-900 text-sm mb-1">{feed.name}</h4>
                    <p className="text-xs text-earth-500 mb-2">{feed.type}</p>
                    <div className="flex items-center gap-1 text-sm font-bold text-bora-700">
                      <DollarSign className="w-3 h-3" />
                      {feed.price} <span className="text-xs font-normal text-earth-400">/kg</span>
                    </div>
                  </button>
                )
              })}
            </div>

            <div className="flex justify-between mt-8">
              <button
                onClick={() => setStep(1)}
                className="inline-flex items-center gap-2 px-6 py-3 text-earth-600 font-semibold hover:text-earth-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                Back
              </button>
              <button
                onClick={() => selectedFeeds.length >= 3 && setStep(3)}
                disabled={selectedFeeds.length < 3}
                className="inline-flex items-center gap-2 px-6 py-3 bg-bora-600 text-white font-semibold rounded-full hover:bg-bora-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next Step
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
            {selectedFeeds.length < 3 && (
              <p className="text-center text-sm text-red-500 mt-2">Select at least 3 feeds to continue</p>
            )}
          </div>
        )}

        {/* Step 3: Set Budget */}
        {step === 3 && (
          <div className="animate-on-scroll visible max-w-xl mx-auto">
            <h3 className="text-xl font-bold text-earth-900 text-center mb-8">Set Your Daily Budget</h3>

            <div className="bg-earth-50 rounded-2xl p-8 mb-8">
              <div className="flex items-center justify-between mb-4">
                <span className="text-earth-600 font-medium">Daily Feed Budget</span>
                <span className="text-3xl font-bold text-bora-700">KES {budget}</span>
              </div>

              <input
                type="range"
                min="50"
                max="500"
                step="10"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                className="w-full h-2 bg-earth-200 rounded-full appearance-none cursor-pointer accent-bora-600"
              />

              <div className="flex justify-between mt-2 text-sm text-earth-400">
                <span>KES 50</span>
                <span>KES 500</span>
              </div>
            </div>

            <div className="bg-bora-50 rounded-xl p-6 mb-8">
              <h4 className="font-semibold text-earth-900 mb-3 flex items-center gap-2">
                <Scale className="w-5 h-5 text-bora-600" />
                Selected Summary
              </h4>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-earth-600">Animal:</span>
                  <span className="font-semibold text-earth-900">{requirements[selectedAnimal]?.name}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-earth-600">Feeds selected:</span>
                  <span className="font-semibold text-earth-900">{selectedFeeds.length} ingredients</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-earth-600">Budget:</span>
                  <span className="font-semibold text-bora-700">KES {budget}/day</span>
                </div>
              </div>
            </div>

            <div className="flex justify-between">
              <button
                onClick={() => setStep(2)}
                className="inline-flex items-center gap-2 px-6 py-3 text-earth-600 font-semibold hover:text-earth-900 transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
                Back
              </button>
              <button
                onClick={handleFormulate}
                disabled={formulating}
                className="inline-flex items-center gap-2 px-8 py-4 bg-bora-600 text-white font-bold rounded-full hover:bg-bora-700 transition-all shadow-lg shadow-bora-600/20"
              >
                {formulating ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Optimizing...
                  </>
                ) : (
                  <>
                    <Calculator className="w-5 h-5" />
                    Formulate Ration
                  </>
                )}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Results */}
        {step === 4 && result && (
          <div className="animate-on-scroll visible">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-4 py-2 bg-bora-100 text-bora-800 rounded-full text-sm font-semibold mb-4">
                <CheckCircle2 className="w-4 h-4" />
                Optimization Complete
              </div>
              <h3 className="text-2xl font-bold text-earth-900">Your Optimized Ration</h3>
            </div>

            {/* Stats Cards */}
            <div className="grid sm:grid-cols-4 gap-4 mb-8">
              <div className="bg-earth-50 rounded-xl p-5 text-center">
                <p className="text-xs text-earth-500 mb-1">Total Cost</p>
                <p className="text-2xl font-bold text-earth-900">KES {result.totalCost}</p>
                <p className={`text-xs font-medium flex items-center justify-center gap-1 mt-1 ${result.savings >= 0 ? 'text-bora-600' : 'text-red-500'}`}>
                  {result.savings >= 0 ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
                  {result.savings >= 0 ? `${result.savings} under budget` : `${Math.abs(result.savings)} over budget`}
                </p>
              </div>
              <div className="bg-earth-50 rounded-xl p-5 text-center">
                <p className="text-xs text-earth-500 mb-1">Dry Matter</p>
                <p className="text-2xl font-bold text-earth-900">{result.totalDM} kg</p>
                <p className="text-xs text-earth-400 mt-1">Required: {result.req.dm} kg</p>
              </div>
              <div className="bg-earth-50 rounded-xl p-5 text-center">
                <p className="text-xs text-earth-500 mb-1">Crude Protein</p>
                <p className="text-2xl font-bold text-earth-900">{result.cpPct}%</p>
                <p className="text-xs text-earth-400 mt-1">Required: {result.req.cp}%</p>
              </div>
              <div className="bg-earth-50 rounded-xl p-5 text-center">
                <p className="text-xs text-earth-500 mb-1">Energy Density</p>
                <p className="text-2xl font-bold text-earth-900">{result.energyDensity}</p>
                <p className="text-xs text-earth-400 mt-1">Required: {result.req.energy}</p>
              </div>
            </div>

            {/* Ration Table */}
            <div className="bg-white rounded-2xl border border-earth-200 overflow-hidden mb-8">
              <div className="px-6 py-4 bg-earth-50 border-b border-earth-100">
                <h4 className="font-bold text-earth-900">Ration Composition</h4>
              </div>
              <div className="divide-y divide-earth-100">
                {result.ration.map((item) => (
                  <div key={item.id} className="px-6 py-4 flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-bora-50 flex items-center justify-center">
                        <item.icon className="w-5 h-5 text-bora-600" />
                      </div>
                      <div>
                        <p className="font-semibold text-earth-900">{item.name}</p>
                        <p className="text-xs text-earth-500">{item.type}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-earth-900">{item.amount} kg DM</p>
                      <p className="text-xs text-earth-500">{item.percentage}% of ration</p>
                    </div>
                    <div className="text-right min-w-[80px]">
                      <p className="font-bold text-bora-700">KES {item.cost}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-6 py-4 bg-earth-50 border-t border-earth-100 flex justify-between items-center">
                <span className="font-bold text-earth-900">Total Daily Cost</span>
                <span className="text-xl font-bold text-bora-700">KES {result.totalCost}</span>
              </div>
            </div>

            {/* Nutrition Adequacy */}
            <div className="bg-bora-50 rounded-xl p-6 mb-8">
              <h4 className="font-bold text-earth-900 mb-4">Nutritional Adequacy</h4>
              <div className="space-y-4">
                {[
                  { label: 'Dry Matter Intake', value: Math.min((result.totalDM / result.req.dm) * 100, 100), target: 100 },
                  { label: 'Crude Protein', value: Math.min((result.cpPct / result.req.cp) * 100, 100), target: 100 },
                  { label: 'Energy Density', value: Math.min((result.energyDensity / result.req.energy) * 100, 100), target: 100 },
                ].map((metric) => (
                  <div key={metric.label}>
                    <div className="flex justify-between text-sm mb-1">
                      <span className="text-earth-700">{metric.label}</span>
                      <span className={`font-semibold ${metric.value >= 90 ? 'text-bora-600' : 'text-amber-600'}`}>
                        {Math.round(metric.value)}%
                      </span>
                    </div>
                    <div className="h-2 bg-earth-200 rounded-full overflow-hidden">
                      <div 
                        className={`h-full rounded-full transition-all duration-1000 ${metric.value >= 90 ? 'bg-bora-500' : 'bg-amber-500'}`}
                        style={{ width: `${metric.value}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-center">
              <button
                onClick={reset}
                className="inline-flex items-center gap-2 px-8 py-4 bg-earth-900 text-white font-bold rounded-full hover:bg-earth-800 transition-all"
              >
                <RefreshCw className="w-5 h-5" />
                Try Another Ration
              </button>
            </div>
          </div>
        )}
      </div>
    </section>
  )
}
