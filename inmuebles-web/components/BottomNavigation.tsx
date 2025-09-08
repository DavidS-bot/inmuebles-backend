"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Building2, 
  TrendingUp, 
  BarChart3, 
  MoreHorizontal 
} from 'lucide-react';

interface NavTab {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  badge?: number;
}

// Dynamic badge data hook
function useBadgeData() {
  // This would normally come from API or context
  // For now, simulating dynamic badges
  return {
    dashboard: 0,
    properties: 0,
    movements: 3, // Unclassified movements
    analytics: 1, // New insights available
    more: 0
  };
}

function getNavigationTabs(badgeData: Record<string, number>): NavTab[] {
  return [
    {
      id: 'dashboard',
      label: 'Dashboard',
      href: '/financial-agent',
      icon: Home,
      badge: badgeData.dashboard
    },
    {
      id: 'properties',
      label: 'Propiedades',
      href: '/dashboard/properties',
      icon: Building2,
      badge: badgeData.properties
    },
    {
      id: 'movements',
      label: 'Movimientos',
      href: '/financial-agent/movements',
      icon: TrendingUp,
      badge: badgeData.movements
    },
    {
      id: 'analytics',
      label: 'Analytics',
      href: '/financial-agent/analytics',
      icon: BarChart3,
      badge: badgeData.analytics
    },
    {
      id: 'more',
      label: 'Más',
      href: '/dashboard',
      icon: MoreHorizontal,
      badge: badgeData.more
    }
  ];
}

export default function BottomNavigation() {
  const pathname = usePathname();
  const badgeData = useBadgeData();
  const navigationTabs = getNavigationTabs(badgeData);

  const getActiveTab = () => {
    if (pathname.includes('/financial-agent')) {
      if (pathname.includes('/analytics')) return 'analytics';
      if (pathname.includes('/movements')) return 'movements';
      return 'dashboard';
    } else if (pathname.includes('/properties')) {
      return 'properties';
    } else if (pathname.includes('/dashboard')) {
      return 'more';
    }
    return 'dashboard';
  };

  const activeTab = getActiveTab();

  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 md:hidden">
      <div className="flex justify-around items-center h-16 px-2">
        {navigationTabs.map((tab) => {
          const Icon = tab.icon;
          const isActive = activeTab === tab.id;
          
          return (
            <Link
              key={tab.id}
              href={tab.href}
              className={`flex flex-col items-center justify-center min-w-0 flex-1 px-1 py-2 text-xs font-medium transition-all duration-300 ease-out transform ${
                isActive
                  ? 'text-blue-600 scale-110 -translate-y-0.5 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700 hover:scale-105 active:scale-95'
              }`}
            >
              <div className="relative mb-1">
                <Icon 
                  size={20} 
                  className={`transition-all duration-300 ease-out ${
                    isActive 
                      ? 'text-blue-600 stroke-2 drop-shadow-sm' 
                      : 'text-gray-500 group-hover:text-gray-600'
                  }`} 
                />
                {tab.badge && tab.badge > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold animate-pulse shadow-lg">
                    {tab.badge > 9 ? '9+' : tab.badge}
                  </span>
                )}
              </div>
              <span className={`truncate max-w-full transition-all duration-300 ease-out ${
                isActive ? 'text-blue-600 font-semibold transform scale-105' : 'text-gray-500 hover:text-gray-600'
              }`}>
                {tab.label}
              </span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
}