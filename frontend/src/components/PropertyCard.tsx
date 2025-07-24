import React, { useState } from 'react';
import { Star, Heart, Users, Bed, Bath, MapPin, Wifi, Car, Coffee } from 'lucide-react';
import { Property, formatPrice, formatRating, getPropertyImage, truncateText } from '../services/api';

interface PropertyCardProps {
  property: Property;
  onFavorite?: (propertyId: string) => void;
  isFavorited?: boolean;
  className?: string;
}

const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  onFavorite,
  isFavorited = false,
  className = ''
}) => {
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);

  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (onFavorite) {
      onFavorite(property.id);
    }
  };

  const handleCardClick = () => {
    if (property.url) {
      window.open(property.url, '_blank', 'noopener,noreferrer');
    }
  };

  const getAmenityIcon = (amenity: string) => {
    const amenityLower = amenity.toLowerCase();
    if (amenityLower.includes('wifi') || amenityLower.includes('internet')) {
      return <Wifi className="w-4 h-4" />;
    }
    if (amenityLower.includes('parking') || amenityLower.includes('garage')) {
      return <Car className="w-4 h-4" />;
    }
    if (amenityLower.includes('kitchen') || amenityLower.includes('coffee')) {
      return <Coffee className="w-4 h-4" />;
    }
    return null;
  };

  return (
    <div
      className={`bg-white rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer overflow-hidden ${className}`}
      onClick={handleCardClick}
    >
      {/* Image Container */}
      <div className="relative h-48 sm:h-56 overflow-hidden">
        {!imageLoaded && !imageError && (
          <div className="absolute inset-0 bg-gray-200 animate-pulse flex items-center justify-center">
            <div className="text-gray-400 text-sm">Loading...</div>
          </div>
        )}
        
        <img
          src={getPropertyImage(property)}
          alt={property.title}
          className={`w-full h-full object-cover transition-opacity duration-300 ${
            imageLoaded ? 'opacity-100' : 'opacity-0'
          }`}
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            setImageError(true);
            setImageLoaded(true);
          }}
        />

        {/* Favorite Button */}
        <button
          onClick={handleFavoriteClick}
          className={`absolute top-3 right-3 p-2 rounded-full transition-all duration-200 ${
            isFavorited
              ? 'bg-airbnb-primary text-white'
              : 'bg-white/80 text-gray-600 hover:bg-white hover:text-airbnb-primary'
          }`}
          aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
        >
          <Heart
            className={`w-4 h-4 ${isFavorited ? 'fill-current' : ''}`}
          />
        </button>

        {/* Superhost Badge */}
        {property.host.isSuperhost && (
          <div className="absolute top-3 left-3 bg-white/90 text-xs font-semibold text-gray-800 px-2 py-1 rounded-full">
            Superhost
          </div>
        )}

        {/* Availability Badge */}
        <div className={`absolute bottom-3 left-3 px-2 py-1 rounded-full text-xs font-medium ${
          property.availability.available
            ? 'bg-green-500 text-white'
            : 'bg-red-500 text-white'
        }`}>
          {property.availability.available ? 'Available' : 'Unavailable'}
        </div>
      </div>

      {/* Content */}
      <div className="p-4 space-y-3">
        {/* Location and Rating */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center text-gray-600 text-sm mb-1">
              <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
              <span className="truncate">
                {property.location.city}, {property.location.country}
              </span>
            </div>
            <h3 className="font-semibold text-gray-900 text-base leading-tight">
              {truncateText(property.title, 60)}
            </h3>
          </div>
          
          {property.rating > 0 && (
            <div className="flex items-center ml-2 flex-shrink-0">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="text-sm font-medium text-gray-900 ml-1">
                {formatRating(property.rating)}
              </span>
              {property.reviewCount > 0 && (
                <span className="text-xs text-gray-500 ml-1">
                  ({property.reviewCount})
                </span>
              )}
            </div>
          )}
        </div>

        {/* Property Details */}
        <div className="flex items-center text-gray-600 text-sm space-x-4">
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1" />
            <span>{property.guests} guests</span>
          </div>
          <div className="flex items-center">
            <Bed className="w-4 h-4 mr-1" />
            <span>{property.bedrooms} bed{property.bedrooms !== 1 ? 's' : ''}</span>
          </div>
          <div className="flex items-center">
            <Bath className="w-4 h-4 mr-1" />
            <span>{property.bathrooms} bath{property.bathrooms !== 1 ? 's' : ''}</span>
          </div>
        </div>

        {/* Property Type */}
        <div className="text-sm text-gray-600">
          {property.propertyType}
        </div>

        {/* Amenities Preview */}
        {property.amenities && property.amenities.length > 0 && (
          <div className="flex items-center space-x-2">
            {property.amenities.slice(0, 3).map((amenity, index) => {
              const icon = getAmenityIcon(amenity);
              return icon ? (
                <div
                  key={index}
                  className="flex items-center text-gray-500"
                  title={amenity}
                >
                  {icon}
                </div>
              ) : null;
            })}
            {property.amenities.length > 3 && (
              <span className="text-xs text-gray-500">
                +{property.amenities.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Price */}
        <div className="flex items-center justify-between pt-2 border-t border-gray-100">
          <div>
            <span className="text-lg font-bold text-gray-900">
              {formatPrice(property.price, property.currency)}
            </span>
            <span className="text-gray-600 text-sm ml-1">/ night</span>
          </div>
          
          {/* Host Info */}
          <div className="flex items-center text-xs text-gray-500">
            <span>Host: {property.host.name}</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;
