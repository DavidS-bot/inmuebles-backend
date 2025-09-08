"use client";
import { useState, useEffect } from "react";
import ResponsiveLayout from "@/components/ResponsiveLayout";
import Link from "next/link";
import api from "@/lib/api";
import ConfirmDialog from "@/components/ConfirmDialog";

interface Property {
  id: number;
  address: string;
  property_type?: string;
  rooms?: number;
  m2?: number;
  purchase_price?: number;
  purchase_date?: string;
  photo?: string | null;
}

interface FinancialStats {
  total_properties: number;
  total_investment: number;
  total_market_value: number;
  total_gross_income: number;
  total_expenses: number;
  total_net_income: number;
  total_equity: number;
  total_debt: number;
}

interface RentalContract {
  id: number;
  property_id: number;
  tenant_name: string;
  start_date: string;
  end_date?: string;
  monthly_rent: number;
  deposit?: number;
  is_active: boolean;
}

interface TenantPaymentStatus {
  tenant_name: string;
  property_address: string;
  monthly_rent: number;
  has_paid_current_month: boolean;
  last_payment_date?: string;
  days_since_payment?: number;
}

export default function DashboardPage() {
  const [properties, setProperties] = useState<Property[]>([]);
  const [stats, setStats] = useState<FinancialStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [showPropertiesList, setShowPropertiesList] = useState(false);
  const [contracts, setContracts] = useState<RentalContract[]>([]);
  const [tenantPayments, setTenantPayments] = useState<TenantPaymentStatus[]>([]);
  const [showTenantDetails, setShowTenantDetails] = useState(false);
  
  // Property management states (copied from properties page)
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [err, setErr] = useState<string>("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [propertyToDelete, setPropertyToDelete] = useState<Property | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  const [showPhotoEditModal, setShowPhotoEditModal] = useState(false);
  const [editingProperty, setEditingProperty] = useState<Property | null>(null);
  const [editingPhotoFile, setEditingPhotoFile] = useState<File | null>(null);
  const [editingPhotoPreview, setEditingPhotoPreview] = useState<string | null>(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  // Form fields
  const [formData, setFormData] = useState({
    address: "",
    property_type: "Piso",
    rooms: "",
    m2: "",
    purchase_price: "",
    purchase_date: "",
    photo: ""
  });

  useEffect(() => {
    loadDashboardData();
  }, []);

  // Calculate tenant payment status when contracts and properties change
  useEffect(() => {
    if (contracts.length > 0 && properties.length > 0) {
      console.log('Contracts and properties loaded, calculating tenant payment status...');
      calculateTenantPaymentStatus();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [contracts, properties]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load properties
      const propertiesRes = await api.get("/properties");
      const propertiesList = propertiesRes.data;
      setProperties(propertiesList);
      
      // Load contracts
      try {
        console.log("Loading rental contracts...");
        const contractsRes = await api.get("/rental-contracts/");
        console.log("Contracts API response:", contractsRes.data);
        console.log("Number of contracts loaded:", contractsRes.data.length);
        setContracts(contractsRes.data);
      } catch (e) {
        console.error("Could not load contracts:", e);
        console.error("Contract loading error details:", e.response?.data);
      }

      // Calculate weighted averages per property
      let totalGrossIncome = 0;
      let totalExpenses = 0;
      let totalDebt = 0;
      let totalMarketValue = 0;
      
      // Use the same analytics endpoint that Dashboard Analytics uses
      try {
        const currentYear = new Date().getFullYear();
        const analyticsRes = await api.get(`/analytics/portfolio-summary?year=${currentYear}`);
        const portfolioData = analyticsRes.data;
        
        console.log('Portfolio summary data:', portfolioData);
        
        // Extract totals from portfolio summary (same as Analytics dashboard)
        totalGrossIncome = portfolioData.total_income || 0;
        totalExpenses = portfolioData.total_expenses || 0;
        
        console.log(`Analytics totals - Income: ${totalGrossIncome}, Expenses: ${totalExpenses}`);
        
      } catch (e) {
        console.log("Could not load analytics data, falling back to financial movements");
        
        // Fallback to financial movements if analytics endpoint fails
        try {
          const movementsRes = await api.get("/financial-movements");
          const movements = movementsRes.data;
          
          const currentYear = new Date().getFullYear();
          const movements2025 = movements.filter((m: any) => {
            if (!m.date) return false;
            const movementYear = new Date(m.date).getFullYear();
            return movementYear === currentYear;
          });
          
          totalGrossIncome = movements2025
            .filter((m: any) => m.amount > 0)
            .reduce((sum: number, m: any) => sum + m.amount, 0);
          
          totalExpenses = movements2025
            .filter((m: any) => m.amount < 0)
            .reduce((sum: number, m: any) => sum + Math.abs(m.amount), 0);
          
        } catch (e2) {
          console.log("Could not load movements either");
        }
      }

      // Load mortgages for debt - FIXED: use trailing slash endpoint
      try {
        const mortgagesRes = await api.get("/mortgage-details/");
        totalDebt = mortgagesRes.data.reduce((sum: number, m: any) => sum + (m.outstanding_balance || 0), 0);
        console.log(`FIXED: Loaded ${mortgagesRes.data.length} mortgages, total debt: ${totalDebt}`);
      } catch (e) {
        console.log("Could not load mortgages:", e);
      }

      // Calculate totals
      const totalInvestment = propertiesList.reduce(
        (sum: number, p: Property) => sum + (p.purchase_price || 0), 
        0
      );

      // Estimate market value (use purchase price * 1.1 as rough estimate if no current value)
      totalMarketValue = propertiesList.reduce((sum: number, p: any) => {
        return sum + (p.current_value || p.purchase_price * 1.1 || 0);
      }, 0);

      const totalEquity = totalMarketValue - totalDebt;
      const totalNetIncome = totalGrossIncome - totalExpenses;

      setStats({
        total_properties: propertiesList.length,
        total_investment: totalInvestment,
        total_market_value: totalMarketValue,
        total_gross_income: totalGrossIncome,
        total_expenses: totalExpenses,
        total_net_income: totalNetIncome,
        total_equity: totalEquity,
        total_debt: totalDebt
      });
      
      // Calculate tenant payment status after contracts are loaded

    } catch (error) {
      console.error("Error loading dashboard data:", error);
    } finally {
      setLoading(false);
    }
  };
  
  const calculateTenantPaymentStatus = async () => {
    try {
      // Get all movements
      const movementsRes = await api.get("/financial-movements");
      const movements = movementsRes.data;
      
      console.log('Total movements loaded:', movements.length);
      
      const currentDate = new Date();
      const currentMonth = currentDate.getMonth();
      const currentYear = currentDate.getFullYear();
      
      console.log(`Looking for payments in: ${currentMonth + 1}/${currentYear}`);
      
      // Filter rent movements only
      const rentMovements = movements.filter((m: any) => 
        m.category === 'Renta' && m.amount > 0
      );
      
      console.log('Total rent movements found:', rentMovements.length);
      
      // Calculate the last 5 business days of previous month
      const getLastBusinessDaysOfPreviousMonth = () => {
        // Get first day of current month
        const firstDayCurrentMonth = new Date(currentYear, currentMonth, 1);
        
        // Get last day of previous month
        const lastDayPreviousMonth = new Date(firstDayCurrentMonth);
        lastDayPreviousMonth.setDate(0); // This sets it to the last day of previous month
        
        const businessDays = [];
        let currentCheckDate = new Date(lastDayPreviousMonth);
        let businessDaysFound = 0;
        
        // Go backwards from last day of previous month to find 5 business days
        while (businessDaysFound < 5 && currentCheckDate.getMonth() === lastDayPreviousMonth.getMonth()) {
          const dayOfWeek = currentCheckDate.getDay();
          
          // Skip weekends (0 = Sunday, 6 = Saturday)
          if (dayOfWeek !== 0 && dayOfWeek !== 6) {
            businessDays.push(new Date(currentCheckDate));
            businessDaysFound++;
          }
          
          currentCheckDate.setDate(currentCheckDate.getDate() - 1);
        }
        
        return businessDays;
      };
      
      const lastBusinessDaysPreviousMonth = getLastBusinessDaysOfPreviousMonth();
      
      console.log('Last 5 business days of previous month:', 
        lastBusinessDaysPreviousMonth.map(d => d.toISOString().split('T')[0]));
      
      // Filter movements for current month OR last 5 business days of previous month
      const validPaymentPeriodMovements = rentMovements.filter((m: any) => {
        const movementDate = new Date(m.date);
        
        // Check if it's in current month
        if (movementDate.getMonth() === currentMonth && movementDate.getFullYear() === currentYear) {
          return true;
        }
        
        // Check if it's in the last 5 business days of previous month
        return lastBusinessDaysPreviousMonth.some(businessDay => {
          return movementDate.getDate() === businessDay.getDate() &&
                 movementDate.getMonth() === businessDay.getMonth() &&
                 movementDate.getFullYear() === businessDay.getFullYear();
        });
      });
      
      console.log(`Valid payment period movements (current month + last 5 business days of previous): ${validPaymentPeriodMovements.length}`);
      
      // Get only truly active contracts (vigentes)
      const activeContracts = contracts.filter(contract => {
        console.log(`Evaluating contract ${contract.id} - ${contract.tenant_name}:`, {
          start_date: contract.start_date,
          end_date: contract.end_date,
          is_active: contract.is_active
        });
        
        // Must be marked as active in database
        if (!contract.is_active) {
          console.log(`Contract ${contract.id} filtered out: not marked as active in DB`);
          return false;
        }
        
        // Contract must have started (not future contracts)
        const startDate = new Date(contract.start_date);
        if (startDate > currentDate) {
          console.log(`Contract ${contract.id} filtered out: starts in future (${contract.start_date})`);
          return false;
        }
        
        // Most important: Check if contract has actually ended
        if (contract.end_date) {
          const endDate = new Date(contract.end_date);
          
          // If contract has ended (even recently), it's not active anymore
          if (endDate < currentDate) {
            console.log(`Contract ${contract.id} filtered out: already ended (${contract.end_date})`);
            return false;
          }
          
          console.log(`Contract ${contract.id} included: active until ${contract.end_date}`);
        } else {
          console.log(`Contract ${contract.id} included: indefinite contract (no end date)`);
        }
        
        return true;
      });
      
      console.log('📊 CONTRACT SUMMARY:');
      console.log(`Total contracts in database: ${contracts.length}`);
      console.log(`Active/vigente contracts: ${activeContracts.length}`);
      console.log(`Filtered out: ${contracts.length - activeContracts.length}`);
      
      console.log('✅ VIGENTE CONTRACTS:');
      activeContracts.forEach(c => {
        console.log(`- ${c.tenant_name} (ID: ${c.id}) - Hasta: ${c.end_date || 'Indefinido'}`);
      });
      
      const filteredOut = contracts.filter(c => !activeContracts.find(ac => ac.id === c.id));
      if (filteredOut.length > 0) {
        console.log('❌ FILTERED OUT CONTRACTS:');
        filteredOut.forEach(c => {
          const reason = !c.is_active ? 'Inactive in DB' : 
                       c.end_date && new Date(c.end_date) < currentDate ? `Ended ${c.end_date}` :
                       new Date(c.start_date) > currentDate ? `Starts ${c.start_date}` : 'Unknown';
          console.log(`- ${c.tenant_name} (ID: ${c.id}) - Reason: ${reason}`);
        });
      }
      
      // Create tenant payment status
      const paymentStatus: TenantPaymentStatus[] = activeContracts
        .map(contract => {
          const property = properties.find(p => p.id === contract.property_id);
          
          // Check for payment in valid period (current month + last 5 business days of previous month)
          const hasCurrentMonthPayment = validPaymentPeriodMovements.some((m: any) => 
            m.tenant_name === contract.tenant_name || 
            (m.property_id === contract.property_id && m.amount >= contract.monthly_rent * 0.8)
          );
          
          // Find most recent payment for this tenant/property
          const recentPayments = rentMovements
            .filter((m: any) => {
              // Match by tenant name first (most reliable)
              if (m.tenant_name && contract.tenant_name) {
                const movementTenant = m.tenant_name.toLowerCase().trim();
                const contractTenant = contract.tenant_name.toLowerCase().trim();
                
                // Check if names match or contain each other
                if (movementTenant === contractTenant || 
                    movementTenant.includes(contractTenant.split(' ')[0]) ||
                    contractTenant.includes(movementTenant.split(' ')[0])) {
                  return true;
                }
              }
              
              // Fallback: match by property and rent amount
              return m.property_id === contract.property_id && 
                     m.amount >= contract.monthly_rent * 0.8 && 
                     m.amount <= contract.monthly_rent * 1.2;
            })
            .sort((a: any, b: any) => new Date(b.date).getTime() - new Date(a.date).getTime());
          
          const lastPayment = recentPayments[0];
          const daysSincePayment = lastPayment ? 
            Math.floor((currentDate.getTime() - new Date(lastPayment.date).getTime()) / (1000 * 60 * 60 * 24)) : 
            undefined;
          
          // Determine if tenant has paid for current month
          // Priority 1: Payment found in valid period (current month + last 5 business days of previous month)
          // Priority 2: If no payment in valid period, check if last payment was recent enough
          let hasPaidCurrentMonth = hasCurrentMonthPayment;
          
          if (!hasPaidCurrentMonth && lastPayment) {
            // If last payment was within the last 35 days, consider it valid
            // This covers cases where the payment might have been slightly earlier
            hasPaidCurrentMonth = daysSincePayment !== undefined && daysSincePayment <= 35;
          }
          
          return {
            tenant_name: contract.tenant_name,
            property_address: property?.address || 'Propiedad desconocida',
            monthly_rent: contract.monthly_rent,
            has_paid_current_month: hasPaidCurrentMonth,
            last_payment_date: lastPayment?.date,
            days_since_payment: daysSincePayment
          };
        });
      
      console.log('Tenant payment status calculated:', paymentStatus);
      setTenantPayments(paymentStatus);
    } catch (error) {
      console.error('Error calculating tenant payment status:', error);
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  // Property management functions (copied from properties page)
  const createProperty = async (e: React.FormEvent) => {
    e.preventDefault();
    setErr(""); setLoading(true);
    
    try {
      let photoUrl = null;
      
      if (selectedFile) {
        const formDataPhoto = new FormData();
        formDataPhoto.append('file', selectedFile);
        
        try {
          const photoResponse = await api.post('/uploads/photo', formDataPhoto, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });
          photoUrl = photoResponse.data.url;
        } catch (photoError) {
          console.error('Error uploading photo:', photoError);
          setErr('Error al subir la foto');
          return;
        }
      }

      const propertyData = {
        address: formData.address,
        property_type: formData.property_type,
        rooms: formData.rooms ? Number(formData.rooms) : undefined,
        m2: formData.m2 ? Number(formData.m2) : undefined,
        purchase_price: formData.purchase_price ? Number(formData.purchase_price) : undefined,
        purchase_date: formData.purchase_date || undefined,
        photo: photoUrl
      };

      await api.post("/properties", propertyData);
      
      setFormData({
        address: "",
        property_type: "Piso",
        rooms: "",
        m2: "",
        purchase_price: "",
        purchase_date: "",
        photo: ""
      });
      setSelectedFile(null);
      setPhotoPreview(null);
      setShowCreateForm(false);
      await loadDashboardData();
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? "Error creando propiedad");
    } finally { 
      setLoading(false); 
    }
  };

  const handleDeleteClick = (property: Property) => {
    setPropertyToDelete(property);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!propertyToDelete) return;
    
    setDeleting(true);
    try {
      console.log(`Attempting to delete property ${propertyToDelete.id}: ${propertyToDelete.address}`);
      console.log('API base URL:', process.env.NEXT_PUBLIC_API_URL);
      
      const response = await api.delete(`/properties/${propertyToDelete.id}`);
      console.log("Delete response:", response.data);
      
      await loadDashboardData();
      setShowDeleteConfirm(false);
      setPropertyToDelete(null);
      
      // Show success message
      alert("Propiedad eliminada correctamente");
      
    } catch (error: any) {
      console.error("Error deleting property:", error);
      console.error("Error details:", {
        message: error.message,
        code: error.code,
        response: error.response,
        request: error.request
      });
      
      // More detailed error handling
      let errorMessage = "Error al eliminar la propiedad";
      
      if (error.code === 'NETWORK_ERROR' || error.message === 'Network Error') {
        errorMessage = "Error de conexión. Verifica que el servidor esté ejecutándose.";
      } else if (error.code === 'ECONNABORTED') {
        errorMessage = "La operación tardó demasiado. Intenta de nuevo.";
      } else if (error?.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error?.response?.status === 404) {
        errorMessage = "La propiedad no fue encontrada";
      } else if (error?.response?.status === 403) {
        errorMessage = "No tienes permisos para eliminar esta propiedad";
      } else if (error?.response?.status === 500) {
        errorMessage = "Error interno del servidor. Por favor, intenta de nuevo.";
      } else if (error?.message) {
        errorMessage = error.message;
      }
      
      alert(errorMessage);
    } finally {
      setDeleting(false);
    }
  };

  const handleDeleteCancel = () => {
    setShowDeleteConfirm(false);
    setPropertyToDelete(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      
      const reader = new FileReader();
      reader.onload = (e) => {
        setPhotoPreview(e.target?.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removePhoto = () => {
    setSelectedFile(null);
    setPhotoPreview(null);
  };

  const openPhotoEditModal = (property: Property) => {
    setEditingProperty(property);
    setEditingPhotoFile(null);
    setEditingPhotoPreview(null);
    setShowPhotoEditModal(true);
  };

  const handleEditPhotoFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setEditingPhotoFile(file);
      
      const reader = new FileReader();
      reader.onloadend = () => {
        setEditingPhotoPreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const removeEditPhoto = () => {
    setEditingPhotoFile(null);
    setEditingPhotoPreview(null);
  };

  const savePhotoEdit = async () => {
    if (!editingProperty || !editingPhotoFile) return;
    
    setUploadingPhoto(true);
    
    try {
      const formData = new FormData();
      formData.append('file', editingPhotoFile);
      
      const photoResponse = await api.post('/uploads/photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      await api.put(`/properties/${editingProperty.id}`, {
        ...editingProperty,
        photo: photoResponse.data.url
      });
      
      await loadDashboardData();
      setShowPhotoEditModal(false);
      setEditingProperty(null);
      setEditingPhotoFile(null);
      setEditingPhotoPreview(null);
      
    } catch (error) {
      console.error('Error uploading photo:', error);
      alert('Error al subir la foto');
    } finally {
      setUploadingPhoto(false);
    }
  };

  if (loading) {
    return (
      <ResponsiveLayout title="Dashboard" subtitle="Cargando información...">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
      </ResponsiveLayout>
    );
  }

  return (
    <ResponsiveLayout 
      title="Dashboard Principal" 
      subtitle="Vista general de tu portafolio inmobiliario"
      showBreadcrumbs={false}
    >
      {/* Property background image */}
      <div 
        className="fixed inset-0 opacity-10 z-[-1]"
        style={{
          backgroundImage: 'url(/platon30.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: 'center',
          backgroundRepeat: 'no-repeat',
          filter: 'contrast(1.2) brightness(1.1)'
        }}
      />
      {/* Main Financial Summary */}
      <div className="bg-gradient-to-br from-white to-gray-50 rounded-2xl shadow-xl p-8 mb-8 border border-gray-100">
        <h2 className="text-2xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent mb-6">
          Resumen Financiero Total
        </h2>
        
        {/* Primary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-blue-600 text-sm font-medium uppercase tracking-wide">Valor Total Mercado</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {formatCurrency(stats?.total_market_value || 0)}
                </p>
                <p className="text-xs text-blue-600 mt-1">Valoración actual estimada</p>
              </div>
              <div className="text-4xl">🏢</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-green-600 text-sm font-medium uppercase tracking-wide">Equity Total</p>
                <p className="text-3xl font-bold text-green-900 mt-2">
                  {formatCurrency(stats?.total_equity || 0)}
                </p>
                <p className="text-xs text-green-600 mt-1">Patrimonio neto</p>
              </div>
              <div className="text-4xl">💎</div>
            </div>
          </div>

          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-xl p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-purple-600 text-sm font-medium uppercase tracking-wide">Deuda Total</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  {formatCurrency(stats?.total_debt || 0)}
                </p>
                <p className="text-xs text-purple-600 mt-1">Hipotecas pendientes</p>
              </div>
              <div className="text-4xl">🏦</div>
            </div>
          </div>
        </div>

        {/* Secondary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center text-white text-xl">
                🏠
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Propiedades</p>
                <p className="text-xl font-bold text-gray-900">{stats?.total_properties || 0}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-green-600 rounded-lg flex items-center justify-center text-white text-xl">
                💰
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Ingresos Totales 2025</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(stats?.total_gross_income || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-red-500 to-red-600 rounded-lg flex items-center justify-center text-white text-xl">
                📊
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Gastos Totales 2025</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(stats?.total_expenses || 0)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-lg flex items-center justify-center text-white text-xl">
                ✨
              </div>
              <div className="ml-4">
                <p className="text-xs text-gray-500 uppercase">Cash Neto Total 2025</p>
                <p className="text-xl font-bold text-gray-900">{formatCurrency(stats?.total_net_income || 0)}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Properties List Section */}
      <div className="mb-8">
        <div className="bg-white rounded-xl shadow-lg border border-gray-100">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Gestión de Propiedades</h3>
                <p className="text-sm text-gray-600 mt-1">
                  {properties.length} propiedades en tu portafolio
                </p>
              </div>
              <div className="flex items-center space-x-3">
                <button
                  onClick={() => setShowCreateForm(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2 text-sm"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                  <span>Nueva Propiedad</span>
                </button>
                <button
                  onClick={() => setShowPropertiesList(!showPropertiesList)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                    showPropertiesList 
                      ? "bg-gray-100 text-gray-700" 
                      : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                  }`}
                >
                  <span>{showPropertiesList ? 'Ocultar Lista' : 'Ver Lista Completa'}</span>
                  <svg className={`w-4 h-4 transition-transform ${showPropertiesList ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </div>
            </div>
          </div>
          
          {/* Collapsible Properties List */}
          {showPropertiesList && (
            <div className="p-6">
              {properties.length === 0 ? (
                <div className="text-center py-12">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                    </svg>
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No hay propiedades</h3>
                  <p className="text-gray-500 mb-6">Comienza agregando tu primera propiedad al portafolio</p>
                  <button
                    onClick={() => setShowCreateForm(true)}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700"
                  >
                    <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                    </svg>
                    Agregar Primera Propiedad
                  </button>
                </div>
              ) : (
                <div className="grid gap-4">
                  {properties.map((property) => (
                    <div key={property.id} className="group relative bg-gradient-to-br from-white to-gray-50 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100">
                      <div className="absolute inset-0 bg-gradient-to-r from-blue-500/5 to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                      <div className="relative p-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-5">
                            <div className="flex-shrink-0 relative">
                              {property.photo ? (
                                <img 
                                  src={property.photo.startsWith('http') ? property.photo : `${process.env.NEXT_PUBLIC_API_URL}${property.photo}`} 
                                  alt={property.address}
                                  className="w-20 h-20 rounded-xl object-cover shadow-lg border-2 border-white"
                                  onError={(e) => {
                                    const target = e.target as HTMLImageElement;
                                    target.style.display = 'none';
                                    target.nextElementSibling?.classList.remove('hidden');
                                  }}
                                />
                              ) : null}
                              <div className={`w-20 h-20 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center shadow-lg ${property.photo ? 'hidden' : ''}`}>
                                <svg className="w-10 h-10 text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path d="M10.707 2.293a1 1 0 00-1.414 0l-7 7a1 1 0 001.414 1.414L4 10.414V17a1 1 0 001 1h2a1 1 0 001-1v-2a1 1 0 011-1h2a1 1 0 011 1v2a1 1 0 001 1h2a1 1 0 001-1v-6.586l.293.293a1 1 0 001.414-1.414l-7-7z" />
                                </svg>
                              </div>
                              <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white flex items-center justify-center">
                                <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                </svg>
                              </div>
                            </div>
                            <div>
                              <h3 className="text-xl font-semibold bg-gradient-to-r from-gray-900 to-gray-700 bg-clip-text text-transparent">
                                {property.address}
                              </h3>
                              <div className="flex items-center space-x-3 text-sm text-gray-600 mt-2">
                                {property.property_type && (
                                  <span className="bg-gradient-to-r from-blue-100 to-indigo-100 px-3 py-1 rounded-full text-xs font-medium text-blue-700">
                                    {property.property_type}
                                  </span>
                                )}
                                {property.rooms && (
                                  <span className="flex items-center">
                                    <svg className="w-4 h-4 mr-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                                      <path d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" fillRule="evenodd" clipRule="evenodd" />
                                    </svg>
                                    {property.rooms} hab
                                  </span>
                                )}
                                {property.m2 && (
                                  <span className="flex items-center">
                                    <svg className="w-4 h-4 mr-1 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4" />
                                    </svg>
                                    {property.m2}m²
                                  </span>
                                )}
                                {property.purchase_date && (
                                  <span className="flex items-center">
                                    <svg className="w-4 h-4 mr-1 text-gray-400" fill="currentColor" viewBox="0 0 20 20">
                                      <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd" />
                                    </svg>
                                    {formatDate(property.purchase_date)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <div className="flex items-center space-x-6">
                            <div className="text-right flex-1">
                              {property.purchase_price && (
                                <div>
                                  <p className="text-xs text-gray-500 uppercase tracking-wide">Valor</p>
                                  <p className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-indigo-600 bg-clip-text text-transparent">
                                    {formatCurrency(property.purchase_price)}
                                  </p>
                                </div>
                              )}
                              <div className="flex flex-wrap gap-2 mt-3 justify-end">
                                <Link
                                  href={`/financial-agent/property/${property.id}`}
                                  className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-blue-500 to-blue-600 text-white text-sm font-medium rounded-lg hover:from-blue-600 hover:to-blue-700 transition-all shadow-sm hover:shadow-md"
                                >
                                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                                  </svg>
                                  Finanzas
                                </Link>
                                <Link
                                  href={`/financial-agent/property/${property.id}/mortgage`}
                                  className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-purple-500 to-purple-600 text-white text-sm font-medium rounded-lg hover:from-purple-600 hover:to-purple-700 transition-all shadow-sm hover:shadow-md"
                                >
                                  <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z" clipRule="evenodd" />
                                  </svg>
                                  Hipoteca
                                </Link>
                                <button
                                  onClick={() => openPhotoEditModal(property)}
                                  className="inline-flex items-center px-3 py-1.5 bg-gradient-to-r from-green-500 to-green-600 text-white text-sm font-medium rounded-lg hover:from-green-600 hover:to-green-700 transition-all shadow-sm hover:shadow-md"
                                >
                                  <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                  </svg>
                                  Cambiar Foto
                                </button>
                              </div>
                            </div>
                            
                            <div className="flex-shrink-0">
                              <button
                                onClick={() => handleDeleteClick(property)}
                                className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-md transition-colors"
                                title="Eliminar propiedad"
                              >
                                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                              </button>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Tenant Summary Section */}
      <div className="mb-8">
        <div className="bg-white rounded-xl shadow-lg p-6 border border-gray-100">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <span className="text-2xl mr-2">👥</span>
                Resumen de Inquilinos
              </h3>
              <p className="text-sm text-gray-600 mt-1">
                {tenantPayments.length} contratos vigentes de {contracts.length} totales - Pagos del mes actual
              </p>
            </div>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowTenantDetails(!showTenantDetails)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  showTenantDetails 
                    ? "bg-gray-100 text-gray-700" 
                    : "bg-gray-50 text-gray-600 hover:bg-gray-100"
                }`}
              >
                <span>{showTenantDetails ? 'Ocultar Detalles' : 'Ver Detalles'}</span>
                <svg className={`w-4 h-4 transition-transform ${showTenantDetails ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>
              <Link 
                href="/financial-agent/contracts" 
                className="text-sm text-blue-600 hover:text-blue-700 font-medium flex items-center"
              >
                Ver contratos completos
                <svg className="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </Link>
            </div>
          </div>

          {tenantPayments.length === 0 ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </div>
              <h4 className="text-lg font-medium text-gray-900 mb-2">No hay inquilinos activos</h4>
              <p className="text-gray-500">Crea contratos de alquiler para ver el estado de pagos</p>
            </div>
          ) : (
            <>
              {/* Summary Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
                <div className="bg-green-50 rounded-lg p-4 border border-green-200">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-green-500 rounded-lg flex items-center justify-center text-white text-xl">
                      ✅
                    </div>
                    <div className="ml-4">
                      <p className="text-sm text-green-600 font-medium">Al Día</p>
                      <p className="text-2xl font-bold text-green-800">
                        {tenantPayments.filter(t => t.has_paid_current_month).length}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-red-50 rounded-lg p-4 border border-red-200">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-red-500 rounded-lg flex items-center justify-center text-white text-xl">
                      ❌
                    </div>
                    <div className="ml-4">
                      <p className="text-sm text-red-600 font-medium">Pendientes</p>
                      <p className="text-2xl font-bold text-red-800">
                        {tenantPayments.filter(t => !t.has_paid_current_month).length}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-blue-500 rounded-lg flex items-center justify-center text-white text-xl">
                      💰
                    </div>
                    <div className="ml-4">
                      <p className="text-sm text-blue-600 font-medium">Total Esperado</p>
                      <p className="text-2xl font-bold text-blue-800">
                        {formatCurrency(tenantPayments.reduce((sum, t) => sum + t.monthly_rent, 0))}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Detailed List - Collapsible */}
              {showTenantDetails && (
                <div className="space-y-3">
                  <h4 className="font-medium text-gray-900 mb-3">Detalle por inquilino</h4>
                  {tenantPayments.map((tenant, index) => (
                    <div key={index} className={`p-4 rounded-lg border-2 transition-all ${
                      tenant.has_paid_current_month 
                        ? 'bg-green-50 border-green-200' 
                        : 'bg-red-50 border-red-200'
                    }`}>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-4">
                          <div className={`w-12 h-12 rounded-full flex items-center justify-center text-white font-bold ${
                            tenant.has_paid_current_month ? 'bg-green-500' : 'bg-red-500'
                          }`}>
                            {tenant.has_paid_current_month ? '✅' : '❌'}
                          </div>
                          <div>
                            <h5 className="font-semibold text-gray-900">{tenant.tenant_name}</h5>
                            <p className="text-sm text-gray-600">{tenant.property_address}</p>
                            {tenant.last_payment_date && (
                              <p className="text-xs text-gray-500">
                                Último pago: {formatDate(tenant.last_payment_date)}
                                {tenant.days_since_payment && (
                                  <span className={`ml-2 ${
                                    tenant.days_since_payment > 30 ? 'text-red-600 font-medium' : 
                                    tenant.days_since_payment > 15 ? 'text-yellow-600 font-medium' : ''
                                  }`}>
                                    ({tenant.days_since_payment} días)
                                  </span>
                                )}
                              </p>
                            )}
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-gray-900">
                            {formatCurrency(tenant.monthly_rent)}
                          </p>
                          <p className={`text-sm font-medium ${
                            tenant.has_paid_current_month ? 'text-green-600' : 'text-red-600'
                          }`}>
                            {tenant.has_paid_current_month ? 'Al Día' : 'Pendiente'}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* All the property management modals from properties page */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-gray-900">Nueva Propiedad</h2>
                <button
                  onClick={() => {
                    setShowCreateForm(false);
                    setErr("");
                  }}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              <form onSubmit={createProperty} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Dirección *
                  </label>
                  <input
                    type="text"
                    value={formData.address}
                    onChange={(e) => setFormData({...formData, address: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="Ej: Calle Mayor 123, Madrid"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Tipo de Propiedad
                  </label>
                  <select
                    value={formData.property_type}
                    onChange={(e) => setFormData({...formData, property_type: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="Piso">Piso</option>
                    <option value="Casa">Casa</option>
                    <option value="Local">Local Comercial</option>
                    <option value="Oficina">Oficina</option>
                    <option value="Garaje">Garaje</option>
                    <option value="Trastero">Trastero</option>
                    <option value="Otro">Otro</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Habitaciones
                    </label>
                    <input
                      type="number"
                      value={formData.rooms}
                      onChange={(e) => setFormData({...formData, rooms: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0"
                      min="0"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Superficie (m²)
                    </label>
                    <input
                      type="number"
                      value={formData.m2}
                      onChange={(e) => setFormData({...formData, m2: e.target.value})}
                      className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="0"
                      min="0"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Precio de Compra (€)
                  </label>
                  <input
                    type="number"
                    value={formData.purchase_price}
                    onChange={(e) => setFormData({...formData, purchase_price: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                    placeholder="0"
                    min="0"
                    step="0.01"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Fecha de Compra
                  </label>
                  <input
                    type="date"
                    value={formData.purchase_date}
                    onChange={(e) => setFormData({...formData, purchase_date: e.target.value})}
                    className="w-full border border-gray-300 rounded-md px-3 py-2 focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Foto de la Propiedad
                  </label>
                  
                  {photoPreview ? (
                    <div className="space-y-2">
                      <div className="relative">
                        <img 
                          src={photoPreview} 
                          alt="Vista previa" 
                          className="w-full h-32 object-cover rounded-md border border-gray-300"
                        />
                        <button
                          type="button"
                          onClick={removePhoto}
                          className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                      <button
                        type="button"
                        onClick={() => document.getElementById('photo-input')?.click()}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50"
                      >
                        Cambiar Foto
                      </button>
                    </div>
                  ) : (
                    <div 
                      onClick={() => document.getElementById('photo-input')?.click()}
                      className="w-full h-32 border-2 border-dashed border-gray-300 rounded-md flex items-center justify-center cursor-pointer hover:border-gray-400 transition-colors"
                    >
                      <div className="text-center">
                        <svg className="w-8 h-8 text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                        <p className="text-sm text-gray-600">Haz clic para subir una foto</p>
                        <p className="text-xs text-gray-500">PNG, JPG hasta 5MB</p>
                      </div>
                    </div>
                  )}
                  
                  <input
                    id="photo-input"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>

                {err && (
                  <div className="bg-red-50 border border-red-200 rounded-md p-3">
                    <p className="text-red-600 text-sm">{err}</p>
                  </div>
                )}

                <div className="flex justify-end space-x-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setShowCreateForm(false);
                      setErr("");
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                  <button
                    type="submit"
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? "Creando..." : "Crear Propiedad"}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Photo Edit Modal */}
      {showPhotoEditModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-semibold">Cambiar Foto de Propiedad</h2>
                <button 
                  onClick={() => setShowPhotoEditModal(false)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
              
              {editingProperty && (
                <div className="mb-4">
                  <p className="text-sm text-gray-600">Propiedad: {editingProperty.address}</p>
                  {editingProperty.photo && (
                    <div className="mt-2">
                      <p className="text-sm text-gray-600 mb-2">Foto actual:</p>
                      <img 
                        src={editingProperty.photo.startsWith('http') ? editingProperty.photo : `${process.env.NEXT_PUBLIC_API_URL}${editingProperty.photo}`} 
                        alt="Foto actual"
                        className="w-full h-32 object-cover rounded-lg border"
                      />
                    </div>
                  )}
                </div>
              )}

              <div className="space-y-4">
                {editingPhotoPreview ? (
                  <div className="space-y-3">
                    <p className="text-sm text-gray-600">Nueva foto:</p>
                    <div className="relative">
                      <img 
                        src={editingPhotoPreview} 
                        alt="Vista previa" 
                        className="w-full h-48 object-cover rounded-lg border border-gray-300"
                      />
                      <button
                        type="button"
                        onClick={removeEditPhoto}
                        className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                      </button>
                    </div>
                    <button
                      type="button"
                      onClick={() => document.getElementById('edit-photo-input')?.click()}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-50"
                    >
                      Seleccionar Otra Foto
                    </button>
                  </div>
                ) : (
                  <div 
                    onClick={() => document.getElementById('edit-photo-input')?.click()}
                    className="w-full h-48 border-2 border-dashed border-gray-300 rounded-lg flex items-center justify-center cursor-pointer hover:border-gray-400 transition-colors"
                  >
                    <div className="text-center">
                      <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                      </svg>
                      <p className="text-gray-600">Haz clic para seleccionar una nueva foto</p>
                      <p className="text-sm text-gray-500 mt-1">PNG, JPG hasta 5MB</p>
                    </div>
                  </div>
                )}
                
                <input
                  id="edit-photo-input"
                  type="file"
                  accept="image/*"
                  onChange={handleEditPhotoFileChange}
                  className="hidden"
                />
              </div>

              <div className="flex justify-end space-x-3 mt-6">
                <button 
                  onClick={() => setShowPhotoEditModal(false)}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                  disabled={uploadingPhoto}
                >
                  Cancelar
                </button>
                <button 
                  onClick={savePhotoEdit}
                  disabled={!editingPhotoFile || uploadingPhoto}
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
                >
                  {uploadingPhoto && (
                    <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                  )}
                  <span>{uploadingPhoto ? 'Subiendo...' : 'Guardar Foto'}</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <ConfirmDialog
        isOpen={showDeleteConfirm}
        title="Eliminar Propiedad"
        message={`¿Estás seguro de que quieres eliminar la propiedad "${propertyToDelete?.address}"? Esta acción no se puede deshacer y se eliminarán todos los datos financieros asociados.`}
        confirmText={deleting ? "Eliminando..." : "Sí, eliminar"}
        cancelText="Cancelar"
        confirmColor="red"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
      />

      {/* Footer Message */}
      <div className="text-center mt-8 text-gray-500 text-sm">
        <p>Made in Chaparrito with ❤️</p>
      </div>
    </ResponsiveLayout>
  );
}