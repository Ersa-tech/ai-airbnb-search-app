import React, { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight } from 'lucide-react';
import PropertyCard from './PropertyCard';
import { Property } from '../services/api';

interface PropertyCarouselProps {
  properties: Property[];
  onFavorite?: (propertyId: string) => void;
  favoritedProperties?: Set<string>;
  className?: string;
}

const PropertyCarousel: React.FC<PropertyCarouselProps> = ({
  properties,
  onFavorite,
  favoritedProperties = new Set(),
  className = ''
}) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [touchStart, setTouchStart] = useState<number | null>(null);
  const [touchEnd, setTouchEnd] = useState<number | null>(null);
  const carouselRef = useRef<HTMLDivElement>(null);

  // Ensure we only show exactly 5 properties as per requirements
  const displayProperties = properties.slice(0, 5);
  const totalProperties = displayProperties.length;

  // Auto-advance carousel every 8 seconds
  useEffect(() => {
    if (totalProperties <= 1) return;

    const interval = setInterval(() => {
      handleNext();
    }, 8000);

    return () => clearInterval(interval);
  }, [currentIndex, totalProperties]);

  const handlePrevious = () => {
    if (isTransitioning || totalProperties <= 1) return;
    
    setIsTransitioning(true);
    setCurrentIndex((prev) => (prev === 0 ? totalProperties - 1 : prev - 1));
    
    setTimeout(() => setIsTransitioning(false), 300);
  };

  const handleNext = () => {
    if (isTransitioning || totalProperties <= 1) return;
    
    setIsTransitioning(true);
    setCurrentIndex((prev) => (prev === totalProperties - 1 ? 0 : prev + 1));
    
    setTimeout(() => setIsTransitioning(false), 300);
  };

  const goToSlide = (index: number) => {
    if (isTransitioning || index === currentIndex) return;
    
    setIsTransitioning(true);
    setCurrentIndex(index);
    
    setTimeout(() => setIsTransitioning(false), 300);
  };

  // Touch handlers for mobile swipe
  const handleTouchStart = (e: React.TouchEvent) => {
    setTouchEnd(null);
    setTouchStart(e.targetTouches[0].clientX);
  };

  const handleTouchMove = (e: React.TouchEvent) => {
    setTouchEnd(e.targetTouches[0].clientX);
  };

  const handleTouchEnd = () => {
    if (!touchStart || !touchEnd) return;
    
    const distance = touchStart - touchEnd;
    const isLeftSwipe = distance > 50;
    const isRightSwipe = distance < -50;

    if (isLeftSwipe) {
      handleNext();
    } else if (isRightSwipe) {
      handlePrevious();
    }
  };

  // Keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowLeft') {
        handlePrevious();
      } else if (e.key === 'ArrowRight') {
        handleNext();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (totalProperties === 0) {
    return (
      <div className={`text-center py-12 ${className}`}>
        <div className="text-gray-500 text-lg">No properties found</div>
        <div className="text-gray-400 text-sm mt-2">Try adjusting your search criteria</div>
      </div>
    );
  }

  return (
    <div className={`relative w-full ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">
            Featured Properties
          </h2>
          <p className="text-gray-600 text-sm mt-1">
            Showing {totalProperties} of {properties.length} results
          </p>
        </div>
        
        {/* Navigation Buttons - Desktop */}
        {totalProperties > 1 && (
          <div className="hidden sm:flex items-center space-x-2">
            <button
              onClick={handlePrevious}
              disabled={isTransitioning}
              className="p-2 rounded-full border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Previous property"
            >
              <ChevronLeft className="w-5 h-5 text-gray-600" />
            </button>
            <button
              onClick={handleNext}
              disabled={isTransitioning}
              className="p-2 rounded-full border border-gray-300 hover:border-gray-400 hover:bg-gray-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Next property"
            >
              <ChevronRight className="w-5 h-5 text-gray-600" />
            </button>
          </div>
        )}
      </div>

      {/* Carousel Container */}
      <div className="relative overflow-hidden rounded-2xl">
        <div
          ref={carouselRef}
          className="flex transition-transform duration-300 ease-in-out"
          style={{
            transform: `translateX(-${currentIndex * 100}%)`,
          }}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          {displayProperties.map((property, index) => (
            <div
              key={property.id}
              className="w-full flex-shrink-0 px-2"
            >
              <PropertyCard
                property={property}
                onFavorite={onFavorite}
                isFavorited={favoritedProperties.has(property.id)}
                className="h-full"
              />
            </div>
          ))}
        </div>

        {/* Mobile Navigation Overlay */}
        {totalProperties > 1 && (
          <>
            <button
              onClick={handlePrevious}
              disabled={isTransitioning}
              className="absolute left-2 top-1/2 transform -translate-y-1/2 sm:hidden p-2 rounded-full bg-white/80 backdrop-blur-sm shadow-lg hover:bg-white transition-colors disabled:opacity-50"
              aria-label="Previous property"
            >
              <ChevronLeft className="w-5 h-5 text-gray-700" />
            </button>
            <button
              onClick={handleNext}
              disabled={isTransitioning}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 sm:hidden p-2 rounded-full bg-white/80 backdrop-blur-sm shadow-lg hover:bg-white transition-colors disabled:opacity-50"
              aria-label="Next property"
            >
              <ChevronRight className="w-5 h-5 text-gray-700" />
            </button>
          </>
        )}
      </div>

      {/* Dots Indicator */}
      {totalProperties > 1 && (
        <div className="flex justify-center mt-6 space-x-2">
          {displayProperties.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`w-2 h-2 rounded-full transition-all duration-200 ${
                index === currentIndex
                  ? 'bg-airbnb-primary w-6'
                  : 'bg-gray-300 hover:bg-gray-400'
              }`}
              aria-label={`Go to property ${index + 1}`}
            />
          ))}
        </div>
      )}

      {/* Property Counter */}
      <div className="text-center mt-4 text-sm text-gray-500">
        {currentIndex + 1} of {totalProperties}
      </div>

      {/* Swipe Hint for Mobile */}
      {totalProperties > 1 && (
        <div className="sm:hidden text-center mt-2 text-xs text-gray-400">
          Swipe left or right to browse properties
        </div>
      )}
    </div>
  );
};

export default PropertyCarousel;
