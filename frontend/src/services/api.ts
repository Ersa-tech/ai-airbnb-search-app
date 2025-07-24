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

// API Functions
export const searchProperties = async (searchRequest: SearchRequest): Promise<SearchResponse> => {
  try {
    const response = await api.post<SearchResponse>('/api/v1/search', searchRequest);
    return response.data;
  } catch (error) {
    console.error('Search properties error:', error);
    throw new Error('Failed to search properties. Please try again.');
  }
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
