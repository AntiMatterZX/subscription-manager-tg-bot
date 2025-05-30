import { useState, useEffect } from 'react'
import { getSubscriptions, getProducts } from '../../services/api'

function Subscriptions() {
  const [subscriptions, setSubscriptions] = useState([])
  const [products, setProducts] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [filter, setFilter] = useState({
    status: '',
    productId: ''
  })

  const fetchData = async () => {
    try {
      const [subscriptionsResponse, productsResponse] = await Promise.all([
        getSubscriptions(),
        getProducts()
      ])
      setSubscriptions(subscriptionsResponse.data)
      setProducts(productsResponse.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to load data. Please try again later.')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  // Get status badge color
  const getStatusBadgeClass = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800'
      case 'pending_join':
        return 'bg-yellow-100 text-yellow-800'
      case 'expired':
        return 'bg-red-100 text-red-800'
      case 'cancelled':
        return 'bg-gray-100 text-gray-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  // Filter subscriptions based on selected filters
  const filteredSubscriptions = subscriptions.filter(subscription => {
    if (filter.status && subscription.status !== filter.status) {
      return false
    }
    if (filter.productId && subscription.product.id.toString() !== filter.productId) {
      return false
    }
    return true
  })

  const handleFilterChange = (e) => {
    const { name, value } = e.target
    setFilter(prev => ({
      ...prev,
      [name]: value
    }))
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading subscriptions...</div>
      </div>
    )
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Manage Subscriptions</h1>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {/* Filters */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <div className="flex flex-wrap gap-4">
          <div className="w-full md:w-auto">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="status">
              Filter by Status
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="status"
              name="status"
              value={filter.status}
              onChange={handleFilterChange}
            >
              <option value="">All Statuses</option>
              <option value="active">Active</option>
              <option value="pending_join">Pending Join</option>
              <option value="expired">Expired</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
          
          <div className="w-full md:w-auto">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="productId">
              Filter by Product
            </label>
            <select
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="productId"
              name="productId"
              value={filter.productId}
              onChange={handleFilterChange}
            >
              <option value="">All Products</option>
              {products.map(product => (
                <option key={product.id} value={product.id}>
                  {product.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                User
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Product
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Telegram Info
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Invite Link
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Expires
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {filteredSubscriptions.length === 0 ? (
              <tr>
                <td colSpan="6" className="px-6 py-4 text-center text-gray-500">
                  No subscriptions available.
                </td>
              </tr>
            ) : (
              filteredSubscriptions.map(subscription => (
                <tr key={subscription.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{subscription.user.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{subscription.product.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusBadgeClass(subscription.status)}`}>
                      {subscription.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {subscription.user.telegram_user_id ? (
                      <div>
                        <div className="text-sm text-gray-900">ID: {subscription.user.telegram_user_id}</div>
                        {subscription.user.telegram_username && (
                          <div className="text-sm text-gray-500">@{subscription.user.telegram_username}</div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500">Not joined yet</span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    {subscription.invite_link_url ? (
                      <div className="text-sm text-gray-500 truncate max-w-xs">
                        <a 
                          href={subscription.invite_link_url} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:underline"
                        >
                          View Link
                        </a>
                        <div className="text-xs">
                          Expires: {formatDate(subscription.invite_link_expires_at)}
                        </div>
                      </div>
                    ) : (
                      <span className="text-sm text-gray-500">No link</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {formatDate(subscription.subscription_expires_at)}
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}

export default Subscriptions