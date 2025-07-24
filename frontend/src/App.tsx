import React, { useState, useEffect } from 'react';
import { Search, Loader2, MapPin, Calendar, Users, AlertCircle } from 'lucide-react';
import PropertyCarousel from './components/PropertyCarousel';
import { searchProperties, getHealthStatus, Property, SearchRequest } from './services/api';

function App() {
  const [query, setQuery] = useState('');
  const [properties, setProperties] = useState<Property[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);
  const [favoritedProperties, setFavoritedProperties] = useState<Set<string>>(new Set());
  const [healthStatus, setHealthStatus] = useState<string>('checking');

  // Check health status on mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      await getHealthStatus();
      setHealthStatus('healthy');
    } catch (error) {
      setHealthStatus('unhealthy');
      console.warn('Health check failed:', error);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Enhanced input validation
    const trimmedQuery = query.trim();
    if (!trimmedQuery) {
      setError('Please enter a search query');
      return;
    }

    if (trimmedQuery.length < 2) {
      setError('Please enter at least 2 characters');
      return;
    }

    if (trimmedQuery.length > 500) {
      setError('Search query is too long. Please keep it under 500 characters.');
      return;
    }

    setLoading(true);
    setError(null);
    setHasSearched(true);

    try {
      const searchRequest: SearchRequest = {
        query: trimmedQuery,
      };

      console.log('🔍 Starting search with query:', trimmedQuery);
      const response = await searchProperties(searchRequest);
      
      // Enhanced response validation
      if (response && response.success) {
        const properties = response.data?.properties || [];
        setProperties(properties);
        
        if (properties.length === 0) {
          setError('No properties found for your search. Try different keywords, be more specific about the location, or check your spelling.');
        } else {
          console.log(`✅ Found ${properties.length} properties`);
        }
      } else {
        const errorMsg = response?.message || 'Search failed. Please try again.';
        setError(errorMsg);
        console.error('❌ Search failed:', errorMsg);
      }
    } catch (error: any) {
      console.error('🚨 Search error:', error);
      
      // Enhanced error handling with specific messages
      let errorMessage = 'An unexpected error occurred. Please try again.';
      
      if (error.message) {
        errorMessage = error.message;
      } else if (error.code === 'NETWORK_ERROR') {
        errorMessage = 'Network connection failed. Please check your internet connection and try again.';
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = 'Search timed out. The service might be busy. Please try again in a moment.';
      }
      
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  const handleFavorite = (propertyId: string) => {
    setFavoritedProperties(prev => {
      const newSet = new Set(prev);
      if (newSet.has(propertyId)) {
        newSet.delete(propertyId);
      } else {
        newSet.add(propertyId);
      }
      return newSet;
    });
  };

  const handleExampleSearch = (exampleQuery: string) => {
    setQuery(exampleQuery);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-airbnb-background to-white">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-airbnb-primary rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">A</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">AI Airbnb Search</h1>
                <p className="text-sm text-gray-500">Find your perfect stay with AI</p>
              </div>
            </div>
            
            {/* Health Status */}
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-xs ${
              healthStatus === 'healthy' 
                ? 'bg-green-100 text-green-800' 
                : healthStatus === 'unhealthy'
                ? 'bg-red-100 text-red-800'
                : 'bg-yellow-100 text-yellow-800'
            }`}>
              <div className={`w-2 h-2 rounded-full ${
                healthStatus === 'healthy' 
                  ? 'bg-green-500' 
                  : healthStatus === 'unhealthy'
                  ? 'bg-red-500'
                  : 'bg-yellow-500'
              }`} />
              <span>
                {healthStatus === 'healthy' ? 'Online' : 
                 healthStatus === 'unhealthy' ? 'Offline' : 'Checking...'}
              </span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="text-center mb-12">
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Find Your Perfect Stay
          </h2>
          <p className="text-lg text-gray-600 mb-8 max-w-2xl mx-auto">
            Use natural language to describe what you're looking for. Our AI will find the best properties for you.
          </p>

          {/* Search Form */}
          <form onSubmit={handleSearch} className="max-w-2xl mx-auto">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="e.g., 'Cozy apartment in Paris for 2 people near the Eiffel Tower'"
                className="w-full pl-12 pr-4 py-4 text-lg border border-gray-300 rounded-2xl focus:ring-2 focus:ring-airbnb-primary focus:border-transparent outline-none transition-all duration-200"
                disabled={loading}
              />
            </div>
            <button
              type="submit"
              disabled={loading || !query.trim()}
              className="mt-4 w-full sm:w-auto px-8 py-4 bg-airbnb-primary text-white font-semibold rounded-2xl hover:bg-red-600 focus:ring-2 focus:ring-airbnb-primary focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin" />
                  <span>Searching...</span>
                </>
              ) : (
                <>
                  <Search className="w-5 h-5" />
                  <span>Search Properties</span>
                </>
              )}
            </button>
          </form>

          {/* Example Searches */}
          {!hasSearched && (
            <div className="mt-8">
              <p className="text-sm text-gray-500 mb-4">Try these example searches:</p>
              <div className="flex flex-wrap justify-center gap-2">
                {[
                  '11 bedroom house in Texas for large group',
                  'Luxury 8 bedroom villa in Napa Valley with pool',
                  'Beach house in Malibu for weekend getaway',
                  'Modern apartment in NYC with city views',
                  'Mansion in the Hamptons for wedding party',
                  'Ski lodge in Aspen for 20 people'
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => handleExampleSearch(example)}
                    className="px-4 py-2 text-sm bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-full transition-colors duration-200"
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Error Message */}
        {error && (
          <div className="max-w-2xl mx-auto mb-8">
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 flex-shrink-0 mt-0.5" />
              <div>
                <h3 className="text-sm font-medium text-red-800">Search Error</h3>
                <p className="text-sm text-red-700 mt-1">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Results Section */}
        {hasSearched && !loading && !error && (
          <div className="mb-8">
            {properties.length > 0 ? (
              <PropertyCarousel
                properties={properties}
                onFavorite={handleFavorite}
                favoritedProperties={favoritedProperties}
              />
            ) : (
              <div className="text-center py-12">
                <div className="text-gray-500 text-lg mb-2">No properties found</div>
                <p className="text-gray-400 text-sm">
                  Try adjusting your search terms or being more specific about the location.
                </p>
              </div>
            )}
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-airbnb-primary mx-auto mb-4" />
            <p className="text-gray-600">Searching for the perfect properties...</p>
            <p className="text-sm text-gray-500 mt-2">This may take a few moments</p>
          </div>
        )}

        {/* Features Section */}
        {!hasSearched && (
          <div className="mt-16 grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-12 h-12 bg-airbnb-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Search className="w-6 h-6 text-airbnb-primary" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">AI-Powered Search</h3>
              <p className="text-gray-600">
                Use natural language to describe exactly what you're looking for
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-airbnb-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <MapPin className="w-6 h-6 text-airbnb-primary" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-Time Data</h3>
              <p className="text-gray-600">
                Get up-to-date availability and pricing information
              </p>
            </div>
            
            <div className="text-center">
              <div className="w-12 h-12 bg-airbnb-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                <Users className="w-6 h-6 text-airbnb-primary" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Perfect Matches</h3>
              <p className="text-gray-600">
                Find properties that match your specific needs and preferences
              </p>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-50 border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500 text-sm">
            <p>© 2025 AI Airbnb Search. All rights reserved.</p>
            <p className="mt-2">Find your perfect stay with intelligent search.</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
