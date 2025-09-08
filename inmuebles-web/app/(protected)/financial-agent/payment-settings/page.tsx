"use client";

import { useState, useEffect } from 'react';
import api from '@/lib/api';

interface PaymentRule {
  id?: number;
  property_id?: number;
  tenant_name?: string;
  payment_start_day: number;
  payment_end_day: number;
  allow_previous_month_end: boolean;
  previous_month_end_days: number;
  overdue_grace_days: number;
  warning_days: number;
  critical_days: number;
  rule_name: string;
  is_active: boolean;
}

interface PropertyTenant {
  property_id: number;
  property_address: string;
  tenants: string[];
}

export default function PaymentSettingsPage() {
  const [rules, setRules] = useState<PaymentRule[]>([]);
  const [propertiesAndTenants, setPropertiesAndTenants] = useState<PropertyTenant[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [editingRule, setEditingRule] = useState<PaymentRule | null>(null);
  const [loading, setLoading] = useState(true);

  const [formData, setFormData] = useState<PaymentRule>({
    property_id: undefined,
    tenant_name: undefined,
    payment_start_day: 1,
    payment_end_day: 5,
    allow_previous_month_end: false,
    previous_month_end_days: 0,
    overdue_grace_days: 15,
    warning_days: 30,
    critical_days: 60,
    rule_name: '',
    is_active: true
  });

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [rulesResponse, propertiesResponse] = await Promise.all([
        api.get('/payment-rules/'),
        api.get('/payment-rules/properties-and-tenants')
      ]);
      
      setRules(rulesResponse.data);
      setPropertiesAndTenants(propertiesResponse.data);
      
      // Create default rule if none exist
      if (rulesResponse.data.length === 0) {
        await api.get('/payment-rules/default-rule');
        const updatedRules = await api.get('/payment-rules/');
        setRules(updatedRules.data);
      }
    } catch (error) {
      console.error('Error loading payment rules:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (editingRule) {
        await api.put(`/payment-rules/${editingRule.id}`, formData);
      } else {
        await api.post('/payment-rules/', formData);
      }
      
      await loadData();
      resetForm();
    } catch (error) {
      console.error('Error saving payment rule:', error);
      alert('Error al guardar la regla de pago');
    }
  };

  const handleDelete = async (ruleId: number) => {
    if (confirm('¿Estás seguro de que quieres eliminar esta regla?')) {
      try {
        await api.delete(`/payment-rules/${ruleId}`);
        await loadData();
      } catch (error) {
        console.error('Error deleting payment rule:', error);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      property_id: undefined,
      tenant_name: undefined,
      payment_start_day: 1,
      payment_end_day: 5,
      allow_previous_month_end: false,
      previous_month_end_days: 0,
      overdue_grace_days: 15,
      warning_days: 30,
      critical_days: 60,
      rule_name: '',
      is_active: true
    });
    setShowCreateForm(false);
    setEditingRule(null);
  };

  const startEdit = (rule: PaymentRule) => {
    setFormData(rule);
    setEditingRule(rule);
    setShowCreateForm(true);
  };

  if (loading) {
    return <div className="p-6">Cargando reglas de pago...</div>;
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Configuración de Pagos</h1>
        <p className="text-gray-600">
          Configura las reglas para determinar cuándo un inquilino se considera en impago
        </p>
      </div>

      {/* Existing Rules */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Reglas Actuales</h2>
          <button
            onClick={() => setShowCreateForm(true)}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
          >
            + Nueva Regla
          </button>
        </div>

        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Regla
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Propiedad/Inquilino
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Ventana de Pago
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Días Impago
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Acciones
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {rules.map((rule) => (
                <tr key={rule.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {rule.rule_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {rule.property_id ? 
                      `Propiedad ${rule.property_id}${rule.tenant_name ? ` - ${rule.tenant_name}` : ''}` : 
                      rule.tenant_name ? `${rule.tenant_name} (Global)` : 'Todas las propiedades'
                    }
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    Días {rule.payment_start_day}-{rule.payment_end_day}
                    {rule.allow_previous_month_end && (
                      <div className="text-xs text-blue-600">
                        + {rule.previous_month_end_days} días del mes anterior
                      </div>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <span className="text-orange-600 font-medium">{rule.overdue_grace_days} días</span>
                    <br />
                    <span className="text-xs text-gray-400">
                      Aviso: {rule.warning_days}d, Crítico: {rule.critical_days}d
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs rounded-full ${
                      rule.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                    }`}>
                      {rule.is_active ? 'Activa' : 'Inactiva'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    <button
                      onClick={() => startEdit(rule)}
                      className="text-blue-600 hover:text-blue-900 mr-3"
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => rule.id && handleDelete(rule.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      Eliminar
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Create/Edit Form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-4">
            {editingRule ? 'Editar Regla de Pago' : 'Nueva Regla de Pago'}
          </h3>

          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Rule Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre de la Regla
                </label>
                <input
                  type="text"
                  value={formData.rule_name}
                  onChange={(e) => setFormData({...formData, rule_name: e.target.value})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                  required
                />
              </div>

              {/* Property Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Propiedad (opcional)
                </label>
                <select
                  value={formData.property_id || ''}
                  onChange={(e) => setFormData({
                    ...formData, 
                    property_id: e.target.value ? Number(e.target.value) : undefined,
                    tenant_name: undefined // Reset tenant when property changes
                  })}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Todas las propiedades</option>
                  {propertiesAndTenants.map((prop) => (
                    <option key={prop.property_id} value={prop.property_id}>
                      {prop.property_address}
                    </option>
                  ))}
                </select>
              </div>

              {/* Tenant Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Inquilino (opcional)
                </label>
                <select
                  value={formData.tenant_name || ''}
                  onChange={(e) => setFormData({...formData, tenant_name: e.target.value || undefined})}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2"
                >
                  <option value="">Todos los inquilinos</option>
                  {formData.property_id && propertiesAndTenants
                    .find(p => p.property_id === formData.property_id)?.tenants
                    .map((tenant) => (
                      <option key={tenant} value={tenant}>
                        {tenant}
                      </option>
                    ))
                  }
                </select>
              </div>

              {/* Active Status */}
              <div>
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">Regla activa</span>
                </label>
              </div>
            </div>

            {/* Payment Window */}
            <div>
              <h4 className="text-md font-semibold text-gray-900 mb-3">Ventana de Pago del Mes</h4>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Día inicio (1-31)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={formData.payment_start_day}
                    onChange={(e) => setFormData({...formData, payment_start_day: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Día fin (1-31)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="31"
                    value={formData.payment_end_day}
                    onChange={(e) => setFormData({...formData, payment_end_day: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                </div>
              </div>
              
              {/* Previous Month End Configuration */}
              <div className="mt-4">
                <label className="flex items-center mb-3">
                  <input
                    type="checkbox"
                    checked={formData.allow_previous_month_end}
                    onChange={(e) => setFormData({
                      ...formData, 
                      allow_previous_month_end: e.target.checked,
                      previous_month_end_days: e.target.checked ? formData.previous_month_end_days : 0
                    })}
                    className="mr-2"
                  />
                  <span className="text-sm font-medium text-gray-700">
                    Permitir pagos desde finales del mes anterior
                  </span>
                </label>
                
                {formData.allow_previous_month_end && (
                  <div className="ml-6">
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Días desde final del mes anterior (0-10)
                    </label>
                    <input
                      type="number"
                      min="0"
                      max="10"
                      value={formData.previous_month_end_days}
                      onChange={(e) => setFormData({...formData, previous_month_end_days: Number(e.target.value)})}
                      className="w-32 border border-gray-300 rounded-lg px-3 py-2"
                    />
                    <p className="text-xs text-gray-500 mt-1">
                      Ej: Si pones 3, se aceptarán pagos desde 3 días antes del fin del mes anterior
                    </p>
                  </div>
                )}
              </div>
            </div>

            {/* Overdue Thresholds */}
            <div>
              <h4 className="text-md font-semibold text-gray-900 mb-3">Configuración de Impagos</h4>
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Días para considerar impago
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.overdue_grace_days}
                    onChange={(e) => setFormData({...formData, overdue_grace_days: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Días después de la ventana de pago antes de marcar como impago
                  </p>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Días para aviso
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.warning_days}
                    onChange={(e) => setFormData({...formData, warning_days: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Días para crítico
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={formData.critical_days}
                    onChange={(e) => setFormData({...formData, critical_days: Number(e.target.value)})}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2"
                    required
                  />
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="flex justify-end space-x-3">
              <button
                type="button"
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Cancelar
              </button>
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                {editingRule ? 'Actualizar' : 'Crear'} Regla
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Help Section */}
      <div className="mt-8 bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-900 mb-3">¿Cómo funcionan las reglas de pago?</h3>
        <ul className="text-blue-800 space-y-2">
          <li><strong>Ventana de pago:</strong> Define qué días del mes se considera normal recibir el pago</li>
          <li><strong>Días del mes anterior:</strong> Permite incluir los últimos días del mes anterior como válidos para el pago (útil cuando el inquilino paga por adelantado)</li>
          <li><strong>Días para impago:</strong> Después de este número de días sin pago, se muestra como impagado</li>
          <li><strong>Prioridad:</strong> Las reglas específicas (propiedad + inquilino) tienen prioridad sobre las globales</li>
          <li><strong>Ejemplo:</strong> Ventana 1-5 días + 3 días del mes anterior + 15 días de gracia = los pagos son válidos desde el día 28 del mes anterior hasta el día 20 del mes actual</li>
        </ul>
      </div>
    </div>
  );
}