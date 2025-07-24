import React, { useState } from 'react';
import { Star, Heart, Users, Bed, Bath, MapPin, Wifi, Car, Coffee, Shield, Award } from 'lucide-react';
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
  const [isHovered, setIsHovered] = useState(false);

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
      className={`group relative bg-white rounded-3xl shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 cursor-pointer overflow-hidden border border-gray-100 ${className}`}
      onClick={handleCardClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Image Container with Enhanced Overlay */}
      <div className="relative h-56 sm:h-64 overflow-hidden rounded-t-3xl">
        {/* Loading Skeleton */}
        {!imageLoaded && !imageError && (
          <div className="absolute inset-0 bg-gradient-to-r from-gray-200 via-gray-300 to-gray-200 animate-pulse">
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white to-transparent animate-shimmer"></div>
          </div>
        )}
        
        {/* Main Image */}
        <img
          src={getPropertyImage(property)}
          alt={property.title}
          className={`w-full h-full object-cover transition-all duration-700 ${
            imageLoaded ? 'opacity-100 scale-100' : 'opacity-0 scale-105'
          } ${isHovered ? 'scale-110' : 'scale-100'}`}
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            setImageError(true);
            setImageLoaded(true);
          }}
        />

        {/* Gradient Overlay */}
        <div className="absolute inset-0 bg-gradient-to-t from-black/30 via-transparent to-black/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />

        {/* Top Row: Superhost & Favorite */}
        <div className="absolute top-4 left-4 right-4 flex items-center justify-between">
          {/* Superhost Badge */}
          {property.host.isSuperhost && (
            <div className="flex items-center bg-white/95 backdrop-blur-sm text-xs font-bold text-gray-800 px-3 py-1.5 rounded-full shadow-lg border border-white/20">
              <Award className="w-3 h-3 mr-1 text-yellow-500" />
              Superhost
            </div>
          )}

          {/* Favorite Button */}
          <button
            onClick={handleFavoriteClick}
            className={`p-2.5 rounded-full backdrop-blur-sm transition-all duration-300 transform hover:scale-110 active:scale-95 ${
              isFavorited
                ? 'bg-red-500 text-white shadow-lg shadow-red-500/25'
                : 'bg-white/90 text-gray-600 hover:bg-white hover:text-red-500 shadow-lg'
            }`}
            aria-label={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
          >
            <Heart
              className={`w-4 h-4 transition-all duration-200 ${
                isFavorited ? 'fill-current scale-110' : 'hover:scale-110'
              }`}
            />
          </button>
        </div>

        {/* Bottom Row: Availability */}
        <div className="absolute bottom-4 left-4">
          <div className={`flex items-center px-3 py-1.5 rounded-full text-xs font-semibold backdrop-blur-sm shadow-lg ${
            property.availability.available
              ? 'bg-green-500/90 text-white'
              : 'bg-red-500/90 text-white'
          }`}>
            <div className={`w-2 h-2 rounded-full mr-2 ${
              property.availability.available ? 'bg-green-200' : 'bg-red-200'
            }`} />
            {property.availability.available ? 'Available' : 'Unavailable'}
          </div>
        </div>

        {/* Hover Overlay with Quick Info */}
        <div className={`absolute inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center transition-all duration-300 ${
          isHovered ? 'opacity-100' : 'opacity-0 pointer-events-none'
        }`}>
          <div className="text-white text-center">
            <div className="text-sm font-medium mb-1">Click to view details</div>
            <div className="text-xs opacity-80">Opens in new tab</div>
          </div>
        </div>
      </div>

      {/* Enhanced Content Section */}
      <div className="p-5 space-y-4">
        {/* Location and Rating */}
        <div className="flex items-start justify-between">
          <div className="flex-1 min-w-0">
            <div className="flex items-center text-gray-500 text-sm mb-2">
              <MapPin className="w-4 h-4 mr-1.5 flex-shrink-0" />
              <span className="truncate font-medium">
                {property.location.city}, {property.location.country}
              </span>
            </div>
            <h3 className="font-bold text-gray-900 text-lg leading-tight mb-1">
              {truncateText(property.title, 50)}
            </h3>
            <p className="text-sm text-gray-600 font-medium">
              {property.propertyType}
            </p>
          </div>
          
          {property.rating > 0 && (
            <div className="flex items-center ml-3 flex-shrink-0 bg-gray-50 px-2 py-1 rounded-lg">
              <Star className="w-4 h-4 text-yellow-400 fill-current" />
              <span className="text-sm font-bold text-gray-900 ml-1">
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

        {/* Property Details with Enhanced Icons */}
        <div className="flex items-center justify-between text-gray-600 text-sm bg-gray-50 rounded-xl p-3">
          <div className="flex items-center">
            <Users className="w-4 h-4 mr-1.5 text-blue-500" />
            <span className="font-medium">{property.guests} guests</span>
          </div>
          <div className="flex items-center">
            <Bed className="w-4 h-4 mr-1.5 text-purple-500" />
            <span className="font-medium">{property.bedrooms} bed{property.bedrooms !== 1 ? 's' : ''}</span>
          </div>
          <div className="flex items-center">
            <Bath className="w-4 h-4 mr-1.5 text-teal-500" />
            <span className="font-medium">{property.bathrooms} bath{property.bathrooms !== 1 ? 's' : ''}</span>
          </div>
        </div>

        {/* Enhanced Amenities Preview */}
        {property.amenities && property.amenities.length > 0 && (
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              {property.amenities.slice(0, 3).map((amenity, index) => {
                const icon = getAmenityIcon(amenity);
                return icon ? (
                  <div
                    key={index}
                    className="flex items-center text-gray-500 bg-gray-100 rounded-lg px-2 py-1"
                    title={amenity}
                  >
                    {icon}
                  </div>
                ) : null;
              })}
            </div>
            {property.amenities.length > 3 && (
              <span className="text-xs text-gray-500 font-medium bg-gray-100 px-2 py-1 rounded-full">
                +{property.amenities.length - 3} more
              </span>
            )}
          </div>
        )}

        {/* Enhanced Price and Host Section */}
        <div className="flex items-center justify-between pt-3 border-t border-gray-100">
          <div className="flex flex-col">
            <div className="flex items-baseline">
              <span className="text-2xl font-bold text-gray-900">
                {formatPrice(property.price, property.currency)}
              </span>
              <span className="text-gray-500 text-sm ml-1 font-medium">/ night</span>
            </div>
          </div>
          
          {/* Enhanced Host Info */}
          <div className="flex items-center text-xs text-gray-500 bg-gray-50 rounded-lg px-3 py-2">
            <Shield className="w-3 h-3 mr-1.5" />
            <span className="font-medium">Host: {property.host.name}</span>
          </div>
        </div>
      </div>

      {/* Subtle Border Glow on Hover */}
      <div className={`absolute inset-0 rounded-3xl border-2 transition-all duration-300 pointer-events-none ${
        isHovered ? 'border-blue-200 shadow-lg shadow-blue-100' : 'border-transparent'
      }`} />
    </div>
  );
};

export default PropertyCard;
