import { Link } from "react-router-dom";

function ProductCard({ product }) {
  return (
    <div className="card group">
      <div className="h-2 gradient-primary"></div>
      <div className="p-6">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-bold text-gray-800 group-hover:text-purple-700 transition-colors">{product.name}</h2>
          {product.telegram_group && (
            <span className="badge-primary flex items-center">
              <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path d="M18 5v8a2 2 0 01-2 2h-5l-5 4v-4H4a2 2 0 01-2-2V5a2 2 0 012-2h12a2 2 0 012 2z"></path>
              </svg>
              Telegram
            </span>
          )}
        </div>
        
        <p className="text-gray-600 mb-6 line-clamp-3">{product.description || 'No description available'}</p>
        
        <div className="mt-auto pt-4 border-t border-gray-100 flex items-center justify-between">
          <Link
            to={`/subscribe/${product.id}`}
            className="btn-primary flex items-center"
          >
            <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            Subscribe
          </Link>
          
          <span className="text-sm text-gray-500">
            {product.created_at && new Date(product.created_at).toLocaleDateString()}
          </span>
        </div>
      </div>
    </div>
  );
}

export default ProductCard;
