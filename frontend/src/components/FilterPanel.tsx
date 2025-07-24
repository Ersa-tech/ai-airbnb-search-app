import React, { useState } from 'react';
import { X, Sliders, Wifi, Tv, WashingMachine, Home, Check } from 'lucide-react';

export interface FilterState {
  amenities: Set<string>;
  propertyTypes: Set<string>;
  isExpanded: boolean;
}

interface FilterPanelProps {
  filters: FilterState;
  onFiltersChange: (filters: FilterState) => void;
  onClose: () => void;
  isVisible: boolean;
}

const FilterPanel: React.FC<FilterPanelProps> = ({
  filters,
  onFiltersChange,
  onClose,
  isVisible
}) => {
  const [localFilters, setLocalFilters] = useState<FilterState>(filters);

  const amenityOptions = [
    { id: 'wifi', label: 'WiFi', icon: Wifi },
    { id: 'tv', label: 'TV', icon: Tv },
    { id: 'washer', label: 'Washer', icon: WashingMachine },
  ];

  const propertyTypeOptions = [
    { id: 'entire_house', label: 'Entire House', icon: Home },
  ];

  const toggleAmenity = (amenityId: string) => {
    const newAmenities = new Set(localFilters.amenities);
    if (newAmenities.has(amenityId)) {
      newAmenities.delete(amenityId);
    } else {
      newAmenities.add(amenityId);
    }
    setLocalFilters({
      ...localFilters,
      amenities: newAmenities
    });
  };

  const togglePropertyType = (typeId: string) => {
    const newPropertyTypes = new Set(localFilters.propertyTypes);
    if (newPropertyTypes.has(typeId)) {
      newPropertyTypes.delete(typeId);
    } else {
      newPropertyTypes.add(typeId);
    }
    setLocalFilters({
      ...localFilters,
      propertyTypes: newPropertyTypes
    });
  };

  const applyFilters = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  const clearAllFilters = () => {
    const clearedFilters = {
      amenities: new Set<string>(),
      propertyTypes: new Set<string>(),
      isExpanded: false
    };
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
  };

  const getTotalActiveFilters = () => {
    return localFilters.amenities.size + localFilters.propertyTypes.size;
  };

  if (!isVisible) return null;

  return (
    <>
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black/50 backdrop-blur-sm z-40 transition-opacity duration-300"
        onClick={onClose}
      />
      
      {/* Filter Panel */}
      <div className="fixed bottom-0 left-0 right-0 bg-white rounded-t-3xl shadow-2xl z-50 transform transition-transform duration-300 ease-out">
        {/* Handle */}
        <div className="flex justify-center pt-3 pb-2">
          <div className="w-12 h-1 bg-gray-300 rounded-full" />
        </div>

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
          <div className="flex items-center space-x-3">
            <Sliders className="w-6 h-6 text-gray-700" />
            <h2 className="text-xl font-semibold text-gray-900">Filters</h2>
            {getTotalActiveFilters() > 0 && (
              <div className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full min-w-[20px] text-center">
                {getTotalActiveFilters()}
              </div>
            )}
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-full transition-colors"
            aria-label="Close filters"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Filter Content */}
        <div className="px-6 py-6 max-h-[60vh] overflow-y-auto">
          {/* Property Type Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Home className="w-5 h-5 mr-2 text-gray-600" />
              Property Type
            </h3>
            <div className="space-y-3">
              {propertyTypeOptions.map((option) => {
                const IconComponent = option.icon;
                const isSelected = localFilters.propertyTypes.has(option.id);
                
                return (
                  <button
                    key={option.id}
                    onClick={() => togglePropertyType(option.id)}
                    className={`w-full flex items-center justify-between p-4 rounded-xl border-2 transition-all duration-200 ${
                      isSelected
                        ? 'border-red-500 bg-red-50 text-red-700'
                        : 'border-gray-200 hover:border-gray-300 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <IconComponent className={`w-5 h-5 ${isSelected ? 'text-red-600' : 'text-gray-500'}`} />
                      <span className="font-medium">{option.label}</span>
                    </div>
                    {isSelected && (
                      <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Amenities Section */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Sliders className="w-5 h-5 mr-2 text-gray-600" />
              Amenities
            </h3>
            <div className="grid grid-cols-1 gap-3">
              {amenityOptions.map((option) => {
                const IconComponent = option.icon;
                const isSelected = localFilters.amenities.has(option.id);
                
                return (
                  <button
                    key={option.id}
                    onClick={() => toggleAmenity(option.id)}
                    className={`flex items-center justify-between p-4 rounded-xl border-2 transition-all duration-200 ${
                      isSelected
                        ? 'border-blue-500 bg-blue-50 text-blue-700'
                        : 'border-gray-200 hover:border-gray-300 text-gray-700'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <IconComponent className={`w-5 h-5 ${isSelected ? 'text-blue-600' : 'text-gray-500'}`} />
                      <span className="font-medium">{option.label}</span>
                    </div>
                    {isSelected && (
                      <div className="w-6 h-6 bg-blue-500 rounded-full flex items-center justify-center">
                        <Check className="w-4 h-4 text-white" />
                      </div>
                    )}
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Footer Actions */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 rounded-t-3xl">
          <div className="flex space-x-3">
            <button
              onClick={clearAllFilters}
              className="flex-1 py-3 px-4 border border-gray-300 text-gray-700 font-medium rounded-xl hover:bg-gray-100 transition-colors"
            >
              Clear All
            </button>
            <button
              onClick={applyFilters}
              className="flex-1 py-3 px-4 bg-red-500 text-white font-medium rounded-xl hover:bg-red-600 transition-colors"
            >
              Apply Filters
              {getTotalActiveFilters() > 0 && (
                <span className="ml-2 bg-red-600 text-white text-xs px-2 py-1 rounded-full">
                  {getTotalActiveFilters()}
                </span>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default FilterPanel;
