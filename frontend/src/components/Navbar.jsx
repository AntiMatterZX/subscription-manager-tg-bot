import { useState } from 'react'
import { Link } from 'react-router-dom'

function Navbar() {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false)
  
  const toggleDropdown = () => {
    setIsDropdownOpen(!isDropdownOpen)
  }

  return (
    <nav className="bg-blue-600 text-white shadow-md">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <Link to="/" className="text-xl font-bold">TG Manager</Link>
          
          <div className="flex space-x-4">
            <Link to="/" className="hover:text-blue-200">Products</Link>
            <div className="relative">
              <button 
                onClick={toggleDropdown} 
                className="hover:text-blue-200 focus:outline-none"
              >
                Admin
              </button>
              {isDropdownOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10">
                  <div className="py-1">
                    <Link 
                      to="/admin/products" 
                      className="block px-4 py-2 text-gray-800 hover:bg-blue-500 hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Products
                    </Link>
                    <Link 
                      to="/admin/groups" 
                      className="block px-4 py-2 text-gray-800 hover:bg-blue-500 hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Groups
                    </Link>
                    <Link 
                      to="/admin/subscriptions" 
                      className="block px-4 py-2 text-gray-800 hover:bg-blue-500 hover:text-white"
                      onClick={() => setIsDropdownOpen(false)}
                    >
                      Subscriptions
                    </Link>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default Navbar