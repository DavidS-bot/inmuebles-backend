"use client";
import React, { createContext, useContext, useState, useEffect } from 'react';
import { usePathname } from 'next/navigation';

export interface NavTab {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  badge?: number;
  isActive: boolean;
}

interface NavigationContextType {
  activeTab: string;
  tabs: NavTab[];
  setActiveTab: (tabId: string) => void;
  setBadge: (tabId: string, count: number) => void;
  isMobile: boolean;
  showBottomNav: boolean;
}

const NavigationContext = createContext<NavigationContextType | undefined>(undefined);

export function useNavigation() {
  const context = useContext(NavigationContext);
  if (!context) {
    throw new Error('useNavigation must be used within a NavigationProvider');
  }
  return context;
}

interface NavigationProviderProps {
  children: React.ReactNode;
}

export function NavigationProvider({ children }: NavigationProviderProps) {
  const pathname = usePathname();
  const [activeTab, setActiveTab] = useState('dashboard');
  const [isMobile, setIsMobile] = useState(false);
  const [tabs, setTabs] = useState<NavTab[]>([]);

  useEffect(() => {
    const checkMobile = () => {
      setIsMobile(window.innerWidth < 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  useEffect(() => {
    if (pathname.includes('/financial-agent')) {
      setActiveTab('dashboard');
    } else if (pathname.includes('/properties')) {
      setActiveTab('properties');
    } else if (pathname.includes('/movements') || pathname.includes('/financial')) {
      setActiveTab('movements');
    } else if (pathname.includes('/analytics')) {
      setActiveTab('analytics');
    } else if (pathname.includes('/settings') || pathname.includes('/profile')) {
      setActiveTab('more');
    } else {
      setActiveTab('dashboard');
    }
  }, [pathname]);

  const setBadge = (tabId: string, count: number) => {
    setTabs(prev => prev.map(tab => 
      tab.id === tabId ? { ...tab, badge: count } : tab
    ));
  };

  const showBottomNav = !pathname.includes('/login') && !pathname.includes('/register');

  const contextValue: NavigationContextType = {
    activeTab,
    tabs,
    setActiveTab,
    setBadge,
    isMobile,
    showBottomNav
  };

  return (
    <NavigationContext.Provider value={contextValue}>
      {children}
    </NavigationContext.Provider>
  );
}