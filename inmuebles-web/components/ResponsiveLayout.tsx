"use client";
import { NavigationProvider } from '@/contexts/NavigationContext';
import Sidebar from './Sidebar';
import BottomNavigation from './BottomNavigation';
import Breadcrumbs from './Breadcrumbs';

interface ResponsiveLayoutProps {
  children: React.ReactNode;
  showBreadcrumbs?: boolean;
  breadcrumbs?: Array<{ label: string; href: string }>;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function ResponsiveLayout({ 
  children, 
  showBreadcrumbs = true, 
  breadcrumbs,
  title,
  subtitle,
  actions 
}: ResponsiveLayoutProps) {
  return (
    <NavigationProvider>
      <div className="min-h-screen min-h-[100dvh] bg-gray-50">
        {/* Desktop Sidebar */}
        <Sidebar />
        
        {/* Main Content */}
        <div className="md:pl-64">
          {/* Desktop Header */}
          <div className="hidden md:block bg-white shadow-sm border-b">
            <div className="px-4 sm:px-6 lg:px-8">
              <div className="flex items-center justify-between h-16">
                <div>
                  <h1 className="text-lg font-semibold text-gray-900">
                    {title || 'Dashboard'}
                  </h1>
                </div>
                {actions && (
                  <div className="flex items-center space-x-4">
                    {actions}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Mobile Header */}
          <div className="md:hidden bg-white shadow-sm border-b">
            <div className="px-4 py-4">
              <h1 className="text-xl font-bold text-gray-900">
                {title || 'InmueblesApp'}
              </h1>
              {subtitle && (
                <p className="text-sm text-gray-600 mt-1">{subtitle}</p>
              )}
            </div>
          </div>

          {/* Breadcrumbs */}
          {showBreadcrumbs && (
            <div className="hidden md:block">
              <Breadcrumbs items={breadcrumbs} />
            </div>
          )}
          
          {/* Main Content Area */}
          <main className="px-4 sm:px-6 lg:px-8 py-6 pb-20 md:pb-6">
            {(title || actions) && (
              <div className="hidden md:block mb-6">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                  <div className="mb-4 sm:mb-0">
                    {title && (
                      <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
                    )}
                    {subtitle && (
                      <p className="mt-1 text-sm text-gray-600">{subtitle}</p>
                    )}
                  </div>
                  {actions && (
                    <div className="flex flex-col sm:flex-row gap-3">
                      {actions}
                    </div>
                  )}
                </div>
              </div>
            )}
            
            <div className="space-y-6">
              {children}
            </div>
          </main>
        </div>

        {/* Mobile Bottom Navigation */}
        <BottomNavigation />
      </div>
    </NavigationProvider>
  );
}