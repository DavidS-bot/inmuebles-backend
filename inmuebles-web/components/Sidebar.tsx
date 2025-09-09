"use client";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Building2, 
  TrendingUp, 
  BarChart3, 
  Settings,
  LogOut,
  User,
  Calculator,
  Bell,
  ArrowUpDown,
  PieChart,
  Target
} from 'lucide-react';
import { useRouter } from 'next/navigation';
import { persistToken } from '@/lib/auth';
import { useNotifications } from '@/hooks/useNotifications';

interface NavItem {
  id: string;
  label: string;
  href: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
  badge?: number;
}

interface NavGroup {
  title: string;
  items: NavItem[];
}

// Organized navigation groups
function getNavGroups(badgeData: Record<string, number>): NavGroup[] {
  return [
    {
      title: "Principal",
      items: [
        {
          id: 'dashboard-principal',
          label: 'Dashboard',
          href: '/dashboard',
          icon: Home,
          badge: badgeData.dashboard || 0
        }
      ]
    },
    {
      title: "Finanzas",
      items: [
        {
          id: 'financial-agent',
          label: 'Agente Financiero',
          href: '/financial-agent',
          icon: PieChart,
          badge: badgeData.financialAgent || 0
        },
        {
          id: 'movements',
          label: 'Movimientos',
          href: '/financial-agent/movements',
          icon: ArrowUpDown,
          badge: badgeData.movements || 0
        },
        {
          id: 'analytics',
          label: 'Analítica',
          href: '/financial-agent/analytics',
          icon: BarChart3,
          badge: badgeData.analytics || 0
        },
        {
          id: 'estudios-viabilidad',
          label: 'Estudios de Viabilidad',
          href: '/estudios-viabilidad',
          icon: Target,
          badge: badgeData.viabilityStudies || 0
        },
        {
          id: 'tax-assistant',
          label: 'Asistente Fiscal',
          href: '/financial-agent/tax-assistant',
          icon: Calculator,
          badge: badgeData.taxAssistant || 0
        },
        {
          id: 'payment-settings',
          label: 'Config. Pagos',
          href: '/financial-agent/payment-settings',
          icon: Settings,
          badge: badgeData.paymentSettings || 0
        }
      ]
    },
    {
      title: "Gestión",
      items: [
        {
          id: 'notifications',
          label: 'Notificaciones',
          href: '/notifications',
          icon: Bell,
          badge: badgeData.notifications || 0
        },
        {
          id: 'settings',
          label: 'Configuración',
          href: '/dashboard/settings',
          icon: Settings,
          badge: badgeData.settings || 0
        }
      ]
    }
  ];
}

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const { unreadCount } = useNotifications();
  
  const badgeData = {
    dashboard: 0,
    financialAgent: 0,
    movements: 3, // Unclassified movements
    analytics: 1, // New insights available
    viabilityStudies: 0, // Number of studies
    taxAssistant: 0,
    paymentSettings: 0,
    notifications: unreadCount, // Dynamic notification count
    settings: 0,
  };
  
  const navGroups = getNavGroups(badgeData);

  const getActiveTab = () => {
    if (pathname.includes('/estudios-viabilidad')) {
      return 'estudios-viabilidad';
    } else if (pathname.includes('/financial-agent')) {
      if (pathname.includes('/analytics')) return 'analytics';
      if (pathname.includes('/movements')) return 'movements';
      if (pathname.includes('/tax-assistant')) return 'tax-assistant';
      if (pathname.includes('/payment-settings')) return 'payment-settings';
      return 'financial-agent';
    } else if (pathname.includes('/dashboard')) {
      return 'dashboard-principal';
    } else if (pathname.includes('/notifications')) {
      return 'notifications';
    } else if (pathname.includes('/settings')) {
      return 'settings';
    }
    return 'dashboard-principal';
  };

  const activeTab = getActiveTab();

  const handleLogout = () => {
    persistToken(null);
    router.push("/login");
  };

  const NavLink = ({ item }: { item: NavItem }) => {
    const Icon = item.icon;
    const isActive = activeTab === item.id;
    
    return (
      <Link
        href={item.href}
        className={`group relative overflow-hidden rounded-xl mx-2 mb-1 transition-all duration-300 ${
          isActive
            ? 'bg-gradient-to-r from-blue-50 to-blue-100 text-blue-700 shadow-sm border border-blue-200'
            : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
        }`}
      >
        <div className={`absolute inset-0 bg-gradient-to-r from-blue-500/0 via-blue-500/5 to-blue-500/0 opacity-0 group-hover:opacity-100 transition-all duration-300 ${isActive ? 'opacity-100' : ''}`} />
        <div className="relative z-10 flex items-center px-4 py-3">
          <div className="relative">
            <Icon 
              size={20} 
              className={`mr-3 transition-all duration-300 ${
                isActive 
                  ? 'text-blue-600 scale-110' 
                  : 'text-gray-500 group-hover:text-gray-600 group-hover:scale-105'
              }`} 
            />
            {item.badge && item.badge > 0 && (
              <span className={`absolute -top-2 -right-1 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold transition-all duration-300 ${
                item.id === 'notifications' 
                  ? 'bg-red-500 animate-pulse shadow-lg shadow-red-500/50' 
                  : 'bg-red-500'
              }`}>
                {item.badge > 9 ? '9+' : item.badge}
              </span>
            )}
          </div>
          <span className="text-sm font-medium">{item.label}</span>
          {isActive && (
            <div className="ml-auto w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
          )}
        </div>
      </Link>
    );
  };

  return (
    <div className="hidden md:flex md:w-64 md:flex-col md:fixed md:inset-y-0 bg-white border-r border-gray-200 shadow-sm">
      <div className="flex flex-col h-full">
        {/* Header fijo */}
        <div className="flex-shrink-0 bg-gradient-to-r from-blue-600 to-blue-700 p-4 rounded-b-2xl mb-6">
          <Link href="/dashboard" className="block">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center backdrop-blur-sm">
                <Building2 size={22} className="text-white" />
              </div>
              <div>
                <h2 className="text-white font-bold text-lg">InmoAgent</h2>
                <p className="text-blue-100 text-xs">Gestión Inmobiliaria</p>
              </div>
            </div>
          </Link>
        </div>

        {/* Navegación con scroll */}
        <div className="flex-1 overflow-y-auto px-2">
          <div className="space-y-6">
            {navGroups.map((group) => (
              <div key={group.title}>
                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-3 px-3">
                  {group.title}
                </h3>
                <div className="space-y-1">
                  {group.items.map((item) => (
                    <NavLink key={item.id} item={item} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Footer fijo */}
        <div className="flex-shrink-0 border-t border-gray-200 p-4 space-y-2">
          {/* User Profile */}
          <div className="flex items-center px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-gray-50 transition-colors duration-200">
            <div className="w-8 h-8 bg-gray-200 rounded-full flex items-center justify-center mr-3">
              <User size={16} className="text-gray-500" />
            </div>
            <div>
              <p className="font-medium text-xs">Mi Perfil</p>
              <p className="text-gray-400 text-xs">Usuario</p>
            </div>
          </div>

          {/* Logout */}
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm text-gray-600 rounded-lg hover:bg-red-50 hover:text-red-600 transition-all duration-200 group"
          >
            <LogOut size={16} className="mr-3 text-gray-400 group-hover:text-red-500 transition-colors" />
            <span className="font-medium text-xs">Cerrar Sesión</span>
          </button>
        </div>
      </div>
    </div>
  );
}