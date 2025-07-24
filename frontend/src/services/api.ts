import axios from 'axios';

// Environment configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('❌ API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`✅ API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('❌ API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types
export interface Property {
  id: string;
  title: string;
  description: string;
  price: number;
  currency: string;
  location: {
    address: string;
    city: string;
    country: string;
    coordinates?: {
      lat: number;
      lng: number;
    };
  };
  images: string[];
  amenities: string[];
  rating: number;
  reviewCount: number;
  host: {
    name: string;
    avatar?: string;
    isSuperhost: boolean;
  };
  availability: {
    available: boolean;
    checkIn?: string;
    checkOut?: string;
  };
  propertyType: string;
  guests: number;
  bedrooms: number;
  bathrooms: number;
  url?: string;
}

export interface SearchRequest {
  query: string;
  location?: string;
  checkIn?: string;
  checkOut?: string;
  guests?: number;
  priceMin?: number;
  priceMax?: number;
}

export interface SearchResponse {
  success: boolean;
  data: {
    properties: Property[];
    total: number;
    query: string;
    processingTime: number;
  };
  message?: string;
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  services: {
    openrouter: string;
    mcp_server: string;
  };
}

// Enhanced error message utility
const getErrorMessage = (error: any): string => {
  if (error?.response?.data?.message) {
    return error.response.data.message;
  }
  if (error?.response?.data?.error) {
    return error.response.data.error;
  }
  if (error?.message) {
    return error.message;
  }
  if (error?.response?.status === 404) {
    return 'Service not found. Please check your connection.';
  }
  if (error?.response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  if (error?.response?.status === 503) {
    return 'Service temporarily unavailable. Please try again.';
  }
  if (error?.code === 'NETWORK_ERROR') {
    return 'Network error. Please check your internet connection.';
  }
  if (error?.code === 'ECONNABORTED') {
    return 'Request timeout. Please try again.';
  }
  return 'An unexpected error occurred. Please try again.';
};

// API Functions with enhanced error handling
export const searchProperties = async (searchRequest: SearchRequest): Promise<SearchResponse> => {
  const maxRetries = 3;
  let lastError: Error = new Error('Unknown error');

  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      console.log(`🔍 Search attempt ${attempt}/${maxRetries}:`, searchRequest);
      
      const response = await api.post<SearchResponse>('/api/v1/search', searchRequest);
      
      // Validate response structure
      if (!response.data || typeof response.data !== 'object') {
        throw new Error('Invalid response format from server');
      }
      
      // Ensure properties array exists
      if (!response.data.data?.properties) {
        response.data.data = {
          ...response.data.data,
          properties: [],
          total: 0,
          query: searchRequest.query,
          processingTime: 0
        };
      }
      
      console.log(`✅ Search successful on attempt ${attempt}`);
      return response.data;
      
    } catch (error: any) {
      lastError = error;
      console.error(`❌ Search attempt ${attempt} failed:`, error);
      
      // Don't retry on client errors (4xx)
      if (error.response?.status >= 400 && error.response?.status < 500) {
        break;
      }
      
      // Wait before retrying (exponential backoff)
      if (attempt < maxRetries) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
        console.log(`⏳ Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }
  
  // All retries failed
  const errorMessage = getErrorMessage(lastError);
  console.error('🚨 All search attempts failed:', errorMessage);
  throw new Error(errorMessage);
};

export const getHealthStatus = async (): Promise<HealthResponse> => {
  try {
    const response = await api.get<HealthResponse>('/health');
    return response.data;
  } catch (error) {
    console.error('Health check error:', error);
    throw new Error('Failed to check service health.');
  }
};

// Utility function to format price
export const formatPrice = (price: number, currency: string = 'USD'): string => {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
};

// Utility function to format rating
export const formatRating = (rating: number): string => {
  return rating.toFixed(1);
};

// Utility function to get property image with fallback
export const getPropertyImage = (property: Property, index: number = 0): string => {
  const fallbackImage = 'https://via.placeholder.com/400x300/f0f0f0/666666?text=No+Image';
  
  if (!property.images || property.images.length === 0) {
    return fallbackImage;
  }
  
  const imageUrl = property.images[index] || property.images[0];
  return imageUrl || fallbackImage;
};

// Utility function to truncate text
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
};

export default api;
