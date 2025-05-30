import { useState, useEffect } from 'react'
import { getProducts, createProduct, updateProduct, deleteProduct, mapProductToGroup, getGroups, getUnmappedGroups } from '../../services/api'

function Products() {
  const [products, setProducts] = useState([])
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [isMapModalOpen, setIsMapModalOpen] = useState(false)
  const [currentProduct, setCurrentProduct] = useState(null)
  const [selectedGroup, setSelectedGroup] = useState('')
  const [formData, setFormData] = useState({
    name: '',
    description: ''
  })

  const fetchData = async () => {
    try {
      const [productsResponse, groupsResponse] = await Promise.all([
        getProducts(),
        getUnmappedGroups()
      ])
      setProducts(productsResponse.data)
      setGroups(groupsResponse.data)
      setLoading(false)
    } catch (err) {
      setError('Failed to load data. Please try again later.')
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
  }, [])

  const handleOpenModal = (product = null) => {
    if (product) {
      setCurrentProduct(product)
      setFormData({
        name: product.name,
        description: product.description || ''
      })
    } else {
      setCurrentProduct(null)
      setFormData({
        name: '',
        description: ''
      })
    }
    setIsModalOpen(true)
  }

  const handleCloseModal = () => {
    setIsModalOpen(false)
    setCurrentProduct(null)
  }

  const handleOpenMapModal = (product) => {
    setCurrentProduct(product)
    setSelectedGroup('')
    setIsMapModalOpen(true)
  }

  const handleCloseMapModal = () => {
    setIsMapModalOpen(false)
    setCurrentProduct(null)
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData({
      ...formData,
      [name]: value
    })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    try {
      const productData = {
        ...formData
      }
      
      if (currentProduct) {
        await updateProduct(currentProduct.id, productData)
      } else {
        await createProduct(productData)
      }
      
      handleCloseModal()
      fetchData()
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to save product. Please try again.')
    }
  }

  const handleMapSubmit = async (e) => {
    e.preventDefault()
    
    if (!selectedGroup) {
      setError('Please select a group')
      return
    }
    
    try {
      const group = groups.find(g => g.id.toString() === selectedGroup)
      
      await mapProductToGroup(currentProduct.id, {
        telegram_group_id: group.telegram_group_id,
        telegram_group_name: group.telegram_group_name
      })
      
      handleCloseMapModal()
      fetchData()
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to map product to group. Please try again.')
    }
  }

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this product?')) {
      try {
        await deleteProduct(id)
        fetchData()
      } catch (err) {
        setError(err.response?.data?.message || 'Failed to delete product. Please try again.')
      }
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="text-gray-600">Loading products...</div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Manage Products</h1>
        <button
          onClick={() => handleOpenModal()}
          className="btn-primary"
        >
          Add Product
        </button>
      </div>
      
      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}
      
      <div className="bg-white shadow-md rounded-lg overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Name
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Description
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Group Status
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {products.length === 0 ? (
              <tr>
                <td colSpan="4" className="px-6 py-4 text-center text-gray-500">
                  No products available.
                </td>
              </tr>
            ) : (
              products.map(product => (
                <tr key={product.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{product.name}</div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500 truncate max-w-xs">
                      {product.description || '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    {product.telegram_group ? (
                      product.telegram_group.is_active ? (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-green-100 text-green-800">
                          Mapped to {product.telegram_group.telegram_group_name}
                        </span>
                      ) : (
                        <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-red-100 text-red-800">
                          Mapped to inactive group: {product.telegram_group.telegram_group_name}
                        </span>
                      )
                    ) : (
                      <span className="px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-gray-100 text-gray-800">
                        Not Mapped
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleOpenModal(product)}
                      className="text-blue-600 hover:text-blue-900 mr-2"
                    >
                      Edit
                    </button>
                    {!product.telegram_group && groups.length > 0 && (
                      <button
                        onClick={() => handleOpenMapModal(product)}
                        className="text-green-600 hover:text-green-900 mr-2"
                      >
                        Map
                      </button>
                    )}
                    <button
                      onClick={() => handleDelete(product.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
      
      {/* Product Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">
              {currentProduct ? 'Edit Product' : 'Add Product'}
            </h2>
            
            <form onSubmit={handleSubmit}>
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="name">
                  Name
                </label>
                <input
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="name"
                  name="name"
                  type="text"
                  placeholder="Product Name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                />
              </div>
              
              <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="description">
                  Description
                </label>
                <textarea
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="description"
                  name="description"
                  placeholder="Product Description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                />
              </div>
              

              
              <div className="flex items-center justify-between">
                <button
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  type="submit"
                >
                  Save
                </button>
                <button
                  type="button"
                  onClick={handleCloseModal}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      
      {/* Map Modal */}
      {isMapModalOpen && currentProduct && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-8 max-w-md w-full">
            <h2 className="text-xl font-bold mb-4">
              Map Product to Group
            </h2>
            
            <p className="mb-4">
              <span className="font-bold">Product:</span> {currentProduct.name}
            </p>
            
            <form onSubmit={handleMapSubmit}>
              <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="group">
                  Select Group
                </label>
                <select
                  className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                  id="group"
                  value={selectedGroup}
                  onChange={(e) => setSelectedGroup(e.target.value)}
                  required
                >
                  <option value="">-- Select a Group --</option>
                  {groups.map(group => (
                    <option key={group.id} value={group.id}>
                      {group.telegram_group_name}
                    </option>
                  ))}
                </select>
                {groups.length === 0 && (
                  <p className="text-red-500 text-xs italic mt-2">
                    No unmapped groups available. Add the bot to a Telegram group first.
                  </p>
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <button
                  className="bg-blue-600 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                  type="submit"
                  disabled={groups.length === 0}
                >
                  Map
                </button>
                <button
                  type="button"
                  onClick={handleCloseMapModal}
                  className="bg-gray-300 hover:bg-gray-400 text-gray-800 font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

export default Products