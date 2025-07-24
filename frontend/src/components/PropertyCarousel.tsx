import React, { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight, Play, Pause } from 'lucide-react';
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
  const [isAutoPlaying, setIsAutoPlaying] = useState(true);
  const [isHovered, setIsHovered] = useState(false);
  const carouselRef = useRef<HTMLDivElement>(null);
  const autoPlayRef = useRef<NodeJS.Timeout | null>(null);

  // Ensure we only show exactly 5 properties as per requirements
  const displayProperties = properties.slice(0, 5);
  const totalProperties = displayProperties.length;

  // Enhanced auto-advance with pause on hover
  useEffect(() => {
    if (totalProperties <= 1 || !isAutoPlaying || isHovered) {
      if (autoPlayRef.current) {
        clearInterval(autoPlayRef.current);
      }
      return;
    }

    autoPlayRef.current = setInterval(() => {
      handleNext();
    }, 6000); // Reduced to 6 seconds for better UX

    return () => {
      if (autoPlayRef.current) {
        clearInterval(autoPlayRef.current);
      }
    };
  }, [currentIndex, totalProperties, isAutoPlaying, isHovered]);

  const handlePrevious = () => {
    if (isTransitioning || totalProperties <= 1) return;
    
    setIsTransitioning(true);
    setCurrentIndex((prev) => (prev === 0 ? totalProperties - 1 : prev - 1));
    
    setTimeout(() => setIsTransitioning(false), 400);
  };

  const handleNext = () => {
    if (isTransitioning || totalProperties <= 1) return;
    
    setIsTransitioning(true);
    setCurrentIndex((prev) => (prev === totalProperties - 1 ? 0 : prev + 1));
    
    setTimeout(() => setIsTransitioning(false), 400);
  };

  const goToSlide = (index: number) => {
    if (isTransitioning || index === currentIndex) return;
    
    setIsTransitioning(true);
    setCurrentIndex(index);
    
    setTimeout(() => setIsTransitioning(false), 400);
  };

  const toggleAutoPlay = () => {
    setIsAutoPlaying(!isAutoPlaying);
  };

  // Enhanced touch handlers with better sensitivity
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
    const isLeftSwipe = distance > 30; // Reduced threshold for better sensitivity
    const isRightSwipe = distance < -30;

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
        e.preventDefault();
        handlePrevious();
      } else if (e.key === 'ArrowRight') {
        e.preventDefault();
        handleNext();
      } else if (e.key === ' ') {
        e.preventDefault();
        toggleAutoPlay();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  if (totalProperties === 0) {
    return (
      <div className={`text-center py-16 ${className}`}>
        <div className="max-w-md mx-auto">
          <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <ChevronRight className="w-8 h-8 text-gray-400" />
          </div>
          <div className="text-gray-600 text-xl font-semibold mb-2">No properties found</div>
          <div className="text-gray-500 text-sm">Try adjusting your search criteria or explore different locations</div>
        </div>
      </div>
    );
  }

  return (
    <div 
      className={`relative w-full ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Enhanced Header with Auto-play Control */}
      <div className="flex items-center justify-between mb-8">
        <div className="flex-1">
          <h2 className="text-3xl font-bold text-gray-900 mb-2">
            Featured Properties
          </h2>
          <div className="flex items-center space-x-4 text-sm text-gray-600">
            <span className="font-medium">
              Showing {totalProperties} of {properties.length} results
            </span>
            {totalProperties > 1 && (
              <div className="flex items-center space-x-2">
                <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
                <span className="text-xs">
                  {isAutoPlaying ? 'Auto-playing' : 'Paused'}
                </span>
              </div>
            )}
          </div>
        </div>
        
        {/* Enhanced Navigation Controls */}
        {totalProperties > 1 && (
          <div className="flex items-center space-x-3">
            {/* Auto-play Toggle */}
            <button
              onClick={toggleAutoPlay}
              className="p-2 rounded-full bg-gray-100 hover:bg-gray-200 transition-colors duration-200"
              aria-label={isAutoPlaying ? 'Pause auto-play' : 'Start auto-play'}
              title={isAutoPlaying ? 'Pause auto-play' : 'Start auto-play'}
            >
              {isAutoPlaying ? (
                <Pause className="w-4 h-4 text-gray-600" />
              ) : (
                <Play className="w-4 h-4 text-gray-600" />
              )}
            </button>

            {/* Navigation Buttons */}
            <div className="hidden sm:flex items-center space-x-2">
              <button
                onClick={handlePrevious}
                disabled={isTransitioning}
                className="p-3 rounded-full border-2 border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
                aria-label="Previous property"
              >
                <ChevronLeft className="w-5 h-5 text-gray-600 group-hover:text-gray-800 transition-colors" />
              </button>
              <button
                onClick={handleNext}
                disabled={isTransitioning}
                className="p-3 rounded-full border-2 border-gray-200 hover:border-gray-300 hover:bg-gray-50 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed group"
                aria-label="Next property"
              >
                <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-gray-800 transition-colors" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Enhanced Carousel Container */}
      <div className="relative overflow-hidden rounded-3xl">
        <div
          ref={carouselRef}
          className="flex transition-transform duration-500 ease-out"
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
              className="w-full flex-shrink-0 px-3"
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

        {/* Enhanced Mobile Navigation Overlay */}
        {totalProperties > 1 && (
          <>
            <button
              onClick={handlePrevious}
              disabled={isTransitioning}
              className="absolute left-3 top-1/2 transform -translate-y-1/2 sm:hidden p-3 rounded-full bg-white/95 backdrop-blur-sm shadow-xl hover:bg-white transition-all duration-200 disabled:opacity-50 border border-white/20"
              aria-label="Previous property"
            >
              <ChevronLeft className="w-5 h-5 text-gray-700" />
            </button>
            <button
              onClick={handleNext}
              disabled={isTransitioning}
              className="absolute right-3 top-1/2 transform -translate-y-1/2 sm:hidden p-3 rounded-full bg-white/95 backdrop-blur-sm shadow-xl hover:bg-white transition-all duration-200 disabled:opacity-50 border border-white/20"
              aria-label="Next property"
            >
              <ChevronRight className="w-5 h-5 text-gray-700" />
            </button>
          </>
        )}
      </div>

      {/* Enhanced Progress Indicators */}
      {totalProperties > 1 && (
        <div className="flex justify-center mt-8 space-x-3">
          {displayProperties.map((_, index) => (
            <button
              key={index}
              onClick={() => goToSlide(index)}
              className={`relative transition-all duration-300 ${
                index === currentIndex
                  ? 'w-8 h-3'
                  : 'w-3 h-3 hover:w-4'
              }`}
              aria-label={`Go to property ${index + 1}`}
            >
              <div className={`w-full h-full rounded-full transition-all duration-300 ${
                index === currentIndex
                  ? 'bg-blue-500 shadow-lg shadow-blue-500/30'
                  : 'bg-gray-300 hover:bg-gray-400'
              }`} />
              
              {/* Auto-play Progress Bar */}
              {index === currentIndex && isAutoPlaying && !isHovered && (
                <div className="absolute inset-0 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-300 rounded-full animate-progress"
                    style={{ animationDuration: '6s' }}
                  />
                </div>
              )}
            </button>
          ))}
        </div>
      )}

      {/* Enhanced Property Counter and Controls */}
      <div className="flex items-center justify-between mt-6">
        <div className="text-center flex-1">
          <div className="text-lg font-semibold text-gray-900">
            {currentIndex + 1} of {totalProperties}
          </div>
          <div className="text-sm text-gray-500 mt-1">
            {displayProperties[currentIndex]?.location.city}, {displayProperties[currentIndex]?.location.country}
          </div>
        </div>
      </div>

      {/* Enhanced Mobile Instructions */}
      {totalProperties > 1 && (
        <div className="sm:hidden text-center mt-4">
          <div className="inline-flex items-center space-x-2 text-xs text-gray-500 bg-gray-50 px-4 py-2 rounded-full">
            <div className="flex space-x-1">
              <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
              <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
              <div className="w-1 h-1 bg-gray-400 rounded-full"></div>
            </div>
            <span>Swipe to browse properties</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default PropertyCarousel;
