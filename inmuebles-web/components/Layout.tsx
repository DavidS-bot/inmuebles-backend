"use client";
import Topbar from "./Topbar";
import Breadcrumbs from "./Breadcrumbs";

interface LayoutProps {
  children: React.ReactNode;
  showBreadcrumbs?: boolean;
  breadcrumbs?: Array<{ label: string; href: string }>;
  title?: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export default function Layout({ 
  children, 
  showBreadcrumbs = true, 
  breadcrumbs,
  title,
  subtitle,
  actions 
}: LayoutProps) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Topbar />
      {showBreadcrumbs && <Breadcrumbs items={breadcrumbs} />}
      
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {(title || actions) && (
          <div className="mb-6">
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
  );
}