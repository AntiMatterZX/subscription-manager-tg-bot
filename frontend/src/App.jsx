import { Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import ProductList from './pages/ProductList'
import SubscriptionForm from './pages/SubscriptionForm'
import AdminProducts from './pages/admin/Products'
import AdminGroups from './pages/admin/Groups'
import AdminSubscriptions from './pages/admin/Subscriptions'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<ProductList />} />
          <Route path="/subscribe/:productId" element={<SubscriptionForm />} />
          <Route path="/admin/products" element={<AdminProducts />} />
          <Route path="/admin/groups" element={<AdminGroups />} />
          <Route path="/admin/subscriptions" element={<AdminSubscriptions />} />
        </Routes>
      </div>
    </div>
  )
}

export default App