import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { getProduct, createSubscription } from '../services/api'

function SubscriptionForm() {
  const { productId } = useParams()
  const navigate = useNavigate()
  
  const [product, setProduct] = useState(null)
  const [email, setEmail] = useState('')
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const [subscriptionData, setSubscriptionData] = useState(null)

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await getProduct(productId)
        setProduct(response.data)
        setLoading(false)
      } catch (err) {
        setError('Failed to load product information. Please try again later.')
        setLoading(false)
      }
    }

    fetchProduct()
  }, [productId])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    
    try {
      const response = await createSubscription({ email, product_id: parseInt(productId) })
      setSuccess('Subscription created successfully!')
      setSubscriptionData(response.data)
      setSubmitting(false)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create subscription. Please try again.')
      setSubmitting(false)
    }
  }

  // Format date for display
  const formatDate = (dateString) => {
    if (!dateString) return '-'
    const date = new Date(dateString)
    return date.toLocaleString()
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading product information...</div>
      </div>
    )
  }

  if (!product) {
    return (
      <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
        Product not found.
      </div>
    )
  }

  // Check if product has a mapped Telegram group
  const hasTelegramGroup = !!product.telegram_group;

  return (
    <div className="max-w-md mx-auto">
      <h1 className="text-2xl font-bold text-gray-800 mb-6">Subscribe to {product.name}</h1>
      
      {!hasTelegramGroup && (
        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded mb-4">
          This product is not currently mapped to a Telegram group. You can still subscribe, but you won't receive an invite link.
        </div>
      )}
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      {success ? (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          <p className="font-bold">{success}</p>
          
          {subscriptionData?.invite_link && (
            <div className="mt-4">
              <p className="mb-2">Your Telegram group invite link:</p>
              <div className="bg-gray-100 p-3 rounded break-all">
                <a 
                  href={subscriptionData.invite_link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  {subscriptionData.invite_link}
                </a>
              </div>
              <p className="text-sm text-gray-600 mt-2">
                This link is valid until {formatDate(subscriptionData.invite_expires_at)} and can only be used once.
              </p>
            </div>
          )}
          
          <div className="mt-4">
            <p className="mb-2">Subscription Details:</p>
            <ul className="list-disc pl-5">
              <li>Product: {product.name}</li>
              <li>Subscription expires: {formatDate(subscriptionData?.subscription_expires_at)}</li>
            </ul>
          </div>
          
          <button
            onClick={() => navigate('/')}
            className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
          >
            Back to Products
          </button>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
          <div className="mb-4">
            <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
              Email Address
            </label>
            <input
              className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
              id="email"
              type="email"
              placeholder="your@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>
          
          <div className="mb-6">
            {product.description && (
              <p className="text-gray-700 mt-2">
                <span className="font-bold">Description:</span> {product.description}
              </p>
            )}
            {product.telegram_group && (
              <p className="text-gray-700 mt-2">
                <span className="font-bold">Telegram Group:</span> {product.telegram_group.telegram_group_name}
              </p>
            )}
          </div>
          
          <div className="flex items-center justify-between">
            <button
              className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
              type="submit"
              disabled={submitting}
            >
              {submitting ? 'Processing...' : 'Subscribe'}
            </button>
            <button
              type="button"
              onClick={() => navigate('/')}
              className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
            >
              Cancel
            </button>
          </div>
        </form>
      )}
    </div>
  )
}

export default SubscriptionForm