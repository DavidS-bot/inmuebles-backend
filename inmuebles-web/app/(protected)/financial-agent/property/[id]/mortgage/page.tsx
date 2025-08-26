"use client";
import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";

interface Property {
  id: number;
  address: string;
}

interface MortgageDetails {
  id: number;
  property_id: number;
  loan_id?: string;
  bank_entity?: string;
  mortgage_type: string;
  initial_amount: number;
  outstanding_balance: number;
  margin_percentage: number;
  start_date: string;
  end_date: string;
  review_period_months: number;
}

interface MortgageRevision {
  id: number;
  effective_date: string;
  euribor_rate?: number;
  margin_rate: number;
  period_months: number;
}

interface MortgageSummary {
  total_payments: number;
  total_interest: number;
  total_principal: number;
  current_payment: number;
  current_balance: number;
  annual_rate: number;
  loan_term_months: number;
}

interface ROIAnalysis {
  property_id: number;
  year: number;
  financial_summary: {
    total_income: number;
    total_expenses: number;
    net_cash_flow: number;
    monthly_cash_flow: number;
  };
  investment_summary: {
    purchase_price: number;
    down_payment: number;
    acquisition_costs: number;
    renovation_costs: number;
    total_equity_invested: number;
    current_value: number;
  };
  roi_metrics: {
    cash_on_cash_roi: number;
    purchase_price_roi: number;
    cap_rate: number;
    monthly_roi: number;
  };
  mortgage_info?: {
    outstanding_balance: number;
    annual_payments: number;
    monthly_payment: number;
  };
}

interface ScheduleEntry {
  month: string;
  payment: number;
  interest: number;
  principal: number;
  balance: number;
  annual_rate: number;
  prepayment: number;
}

