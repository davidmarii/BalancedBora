import { Users, TrendingUp, MapPin, Truck } from 'lucide-react'

function Impact() {
  return (
    <section id="impact" className="py-20 px-6 bg-white animate-on-scroll">
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Real Impact on the Ground
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto">
            We're already helping farmers cut feed costs and boost productivity — one ration at a time.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid md:grid-cols-3 gap-6 mb-16">
          {/* Farmers Reached */}
          <div className="bg-emerald-50 rounded-2xl p-8 text-center">
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 mx-auto mb-4">
              <Users size={28} />
            </div>
            <p className="text-4xl font-bold text-gray-900 mb-2">50+</p>
            <p className="text-gray-600 font-medium">Farmers Reached</p>
            <p className="text-sm text-gray-500 mt-2">Tharaka Nithi County</p>
          </div>

          {/* Productivity Gain */}
          <div className="bg-emerald-50 rounded-2xl p-8 text-center">
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 mx-auto mb-4">
              <TrendingUp size={28} />
            </div>
            <p className="text-4xl font-bold text-gray-900 mb-2">↑</p>
            <p className="text-gray-600 font-medium">Increased Productivity</p>
            <p className="text-sm text-gray-500 mt-2">Reported by chicken & pig farmers</p>
          </div>

          {/* Expansion Target */}
          <div className="bg-emerald-50 rounded-2xl p-8 text-center">
            <div className="w-14 h-14 bg-emerald-100 rounded-full flex items-center justify-center text-emerald-600 mx-auto mb-4">
              <MapPin size={28} />
            </div>
            <p className="text-4xl font-bold text-gray-900 mb-2">2</p>
            <p className="text-gray-600 font-medium">Regions Targeted</p>
            <p className="text-sm text-gray-500 mt-2">Meru & Mount Kenya</p>
          </div>
        </div>

        {/* Detailed Story */}
        <div className="grid md:grid-cols-2 gap-8">
          {/* Farmer Focus */}
          <div className="bg-gray-50 rounded-2xl p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Users size={20} className="text-emerald-600" />
              Farmer Success Stories
            </h3>
            <p className="text-gray-600 leading-relaxed mb-4">
              We've partnered with <strong>50 farmers in Tharaka Nithi County</strong>, 
              primarily <strong>chicken and pig farmers</strong>, who have adopted our 
              AI-powered feed formulations.
            </p>
            <p className="text-gray-600 leading-relaxed">
              These farmers have <strong>reported increased productivity</strong> — 
              better growth rates, improved feed conversion, and lower costs per kilogram 
              of meat or eggs produced.
            </p>
          </div>

          {/* Supplier Network */}
          <div className="bg-gray-50 rounded-2xl p-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center gap-2">
              <Truck size={20} className="text-emerald-600" />
              Supplier Network
            </h3>
            <p className="text-gray-600 leading-relaxed mb-4">
              BalancedBora is <strong>continually engaging feed suppliers</strong> to build 
              a reliable supply chain that connects farmers directly to quality, affordable 
              feed ingredients.
            </p>
            <p className="text-gray-600 leading-relaxed">
              Our goal is to <strong>link suppliers with farmers</strong> — cutting out 
              middlemen, reducing costs, and ensuring consistent access to the right 
              nutrients at the right price.
            </p>
          </div>
        </div>

        {/* Expansion Banner */}
        <div className="mt-12 bg-emerald-600 rounded-2xl p-8 text-center text-white">
          <MapPin size={32} className="mx-auto mb-4 opacity-80" />
          <h3 className="text-2xl font-bold mb-2">Growing Beyond Tharaka Nithi</h3>
          <p className="text-emerald-100 max-w-xl mx-auto">
            We're actively expanding to reach more farmers in <strong>Meru</strong> and 
            the <strong>Mount Kenya</strong> region. If you're a farmer or supplier in 
            these areas, we'd love to hear from you.
          </p>
        </div>
      </div>
    </section>
  )
}

export default Impact