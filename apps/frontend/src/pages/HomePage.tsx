export default function HomePage() {
  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">
        Car Rental Management System
      </h1>
      
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Quick Stats
          </h2>
          <div className="space-y-2">
            <p className="text-gray-600">Total Contracts: <span className="font-medium">0</span></p>
            <p className="text-gray-600">Active Bookings: <span className="font-medium">0</span></p>
            <p className="text-gray-600">Available Cars: <span className="font-medium">0</span></p>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Recent Activity
          </h2>
          <p className="text-gray-500">No recent activity</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            System Status
          </h2>
          <div className="flex items-center">
            <div className="w-3 h-3 bg-green-400 rounded-full mr-2"></div>
            <span className="text-gray-600">All systems operational</span>
          </div>
        </div>
      </div>
    </div>
  )
}