"use client";
import { useEffect, useState } from "react";
import api from "@/lib/api";
import ResponsiveLayout from "@/components/ResponsiveLayout";
import Link from "next/link";
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

export default function PropertiesPage() {
  const [items, setItems] = useState<Property[]>([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string>("");
  
  // Delete confirmation state
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [propertyToDelete, setPropertyToDelete] = useState<Property | null>(null);
  const [deleting, setDeleting] = useState(false);

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

  // Photo upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [photoPreview, setPhotoPreview] = useState<string | null>(null);
  
  // Photo editing states
  const [showPhotoEditModal, setShowPhotoEditModal] = useState(false);
  const [editingProperty, setEditingProperty] = useState<Property | null>(null);
  const [editingPhotoFile, setEditingPhotoFile] = useState<File | null>(null);
  const [editingPhotoPreview, setEditingPhotoPreview] = useState<string | null>(null);
  const [uploadingPhoto, setUploadingPhoto] = useState(false);

  async function load() {
    try {
      const r = await api.get<Property[]>("/properties");
      setItems(r.data);
    } catch (error) {
      console.error("Error loading properties:", error);
    }
  }

  useEffect(() => { load(); }, []);

  async function createProperty(e: React.FormEvent) {
    e.preventDefault();
    setErr(""); setLoading(true);
    
    try {
      let photoUrl = null;
      
      // Upload photo if selected
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
      
      // Reset form
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
      await load();
    } catch (e: any) {
      setErr(e?.response?.data?.detail ?? "Error creando propiedad");
    } finally { 
      setLoading(false); 
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-ES', {
      style: 'currency',
      currency: 'EUR'
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('es-ES');
  };

  const handleDeleteClick = (property: Property) => {
    setPropertyToDelete(property);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    if (!propertyToDelete) return;
    
    setDeleting(true);
    try {
      await api.delete(`/properties/${propertyToDelete.id}`);
      await load(); // Reload the list
      setShowDeleteConfirm(false);
      setPropertyToDelete(null);
    } catch (error: any) {
      console.error("Error deleting property:", error);
      alert(error?.response?.data?.detail || "Error al eliminar la propiedad");
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
      
      // Create preview
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

  // Photo editing functions
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
      // Upload photo
      const formData = new FormData();
      formData.append('file', editingPhotoFile);
      
      const photoResponse = await api.post('/uploads/photo', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Update property with new photo URL
      await api.put(`/properties/${editingProperty.id}`, {
        ...editingProperty,
        photo: photoResponse.data.url
      });
      
      // Refresh properties and close modal
      await load();
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

  const actions = (
    <button
      onClick={() => setShowCreateForm(true)}
      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 flex items-center space-x-2"
    >
      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
      </svg>
      <span>Nueva Propiedad</span>
    </button>
  );

  return (
    <ResponsiveLayout 
      title="Gestión de Propiedades"
      subtitle="Administra tu portafolio inmobiliario"
      actions={actions}
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
      {/* Create Property Form Modal */}
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

      {/* Properties List */}
      <div className="bg-white shadow rounded-lg">
        {items.length === 0 ? (
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
              </svg>
            </div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No hay propiedades</h3>
            <p className="text-gray-500 mb-6">
              Comienza agregando tu primera propiedad al portafolio
            </p>
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
          <>
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-medium text-gray-900">
                Listado de Propiedades ({items.length})
              </h2>
            </div>
            
            <div className="grid gap-4 p-4">
              {items.map((property) => (
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
                      
                      {/* Delete button */}
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
          </>
        )}
      </div>

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
    </ResponsiveLayout>
  );
}
