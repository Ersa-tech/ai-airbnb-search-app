import React from 'react';
import { Sliders } from 'lucide-react';

interface FilterButtonProps {
  onClick: () => void;
  activeFilterCount: number;
}

const FilterButton: React.FC<FilterButtonProps> = ({ onClick, activeFilterCount }) => {
  return (
    <button
      onClick={onClick}
      className="fixed bottom-6 right-6 bg-white shadow-lg border border-gray-200 rounded-full p-4 hover:shadow-xl transition-all duration-200 z-30 flex items-center space-x-2"
      aria-label="Open filters"
    >
      <Sliders className="w-5 h-5 text-gray-700" />
      {activeFilterCount > 0 && (
        <>
          <span className="text-sm font-medium text-gray-700">Filters</span>
          <div className="bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full min-w-[20px] text-center">
            {activeFilterCount}
          </div>
        </>
      )}
      {activeFilterCount === 0 && (
        <span className="text-sm font-medium text-gray-700 hidden sm:block">Filters</span>
      )}
    </button>
  );
};

export default FilterButton;