export default function PropertyMortgagePage() {
  const params = useParams();
  const propertyId = Number(params.id);
  
  const [property, setProperty] = useState<Property | null>(null);
  const [mortgage, setMortgage] = useState<MortgageDetails | null>(null);
  const [revisions, setRevisions] = useState<MortgageRevision[]>([]);
  const [summary, setSummary] = useState<MortgageSummary | null>(null);
  const [schedule, setSchedule] = useState<ScheduleEntry[]>([]);
  const [roiAnalysis, setRoiAnalysis] = useState<ROIAnalysis | null>(null);
  const [activeTab, setActiveTab] = useState<"summary" | "schedule" | "revisions" | "settings">("summary");
  const [loading, setLoading] = useState(true);
  const [showFullSchedule, setShowFullSchedule] = useState(false);
  const [revisionDates, setRevisionDates] = useState<string[]>([]);
  const [editingRevisions, setEditingRevisions] = useState<{[key: string]: MortgageRevision}>({});
  const [hasUnsavedChanges, setHasUnsavedChanges] = useState(false);
  const [showBulkPasteArea, setShowBulkPasteArea] = useState(false);
  const [bulkPasteText, setBulkPasteText] = useState('');

  // New mortgage form
  const [showNewMortgageForm, setShowNewMortgageForm] = useState(false);
  const [newMortgage, setNewMortgage] = useState({
    loan_id: "",
    bank_entity: "",
    mortgage_type: "Variable",
    initial_amount: 0,
    outstanding_balance: 0,
    margin_percentage: 0,
    start_date: "",
    end_date: "",
    review_period_months: 12
  });


  useEffect(() => {
    if (propertyId) {
      loadData();
    }
  }, [propertyId]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Load property
      const propertyRes = await api.get(`/properties/${propertyId}`);
      setProperty(propertyRes.data);

      // Load mortgage details
      try {
        const mortgageRes = await api.get(`/mortgage-details/property/${propertyId}/details`);
        if (mortgageRes.data) {
          setMortgage(mortgageRes.data);
          // Generate revision dates immediately with the mortgage data
          const generatedDates = generateRevisionDatesLocally(mortgageRes.data);
          setRevisionDates(generatedDates);
          await loadMortgageData(mortgageRes.data.id);
        } else {
          setShowNewMortgageForm(true);
        }
      } catch (error) {
        setShowNewMortgageForm(true);
      }
    } catch (error) {
      console.error("Error loading data:", error);
    } finally {
      setLoading(false);
    }
  };

  const generateRevisionDatesLocally = (mortgage: any) => {
    if (!mortgage || !mortgage.start_date || !mortgage.review_period_months) {
      console.log('Cannot generate dates: missing mortgage data', mortgage);
      return [];
    }
    
    const startDate = new Date(mortgage.start_date);
    const endDate = new Date(mortgage.end_date);
    const periodMonths = mortgage.review_period_months;
    
    console.log('Generating dates from:', startDate, 'to:', endDate, 'every', periodMonths, 'months');
    
    const dates = [];
    let currentDate = new Date(startDate);
    
    while (currentDate <= endDate) {
      dates.push(currentDate.toISOString().split('T')[0]); // YYYY-MM-DD format
      currentDate.setMonth(currentDate.getMonth() + periodMonths);
    }
    
    console.log('Generated revision dates:', dates);
    return dates;
  };

  const loadMortgageData = async (mortgageId: number) => {
    try {
      // Load revisions
      const revisionsRes = await api.get(`/mortgage-details/${mortgageId}/revisions`);
      setRevisions(revisionsRes.data);

      // Generate revision dates locally using mortgage data
      if (mortgage) {
        const generatedDates = generateRevisionDatesLocally(mortgage);
        setRevisionDates(generatedDates);
      }

      // Load summary
      const summaryRes = await api.get(`/mortgage-details/${mortgageId}/summary`);
      setSummary(summaryRes.data);

      // Load schedule
      const scheduleRes = await api.get(`/mortgage-details/${mortgageId}/calculate-schedule`);
      setSchedule(scheduleRes.data.schedule || []);

      // Load ROI analysis (optional, catch errors)
      try {
        const roiRes = await api.get(`/mortgage-details/property/${propertyId}/roi-analysis`);
        setRoiAnalysis(roiRes.data);
      } catch (error) {
        console.warn('ROI analysis not available:', error);
        setRoiAnalysis(null);
      }
    } catch (error) {
      console.error("Error loading mortgage data:", error);
    }
  };

  const handleCreateMortgage = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const mortgageData = {
        ...newMortgage,
        property_id: propertyId,
        initial_amount: Number(newMortgage.initial_amount),
        outstanding_balance: Number(newMortgage.outstanding_balance),
        margin_percentage: Number(newMortgage.margin_percentage),
        review_period_months: Number(newMortgage.review_period_months)
      };

      const response = await api.post("/mortgage-details", mortgageData);
      setMortgage(response.data);
      setShowNewMortgageForm(false);
      await loadMortgageData(response.data.id);
    } catch (error) {
      console.error("Error creating mortgage:", error);
      alert("Error al crear la hipoteca");
    }
  };


  const getRevisionForDate = (dateStr: string): MortgageRevision | null => {
    return revisions.find(rev => rev.effective_date === dateStr) || null;
  };

  const handleRevisionChange = (dateStr: string, field: string, value: any) => {
    console.log(`Manual change: ${field} = "${value}" for date ${dateStr}`);
    
    const currentRevision = getRevisionForDate(dateStr) || {
      id: 0,
      mortgage_id: mortgage?.id || 0,
      effective_date: dateStr,
      euribor_rate: null,
      margin_rate: mortgage?.margin_percentage || 0,
      period_months: mortgage?.review_period_months || 12
    };

    let processedValue = value;
    if (field === 'euribor_rate') {
      // Clean the value: remove % signs and convert commas to dots
      const cleanValue = typeof value === 'string' ? value.trim().replace('%', '').replace(',', '.') : value;
      processedValue = cleanValue === '' || cleanValue === null ? null : parseFloat(cleanValue);
      
      // Validate that it's a valid number (allow 0 and positive values)
      if (cleanValue !== '' && cleanValue !== null && (isNaN(processedValue))) {
        console.warn(`Invalid euribor_rate value: "${value}" -> "${cleanValue}"`);
        return; // Don't update with invalid values
      }
    } else if (field === 'margin_rate') {
      // Clean the value: remove % signs and convert commas to dots
      const cleanValue = typeof value === 'string' ? value.trim().replace('%', '').replace(',', '.') : value;
      processedValue = cleanValue === '' || cleanValue === null ? (mortgage?.margin_percentage || 0) : parseFloat(cleanValue);
      
      // Validate that it's a valid number (allow 0 and positive values)
      if (cleanValue !== '' && cleanValue !== null && (isNaN(processedValue))) {
        console.warn(`Invalid margin_rate value: "${value}" -> "${cleanValue}"`);
        return; // Don't update with invalid values
      }
    } else if (field === 'period_months') {
      processedValue = value === '' ? (mortgage?.review_period_months || 12) : parseInt(value);
    }

    const updatedRevision = {
      ...currentRevision,
      [field]: processedValue
    };

    console.log('Updated revision:', updatedRevision);

    setEditingRevisions(prev => ({
      ...prev,
      [dateStr]: updatedRevision
    }));
    
    setHasUnsavedChanges(true);
  };

  const processBulkPasteData = (pastedData: string, startIndex: number = 0) => {
    console.log('Processing bulk paste data:', pastedData);
    console.log('Revision dates available:', revisionDates);
    console.log('Start index:', startIndex);
    
    const rows = pastedData.split('\n').filter(row => row.trim());
    let processedCount = 0;
    
    // Build all changes first, then apply them in a single batch
    const newEditingRevisions: {[key: string]: MortgageRevision} = {};
    
    rows.forEach((row, rowIndex) => {
      const dateIndex = startIndex + rowIndex;
      console.log(`Processing row ${rowIndex}: "${row}", dateIndex: ${dateIndex}`);
      
      // Ensure we don't exceed available dates
      if (dateIndex >= revisionDates.length) {
        console.log(`Skipping row ${rowIndex}, dateIndex ${dateIndex} >= ${revisionDates.length}`);
        return;
      }
      
      const dateStr = revisionDates[dateIndex];
      console.log(`Date for index ${dateIndex}:`, dateStr);
      
      // Handle both tab-separated and single column data
      const columns = row.includes('\t') ? row.split('\t') : [row];
      
      // Get existing revision or create new one
      const existingRevision = getRevisionForDate(dateStr);
      const currentRevision = existingRevision || {
        id: 0,
        mortgage_id: mortgage?.id || 0,
        effective_date: dateStr,
        euribor_rate: null,
        margin_rate: mortgage?.margin_percentage || 0,
        period_months: mortgage?.review_period_months || 12
      };
      
      // Process Euribor value (first column or single column)
      if (columns.length >= 1 && columns[0].trim()) {
        const euriborValue = columns[0].trim().replace('%', '').replace(',', '.');
        console.log(`Processing Euribor value: "${columns[0].trim()}" -> "${euriborValue}"`);
        
        if (!isNaN(parseFloat(euriborValue)) && parseFloat(euriborValue) >= 0) {
          newEditingRevisions[dateStr] = {
            ...currentRevision,
            euribor_rate: parseFloat(euriborValue)
          };
          processedCount++;
          console.log(`Successfully processed Euribor: ${euriborValue} for date ${dateStr}`);
        } else {
          console.log(`Invalid Euribor value: "${euriborValue}"`);
        }
      }
      
      // Process Margin value if provided (second column)
      if (columns.length >= 2 && columns[1].trim()) {
        const marginValue = columns[1].trim().replace('%', '').replace(',', '.');
        if (!isNaN(parseFloat(marginValue))) {
          if (newEditingRevisions[dateStr]) {
            newEditingRevisions[dateStr].margin_rate = parseFloat(marginValue);
          } else {
            newEditingRevisions[dateStr] = {
              ...currentRevision,
              margin_rate: parseFloat(marginValue)
            };
          }
          console.log(`Successfully processed margin: ${marginValue} for date ${dateStr}`);
        }
      }
    });
    
    // Apply all changes at once
    if (Object.keys(newEditingRevisions).length > 0) {
      setEditingRevisions(prev => ({
        ...prev,
        ...newEditingRevisions
      }));
      setHasUnsavedChanges(true);
      console.log('Applied changes successfully');
    } else {
      console.log('No valid changes to apply');
    }
    
    console.log(`Processed ${processedCount} values out of ${rows.length} rows`);
    console.log('New editing revisions:', newEditingRevisions);
    return processedCount;
  };

  const handlePasteFromExcel = (e: React.ClipboardEvent, startDateStr: string) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    console.log('Pasting from Excel, data:', pastedData);
    console.log('Starting from date:', startDateStr);
    
    const startIndex = revisionDates.findIndex(date => date === startDateStr);
    console.log('Start index found:', startIndex);
    
    if (startIndex === -1) {
      console.error('Start date not found in revision dates');
      return;
    }
    
    // Check if it's just a single value (normal input) or multiple lines (bulk paste)
    const lines = pastedData.split('\n').filter(line => line.trim());
    if (lines.length === 1 && !pastedData.includes('\t')) {
      // Single value, handle as normal input
      const value = pastedData.trim().replace('%', '').replace(',', '.');
      if (!isNaN(parseFloat(value))) {
        handleRevisionChange(startDateStr, 'euribor_rate', value);
        return;
      }
    }
    
    // Multiple values, process as bulk paste
    const processedCount = processBulkPasteData(pastedData, startIndex);
    if (processedCount > 0) {
      alert(`✅ Se pegaron ${processedCount} valores del Euribor exitosamente desde ${formatDate(startDateStr)}`);
    } else {
      alert(`❌ No se pudieron procesar los datos. Verifica el formato.`);
    }
  };

  const handleBulkPaste = () => {
    if (!bulkPasteText.trim()) {
      alert('Por favor, pega los datos del Euribor en el área de texto');
      return;
    }
    
    const processedCount = processBulkPasteData(bulkPasteText, 0);
    if (processedCount > 0) {
      alert(`✅ Se procesaron ${processedCount} valores del Euribor exitosamente`);
      setBulkPasteText('');
      setShowBulkPasteArea(false);
    } else {
      alert('❌ No se pudieron procesar los datos. Verifica el formato.');
    }
  };

  const handleSaveRevisions = async () => {
    if (!mortgage || Object.keys(editingRevisions).length === 0) return;

    try {
      let savedCount = 0;
      const errors: string[] = [];

      for (const [dateStr, revision] of Object.entries(editingRevisions)) {
        try {
          const existingRevision = getRevisionForDate(dateStr);
          console.log(`Saving revision for ${dateStr}:`, { existingRevision, revision });
          
          if (existingRevision && existingRevision.id && existingRevision.id > 0) {
            // Try to update existing revision, but be ready to create if it fails
            try {
              await api.put(`/mortgage-details/${mortgage.id}/revisions/${existingRevision.id}`, {
                euribor_rate: revision.euribor_rate,
                margin_rate: revision.margin_rate,
                period_months: revision.period_months
              });
              console.log(`Successfully updated revision ${existingRevision.id} for ${dateStr}`);
            } catch (updateError: any) {
              if (updateError?.response?.status === 404) {
                console.log(`Revision ${existingRevision.id} not found, creating new one for ${dateStr}`);
                // If update fails with 404, create new revision instead
                await api.post(`/mortgage-details/${mortgage.id}/revisions`, {
                  effective_date: dateStr,
                  euribor_rate: revision.euribor_rate,
                  margin_rate: revision.margin_rate,
                  period_months: revision.period_months
                });
                console.log(`Successfully created new revision for ${dateStr}`);
              } else {
                throw updateError; // Re-throw if it's not a 404
              }
            }
          } else {
            // Create new revision
            await api.post(`/mortgage-details/${mortgage.id}/revisions`, {
              effective_date: dateStr,
              euribor_rate: revision.euribor_rate,
              margin_rate: revision.margin_rate,
              period_months: revision.period_months
            });
            console.log(`Successfully created new revision for ${dateStr}`);
          }
          savedCount++;
        } catch (error: any) {
          console.error(`Error saving revision for ${dateStr}:`, error);
          errors.push(`Error en ${dateStr}: ${error?.response?.data?.detail || error.message}`);
        }
      }

      if (errors.length > 0) {
        alert(`⚠️ Guardado completado con errores:\n\nGuardadas: ${savedCount} revisiones\n\nErrores:\n${errors.slice(0, 3).join('\n')}`);
      } else {
        alert(`✅ ¡Revisiones guardadas exitosamente!\n\nGuardadas: ${savedCount} revisiones`);
      }

      // Clear editing state and reload
      setEditingRevisions({});
      setHasUnsavedChanges(false);
      await loadMortgageData(mortgage.id);
      
    } catch (error) {
      console.error("Error saving revisions:", error);
      alert("❌ Error al guardar las revisiones");
    }
  };

  const handleDiscardChanges = () => {
    setEditingRevisions({});
    setHasUnsavedChanges(false);
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('es-ES');
  };

  const formatPercent = (rate: number) => {
    return `${rate.toFixed(2)}%`;
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!property) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">Propiedad no encontrada</p>
      </div>
    );
  }

  if (showNewMortgageForm) {
    return (
      <div className="space-y-6">
        <div>
          <nav className="text-sm text-gray-500 mb-2">
            <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
            <span className="mx-2">&gt;</span>
            <a href={`/financial-agent/property/${propertyId}`} className="hover:text-blue-600">
              {property.address}
            </a>
            <span className="mx-2">&gt;</span>
            <span>Nueva Hipoteca</span>
          </nav>
          <h1 className="text-3xl font-bold text-gray-900">Crear Hipoteca</h1>
          <p className="text-gray-600 mt-1">{property.address}</p>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <form onSubmit={handleCreateMortgage} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">ID del Préstamo</label>
                <input
                  type="text"
                  value={newMortgage.loan_id}
                  onChange={(e) => setNewMortgage({...newMortgage, loan_id: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ej: HIP-2024-001"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Entidad Bancaria</label>
                <input
                  type="text"
                  value={newMortgage.bank_entity}
                  onChange={(e) => setNewMortgage({...newMortgage, bank_entity: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  placeholder="Ej: Banco Santander"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Hipoteca</label>
                <select
                  value={newMortgage.mortgage_type}
                  onChange={(e) => setNewMortgage({...newMortgage, mortgage_type: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                >
                  <option value="Variable">Variable</option>
                  <option value="Fija">Fija</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Importe Inicial (€)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newMortgage.initial_amount}
                  onChange={(e) => setNewMortgage({...newMortgage, initial_amount: Number(e.target.value)})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Deuda Pendiente (€)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newMortgage.outstanding_balance}
                  onChange={(e) => setNewMortgage({...newMortgage, outstanding_balance: Number(e.target.value)})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Margen (%)</label>
                <input
                  type="number"
                  step="0.01"
                  value={newMortgage.margin_percentage}
                  onChange={(e) => setNewMortgage({...newMortgage, margin_percentage: Number(e.target.value)})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Inicio</label>
                <input
                  type="date"
                  value={newMortgage.start_date}
                  onChange={(e) => setNewMortgage({...newMortgage, start_date: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Fecha de Vencimiento</label>
                <input
                  type="date"
                  value={newMortgage.end_date}
                  onChange={(e) => setNewMortgage({...newMortgage, end_date: e.target.value})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Período de Revisión (meses)</label>
                <input
                  type="number"
                  value={newMortgage.review_period_months}
                  onChange={(e) => setNewMortgage({...newMortgage, review_period_months: Number(e.target.value)})}
                  className="w-full border border-gray-300 rounded-md px-3 py-2"
                  min="1"
                  required
                />
              </div>
            </div>

            <div className="flex justify-end space-x-4 pt-4">
              <button
                type="button"
                onClick={() => setShowNewMortgageForm(false)}
                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
              >
                Crear Hipoteca
              </button>
            </div>
          </form>
        </div>
      </div>
    );
  }

  if (!mortgage) {
    return (
      <div className="text-center py-8">
        <p className="text-gray-500">No hay información de hipoteca para esta propiedad</p>
        <button
          onClick={() => setShowNewMortgageForm(true)}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
        >
          Crear Hipoteca
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <nav className="text-sm text-gray-500 mb-2">
          <a href="/financial-agent" className="hover:text-blue-600">Agente Financiero</a>
          <span className="mx-2">&gt;</span>
          <a href={`/financial-agent/property/${propertyId}`} className="hover:text-blue-600">
            {property.address}
          </a>
          <span className="mx-2">&gt;</span>
          <span>Hipoteca</span>
        </nav>
        <h1 className="text-3xl font-bold text-gray-900">🏦 Gestión de Hipoteca</h1>
        <p className="text-gray-600 mt-1">{property.address}</p>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Cuota Actual</p>
            <p className="text-xl font-bold text-blue-600">{formatCurrency(summary.current_payment)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Saldo Pendiente</p>
            <p className="text-xl font-bold text-red-600">{formatCurrency(summary.current_balance)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Tipo Actual</p>
            <p className="text-xl font-bold text-purple-600">{formatPercent(summary.annual_rate)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-sm text-gray-600">Plazo Restante</p>
            <p className="text-xl font-bold text-gray-600">{Math.round(summary.loan_term_months/12)} años</p>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="bg-white rounded-lg shadow">
        <div className="border-b border-gray-200">
          <nav className="flex space-x-8 px-6">
            {[
              { key: "summary", label: "Resumen", icon: "📊" },
              { key: "schedule", label: "Cuadro", icon: "📋" },
              { key: "revisions", label: "Revisiones", icon: "📈" },
              { key: "settings", label: "Configuración", icon: "⚙️" }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key as any)}
                className={`py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                  activeTab === tab.key
                    ? "border-blue-500 text-blue-600"
                    : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                }`}
              >
                {tab.icon} {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="p-6">
          {/* Summary Tab */}
          {activeTab === "summary" && summary && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Información del Préstamo</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Entidad:</span>
                      <span className="font-medium">{mortgage.bank_entity || "No especificada"}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Tipo:</span>
                      <span className="font-medium">{mortgage.mortgage_type}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Importe inicial:</span>
                      <span className="font-medium">{formatCurrency(mortgage.initial_amount)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Fecha inicio:</span>
                      <span className="font-medium">{formatDate(mortgage.start_date)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Fecha vencimiento:</span>
                      <span className="font-medium">{formatDate(mortgage.end_date)}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-medium">Resumen Financiero</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total pagado:</span>
                      <span className="font-medium">{formatCurrency(summary.total_payments)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total intereses:</span>
                      <span className="font-medium text-red-600">{formatCurrency(summary.total_interest)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Total principal:</span>
                      <span className="font-medium text-green-600">{formatCurrency(summary.total_principal)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Duración total:</span>
                      <span className="font-medium">{summary.loan_term_months} meses</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Schedule Tab */}
          {activeTab === "schedule" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Cuadro de Amortización</h3>
                <button
                  onClick={() => setShowFullSchedule(!showFullSchedule)}
                  className="text-blue-600 hover:text-blue-800 text-sm"
                >
                  {showFullSchedule ? "Mostrar menos" : "Mostrar todo"}
                </button>
              </div>
              
              {schedule.length > 0 ? (
                <div className="overflow-x-auto">
                  <table className="w-full border-collapse border border-gray-200 text-sm">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="border border-gray-200 px-3 py-2 text-left">Mes</th>
                        <th className="border border-gray-200 px-3 py-2 text-right">Cuota</th>
                        <th className="border border-gray-200 px-3 py-2 text-right">Interés</th>
                        <th className="border border-gray-200 px-3 py-2 text-right">Principal</th>
                        <th className="border border-gray-200 px-3 py-2 text-right">Saldo</th>
                        <th className="border border-gray-200 px-3 py-2 text-right">Tipo</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(showFullSchedule ? schedule : schedule.slice(0, 12)).map((entry, index) => (
                        <tr key={index} className="hover:bg-gray-50">
                          <td className="border border-gray-200 px-3 py-2">
                            {formatDate(entry.month)}
                          </td>
                          <td className="border border-gray-200 px-3 py-2 text-right font-medium">
                            {formatCurrency(entry.payment)}
                          </td>
                          <td className="border border-gray-200 px-3 py-2 text-right text-red-600">
                            {formatCurrency(entry.interest)}
                          </td>
                          <td className="border border-gray-200 px-3 py-2 text-right text-green-600">
                            {formatCurrency(entry.principal)}
                          </td>
                          <td className="border border-gray-200 px-3 py-2 text-right">
                            {formatCurrency(entry.balance)}
                          </td>
                          <td className="border border-gray-200 px-3 py-2 text-right">
                            {formatPercent(entry.annual_rate)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No se pudo calcular el cuadro de amortización</p>
                </div>
              )}
            </div>
          )}

          {/* Revisions Tab */}
          {activeTab === "revisions" && (
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Calendario de Revisiones Euribor</h3>
                <div className="flex space-x-2">
                  {!showBulkPasteArea && (
                    <button 
                      onClick={() => setShowBulkPasteArea(true)}
                      className="bg-purple-600 text-white px-3 py-2 rounded-md hover:bg-purple-700 text-sm"
                      title="Pegar múltiples valores del Euribor de una vez"
                    >
                      📋 Pegar Múltiples
                    </button>
                  )}
                  {hasUnsavedChanges && (
                    <>
                      <button 
                        onClick={handleDiscardChanges}
                        className="bg-gray-600 text-white px-3 py-2 rounded-md hover:bg-gray-700 text-sm"
                      >
                        Descartar Cambios
                      </button>
                      <button 
                        onClick={handleSaveRevisions}
                        className="bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 text-sm"
                      >
                        ✅ Guardar Cambios
                      </button>
                    </>
                  )}
                </div>
              </div>
              
              {showBulkPasteArea && (
                <div className="bg-purple-50 border border-purple-200 rounded-md p-4 mb-4">
                  <div className="flex justify-between items-center mb-3">
                    <h4 className="font-medium text-purple-900">📋 Pegar Múltiples Valores del Euribor</h4>
                    <button 
                      onClick={() => {
                        setShowBulkPasteArea(false);
                        setBulkPasteText('');
                      }}
                      className="text-purple-600 hover:text-purple-800"
                    >
                      ✕
                    </button>
                  </div>
                  <p className="text-sm text-purple-800 mb-3">
                    Copia una columna de valores del Euribor desde Excel y pégala aquí. Se aplicarán en orden a todas las fechas de revisión.
                  </p>
                  <textarea
                    value={bulkPasteText}
                    onChange={(e) => setBulkPasteText(e.target.value)}
                    placeholder={`Pega aquí los valores del Euribor, uno por línea:
3.650
3.742
3.823
...`}
                    className="w-full h-32 px-3 py-2 border border-purple-300 rounded-md text-sm"
                  />
                  <div className="flex justify-end space-x-2 mt-3">
                    <button 
                      onClick={() => setBulkPasteText('')}
                      className="px-3 py-1 text-sm border border-gray-300 rounded-md hover:bg-gray-50"
                    >
                      Limpiar
                    </button>
                    <button 
                      onClick={handleBulkPaste}
                      className="px-3 py-1 text-sm bg-purple-600 text-white rounded-md hover:bg-purple-700"
                      disabled={!bulkPasteText.trim()}
                    >
                      Aplicar Valores
                    </button>
                  </div>
                </div>
              )}
              
              <div className="bg-blue-50 border border-blue-200 rounded-md p-3">
                <p className="text-sm text-blue-800">
                  📊 <strong>Tabla de Revisiones:</strong> Fechas generadas automáticamente cada {mortgage?.review_period_months} meses. Puedes:
                </p>
                <ul className="text-sm text-blue-700 mt-1 ml-4 list-disc">
                  <li>Editar valores directamente en la tabla</li>
                  <li>Usar "📋 Pegar Múltiples" para aplicar muchos valores de una vez</li>
                  <li>Hacer clic en un campo Euribor y pegar (Ctrl+V) desde esa posición</li>
                </ul>
              </div>
              
              {revisionDates.length > 0 ? (
                <div className="bg-white rounded-lg shadow overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-gray-50">
                        <tr>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Fecha Revisión
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Euribor (%)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Margen (%)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Tipo Total (%)
                          </th>
                          <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                            Estado
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-gray-200">
                        {revisionDates.map((dateStr, index) => {
                          const existingRevision = getRevisionForDate(dateStr);
                          const editingRevision = editingRevisions[dateStr];
                          const currentRevision = editingRevision || existingRevision;
                          
                          const euriborRate = currentRevision?.euribor_rate || null;
                          const marginRate = currentRevision?.margin_rate || mortgage?.margin_percentage || 0;
                          const totalRate = (euriborRate || 0) + marginRate;
                          const isDateInPast = new Date(dateStr) < new Date();
                          
                          return (
                            <tr key={index} className="hover:bg-gray-50">
                              <td className="px-4 py-3 text-sm font-medium text-gray-900">
                                {formatDate(dateStr)}
                              </td>
                              <td className="px-4 py-3">
                                <input
                                  type="number"
                                  step="0.001"
                                  value={euriborRate !== null ? euriborRate : ''}
                                  onChange={(e) => handleRevisionChange(dateStr, 'euribor_rate', e.target.value)}
                                  onPaste={(e) => handlePasteFromExcel(e, dateStr)}
                                  className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                                  placeholder="3.650"
                                  title="Haz clic y pega (Ctrl+V) datos de Excel aquí"
                                />
                              </td>
                              <td className="px-4 py-3">
                                <input
                                  type="number"
                                  step="0.001"
                                  value={marginRate}
                                  onChange={(e) => handleRevisionChange(dateStr, 'margin_rate', e.target.value)}
                                  className="w-24 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-blue-500 focus:border-blue-500"
                                  title="Margen del banco sobre el Euribor"
                                />
                              </td>
                              <td className="px-4 py-3 text-sm">
                                <span className={`font-medium ${
                                  euriborRate !== null ? 'text-blue-600' : 'text-gray-400'
                                }`}>
                                  {euriborRate !== null ? formatPercent(totalRate) : 'Pendiente'}
                                </span>
                              </td>
                              <td className="px-4 py-3 text-xs">
                                {euriborRate !== null ? (
                                  <span className={`px-2 py-1 rounded-full ${
                                    isDateInPast ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                                  }`}>
                                    {isDateInPast ? '✓ Completado' : '📅 Programado'}
                                  </span>
                                ) : (
                                  <span className="px-2 py-1 rounded-full bg-yellow-100 text-yellow-800">
                                    ⏳ Pendiente
                                  </span>
                                )}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-gray-500">
                  <p>No se pudo generar el calendario de revisiones</p>
                  <p className="text-sm mt-1">Verifica que la hipoteca tenga fechas de inicio y fin configuradas</p>
                </div>
              )}
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === "settings" && (
            <div className="space-y-6">
              <h3 className="text-lg font-medium">Configuración de la Hipoteca</h3>
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  ⚠️ La modificación de estos datos afectará todos los cálculos. Procede con precaución.
                </p>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Entidad Bancaria</label>
                  <input
                    type="text"
                    value={mortgage.bank_entity || ""}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    readOnly
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Hipoteca</label>
                  <input
                    type="text"
                    value={mortgage.mortgage_type}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    readOnly
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Deuda Pendiente Actual (€)</label>
                  <input
                    type="number"
                    value={mortgage.outstanding_balance}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    readOnly
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Margen (%)</label>
                  <input
                    type="number"
                    step="0.01"
                    value={mortgage.margin_percentage}
                    className="w-full border border-gray-300 rounded-md px-3 py-2"
                    readOnly
                  />
                </div>
              </div>

              <div className="pt-4">
                <button className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700">
                  Editar Configuración
                </button>
              </div>
            </div>
          )}

          {/* Removed ROI Tab - Moved to Analytics Dashboard */}
          {false && (
            <div className="space-y-6">
              <div className="flex justify-between items-center">
                <h3 className="text-lg font-medium">Análisis de ROI - {roiAnalysis.year}</h3>
                <a 
                  href="/financial-agent/euribor" 
                  className="text-blue-600 hover:text-blue-800 text-sm"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  📈 Gestionar Euribor
                </a>
              </div>

              {/* Financial Summary */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-500">
                  <p className="text-sm text-gray-600">Ingresos Totales</p>
                  <p className="text-xl font-bold text-green-600">{formatCurrency(roiAnalysis.financial_summary.total_income)}</p>
                  <p className="text-xs text-gray-500">Mensual: {formatCurrency(roiAnalysis.financial_summary.total_income / 12)}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-500">
                  <p className="text-sm text-gray-600">Gastos Totales</p>
                  <p className="text-xl font-bold text-red-600">{formatCurrency(roiAnalysis.financial_summary.total_expenses)}</p>
                  <p className="text-xs text-gray-500">Mensual: {formatCurrency(roiAnalysis.financial_summary.total_expenses / 12)}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-500">
                  <p className="text-sm text-gray-600">Cash Flow Neto</p>
                  <p className="text-xl font-bold text-blue-600">{formatCurrency(roiAnalysis.financial_summary.net_cash_flow)}</p>
                  <p className="text-xs text-gray-500">Mensual: {formatCurrency(roiAnalysis.financial_summary.monthly_cash_flow)}</p>
                </div>
                <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-500">
                  <p className="text-sm text-gray-600">Equity Invertido</p>
                  <p className="text-xl font-bold text-purple-600">{formatCurrency(roiAnalysis.investment_summary.total_equity_invested)}</p>
                </div>
              </div>

              {/* ROI Metrics */}
              <div className="bg-white rounded-lg shadow p-6">
                <h4 className="text-lg font-medium mb-4">Métricas de ROI</h4>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-blue-600">{roiAnalysis.roi_metrics.cash_on_cash_roi.toFixed(1)}%</div>
                    <div className="text-sm text-gray-600 mt-1">Cash-on-Cash ROI</div>
                    <div className="text-xs text-gray-500 mt-2">
                      Basado en {formatCurrency(roiAnalysis.investment_summary.total_equity_invested)} invertidos
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-600">{roiAnalysis.roi_metrics.purchase_price_roi.toFixed(1)}%</div>
                    <div className="text-sm text-gray-600 mt-1">ROI sobre Precio Compra</div>
                    <div className="text-xs text-gray-500 mt-2">
                      Basado en {formatCurrency(roiAnalysis.investment_summary.purchase_price || 0)}
                    </div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-purple-600">{roiAnalysis.roi_metrics.cap_rate.toFixed(1)}%</div>
                    <div className="text-sm text-gray-600 mt-1">Cap Rate</div>
                    <div className="text-xs text-gray-500 mt-2">
                      Basado en valoración actual de {formatCurrency(roiAnalysis.investment_summary.current_value || 0)}
                    </div>
                  </div>
                </div>
              </div>

              {/* Investment Breakdown */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="bg-white rounded-lg shadow p-6">
                  <h4 className="text-lg font-medium mb-4">Desglose de Inversión</h4>
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Precio de Compra:</span>
                      <span className="font-medium">{formatCurrency(roiAnalysis.investment_summary.purchase_price || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Entrada/Enganche:</span>
                      <span className="font-medium">{formatCurrency(roiAnalysis.investment_summary.down_payment || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Gastos Adquisición:</span>
                      <span className="font-medium">{formatCurrency(roiAnalysis.investment_summary.acquisition_costs || 0)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Costos Renovación:</span>
                      <span className="font-medium">{formatCurrency(roiAnalysis.investment_summary.renovation_costs || 0)}</span>
                    </div>
                    <div className="border-t pt-2 flex justify-between font-bold">
                      <span>Total Equity Invertido:</span>
                      <span className="text-purple-600">{formatCurrency(roiAnalysis.investment_summary.total_equity_invested)}</span>
                    </div>
                  </div>
                </div>

                {roiAnalysis.mortgage_info && (
                  <div className="bg-white rounded-lg shadow p-6">
                    <h4 className="text-lg font-medium mb-4">Información Hipoteca</h4>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Saldo Pendiente:</span>
                        <span className="font-medium text-red-600">{formatCurrency(roiAnalysis.mortgage_info.outstanding_balance)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Pagos Anuales:</span>
                        <span className="font-medium">{formatCurrency(roiAnalysis.mortgage_info.annual_payments)}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Cuota Mensual:</span>
                        <span className="font-medium">{formatCurrency(roiAnalysis.mortgage_info.monthly_payment)}</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
              
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                <p className="text-sm text-yellow-800">
                  📊 <strong>Interpretación:</strong> El Cash-on-Cash ROI muestra el retorno sobre tu inversión inicial. El Cap Rate indica la rentabilidad de la propiedad independientemente del financiamiento. Ambos se calculan en base a los movimientos financieros registrados para {roiAnalysis.year}.
                </p>
              </div>
            </div>
          )}
        </div>
      </div>

    </div>
  );
}