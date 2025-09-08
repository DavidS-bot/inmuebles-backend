import { useState, ReactNode } from 'react';
import { ChevronDownIcon, ChevronUpIcon } from '@heroicons/react/24/outline';

interface CollapsibleSectionProps {
  title: string;
  icon?: string;
  children: ReactNode;
  defaultOpen?: boolean;
  className?: string;
}

export function CollapsibleSection({ 
  title, 
  icon, 
  children, 
  defaultOpen = false,
  className = ""
}: CollapsibleSectionProps) {
  const [isOpen, setIsOpen] = useState(defaultOpen);

  return (
    <div className={`bg-white rounded-3xl shadow-sm p-8 ${className}`}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center justify-between w-full text-left mb-4 group"
      >
        <h2 className="text-2xl font-bold text-gray-900 group-hover:text-blue-600 transition-colors">
          {icon && <span className="mr-2">{icon}</span>}
          {title}
        </h2>
        {isOpen ? (
          <ChevronUpIcon className="w-6 h-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
        ) : (
          <ChevronDownIcon className="w-6 h-6 text-gray-400 group-hover:text-blue-600 transition-colors" />
        )}
      </button>

      <div className={`transition-all duration-300 ease-in-out overflow-hidden ${
        isOpen ? 'max-h-[2000px] opacity-100' : 'max-h-0 opacity-0'
      }`}>
        <div className="mt-6">
          {children}
        </div>
      </div>
    </div>
  );
}