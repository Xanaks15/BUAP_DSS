import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const FilterPanel = ({ isOpen, onClose, currentFilters, onApply, onClear }) => {
    const [localFilters, setLocalFilters] = useState(currentFilters);

    // Sync local state when popover opens or currentFilters changes
    useEffect(() => {
        if (isOpen) {
            setLocalFilters(currentFilters);
        }
    }, [isOpen, currentFilters]);

    const handleChange = (key, value) => {
        setLocalFilters(prev => ({ ...prev, [key]: value }));
    };

    const handleApply = () => {
        onApply(localFilters);
    };

    if (!isOpen) return null;

    return (
        <div className="absolute right-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-xl p-4 z-20 animate-fade-in-down">
            <div className="flex justify-between items-center mb-4 border-b border-gray-100 pb-2">
                <h3 className="font-semibold text-gray-800">Filtros Avanzados</h3>
                <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
                    <X size={18} />
                </button>
            </div>

            <div className="space-y-4">
                {/* Status */}
                <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Estado</label>
                    <select
                        className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        value={localFilters.status}
                        onChange={(e) => handleChange('status', e.target.value)}
                    >
                        <option value="all">Todos</option>
                        <option value="activo">Activo</option>
                        <option value="completado">Completado</option>
                        <option value="cancelado">Cancelado</option>
                    </select>
                </div>

                {/* Type */}
                <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Tipo de Proyecto</label>
                    <select
                        className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        value={localFilters.type}
                        onChange={(e) => handleChange('type', e.target.value)}
                    >
                        <option value="all">Todos</option>
                        <option value="Desarrollo Web">Desarrollo Web</option>
                        <option value="Aplicación Móvil">Aplicación Móvil</option>
                        <option value="Software Empresarial">Software Empresarial</option>
                        <option value="Infraestructura Cloud">Infraestructura Cloud</option>
                        <option value="Consultoría Técnica">Consultoría Técnica</option>
                    </select>
                </div>

                {/* Client */}
                <div>
                    <label className="block text-xs font-medium text-gray-500 mb-1">Cliente</label>
                    <select
                        className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                        value={localFilters.client}
                        onChange={(e) => handleChange('client', e.target.value)}
                    >
                        <option value="all">Todos</option>
                        <option value="cliente1">Cliente A</option>
                        <option value="cliente2">Cliente B</option>
                        <option value="cliente3">Cliente C</option>
                    </select>
                </div>

                {/* Date Range */}
                <div className="grid grid-cols-2 gap-2">
                    <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">Desde</label>
                        <input
                            type="date"
                            className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            value={localFilters.startDate}
                            onChange={(e) => handleChange('startDate', e.target.value)}
                        />
                    </div>
                    <div>
                        <label className="block text-xs font-medium text-gray-500 mb-1">Hasta</label>
                        <input
                            type="date"
                            className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            value={localFilters.endDate}
                            onChange={(e) => handleChange('endDate', e.target.value)}
                        />
                    </div>
                </div>
            </div>

            <div className="flex justify-between items-center mt-6 pt-4 border-t border-gray-100">
                <button
                    onClick={onClear}
                    className="text-sm text-gray-500 hover:text-gray-700 underline"
                >
                    Limpiar
                </button>
                <button
                    onClick={handleApply}
                    className="bg-blue-600 text-white text-sm px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                    Aplicar Filtros
                </button>
            </div>
        </div>
    );
};

export default FilterPanel;
