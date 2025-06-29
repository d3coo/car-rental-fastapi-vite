import { useQuery } from '@tanstack/react-query'
import { getCars } from '@/lib/api'

export default function CarsPage() {
  const { data: cars, isLoading, error } = useQuery({
    queryKey: ['cars'],
    queryFn: getCars,
  })

  if (isLoading) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/4 mb-6"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="h-64 bg-gray-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto">
        <div className="bg-red-50 border border-red-200 rounded-md p-4">
          <p className="text-red-600">Error loading cars: {error.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Cars</h1>
        <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">
          Add Car
        </button>
      </div>

      {cars && cars.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {cars.map((car) => (
            <div key={car.id} className="bg-white shadow rounded-lg overflow-hidden">
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-medium text-gray-900">
                    {car.display_name}
                  </h3>
                  <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                    car.status === 'available'
                      ? 'bg-green-100 text-green-800'
                      : car.status === 'maintenance'
                      ? 'bg-yellow-100 text-yellow-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {car.status}
                  </span>
                </div>
                
                <div className="space-y-2 text-sm text-gray-600">
                  <div className="flex justify-between">
                    <span>License Plate:</span>
                    <span className="font-medium">{car.license_plate}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Category:</span>
                    <span className="font-medium">{car.category}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Year:</span>
                    <span className="font-medium">{car.year}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Seats:</span>
                    <span className="font-medium">{car.seats}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Transmission:</span>
                    <span className="font-medium capitalize">{car.transmission}</span>
                  </div>
                  <div className="flex justify-between">
                    <span>Daily Rate:</span>
                    <span className="font-medium">{car.daily_rate} {car.currency}</span>
                  </div>
                </div>

                {car.features && car.features.length > 0 && (
                  <div className="mt-4">
                    <div className="text-sm text-gray-600 mb-2">Features:</div>
                    <div className="flex flex-wrap gap-1">
                      {car.features.map((feature, index) => (
                        <span
                          key={index}
                          className="inline-flex px-2 py-1 text-xs bg-blue-100 text-blue-800 rounded"
                        >
                          {feature}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                <div className="mt-4 flex space-x-2">
                  <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700 transition-colors">
                    View Details
                  </button>
                  <button className="flex-1 bg-gray-600 text-white px-3 py-2 rounded text-sm hover:bg-gray-700 transition-colors">
                    Edit
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="bg-white shadow rounded-lg p-12 text-center">
          <p className="text-gray-500">No cars found</p>
        </div>
      )}
    </div>
  )
}