"use client";
import { usePathname } from "next/navigation";
import Link from "next/link";

interface BreadcrumbItem {
  label: string;
  href: string;
}

interface BreadcrumbsProps {
  items?: BreadcrumbItem[];
}

export default function Breadcrumbs({ items }: BreadcrumbsProps) {
  const pathname = usePathname();
  
  // Check if we're in a financial agent sub-page
  const isInFinancialAgentSubPage = pathname.startsWith('/financial-agent/') && pathname !== '/financial-agent';
  
  // Auto-generate breadcrumbs if none provided
  const generateBreadcrumbs = (): BreadcrumbItem[] => {
    const pathSegments = pathname.split('/').filter(Boolean);
    const breadcrumbs: BreadcrumbItem[] = [
      { label: 'Dashboard', href: '/dashboard' }
    ];

    let currentPath = '';
    pathSegments.forEach((segment, index) => {
      currentPath += `/${segment}`;
      
      if (segment === 'dashboard' && index === 0) return;
      
      let label = segment.charAt(0).toUpperCase() + segment.slice(1);
      
      // Custom labels for specific segments
      const customLabels: Record<string, string> = {
        'properties': 'Propiedades',
        'financial-agent': 'Agente Financiero',
        'movements': 'Movimientos',
        'contracts': 'Contratos',
        'rules': 'Reglas',
        'mortgage': 'Hipoteca',
        'property': 'Propiedad'
      };
      
      if (customLabels[segment]) {
        label = customLabels[segment];
      }
      
      // Don't show numeric IDs in breadcrumbs
      if (!isNaN(Number(segment))) {
        return;
      }
      
      breadcrumbs.push({
        label,
        href: currentPath
      });
    });

    return breadcrumbs;
  };

  const breadcrumbItems = items || generateBreadcrumbs();

  if (breadcrumbItems.length <= 1) {
    return null;
  }

  return (
    <nav className="bg-gray-50 border-b px-6 py-3">
      <div className="flex items-center justify-between">
        <ol className="flex items-center space-x-2 text-sm text-gray-600">
          {breadcrumbItems.map((item, index) => (
            <li key={item.href} className="flex items-center">
              {index > 0 && (
                <svg className="w-4 h-4 mx-2 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                </svg>
              )}
              {index === breadcrumbItems.length - 1 ? (
                <span className="font-medium text-gray-900">{item.label}</span>
              ) : (
                <Link 
                  href={item.href}
                  className="hover:text-blue-600 transition-colors"
                >
                  {item.label}
                </Link>
              )}
            </li>
          ))}
        </ol>
        
        {/* Back button for financial agent sub-pages */}
        {isInFinancialAgentSubPage && (
          <Link 
            href="/financial-agent"
            className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            <span>Volver al Agente Financiero</span>
          </Link>
        )}
      </div>
    </nav>
  );
}