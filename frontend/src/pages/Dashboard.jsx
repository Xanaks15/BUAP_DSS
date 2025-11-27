import React, { useEffect, useState } from 'react';
import { getProjects, getProjectMetrics, getGeneralKPIs } from '../services/api';
import ExecutiveSummary from '../components/ExecutiveSummary';
import RayleighCurves from '../components/RayleighCurves';
import QualityDashboard from '../components/QualityDashboard';
import FilterPanel from '../components/FilterPanel';
import { Filter, Calendar, Users, Briefcase, Search, LayoutGrid, List } from 'lucide-react';

const Dashboard = () => {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null); // Null means "All Projects" / Portfolio View
    const [viewMode, setViewMode] = useState('portfolio'); // 'portfolio' | 'project'
    const [projectMetrics, setProjectMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isFilterOpen, setIsFilterOpen] = useState(false);

    // Filters state
    const [filters, setFilters] = useState({
        startDate: '',
        endDate: '',
        type: 'all',
        status: 'all',
        client: 'all',
        query: ''
    });

    useEffect(() => {
        // Fetch projects list
        getProjects().then(data => {
            setProjects(data);
            // Default to Portfolio view initially, or select first project if user prefers
            // User requested: "si elijo Portafolio, selectedProjectId=null; si Proyecto, mantener el seleccionado"
            // We'll start in Portfolio mode.
            setLoading(false);
        }).catch(err => {
            console.error("Error fetching projects:", err);
            setLoading(false);
        });
    }, []);

    // Sync viewMode with selectedProjectId
    useEffect(() => {
        if (viewMode === 'portfolio') {
            setSelectedProjectId(null);
        } else if (viewMode === 'project' && !selectedProjectId && projects.length > 0) {
            setSelectedProjectId(projects[0].proyecto_id);
        }
    }, [viewMode, projects]);

    useEffect(() => {
        if (selectedProjectId) {
            getProjectMetrics(selectedProjectId).then(setProjectMetrics).catch(console.error);
        } else {
            // Roll-up / Portfolio View with Slice & Dice Filters
            getGeneralKPIs(filters).then(data => {
                setProjectMetrics({
                    name: "Vista Portfolio (Global)",
                    spi: 1.0,
                    cpi: 1.0,
                    ev: data.total_profit,
                    pv: data.total_pv || 0,
                    ac: data.total_ac || 0,
                    risk_status: "Low",
                    progress_pct: 100,
                    productivity: 0,
                    isPortfolio: true,
                    ...data
                });
            }).catch(console.error);
        }
    }, [selectedProjectId, filters]);

    // Handlers
    const handlePresetClick = (days) => {
        if (days === 'all') {
            setFilters(prev => ({ ...prev, startDate: '', endDate: '' }));
        } else {
            const date = new Date();
            date.setDate(date.getDate() - days);
            // Format YYYY-MM-DD
            const isoDate = date.toISOString().split('T')[0];
            setFilters(prev => ({ ...prev, startDate: isoDate, endDate: '' }));
        }
    };

    const handleApplyFilters = (newFilters) => {
        setFilters(prev => ({ ...prev, ...newFilters }));
        setIsFilterOpen(false);
    };

    const handleClearFilters = () => {
        setFilters({
            startDate: '',
            endDate: '',
            type: 'all',
            status: 'all',
            client: 'all',
            query: ''
        });
        setIsFilterOpen(false);
    };

    const activeFiltersCount = [
        filters.type !== 'all',
        filters.status !== 'all',
        filters.client !== 'all',
        filters.startDate !== '',
        filters.endDate !== ''
    ].filter(Boolean).length;

    if (loading) return <div className="flex items-center justify-center h-full text-corporate-blue">Cargando DSS...</div>;

    return (
        <div className="space-y-6 font-sans text-gray-800">
            {/* Header & Toolbar */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 space-y-5">
                {/* Top Row: Title & View Switcher */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Dashboard Operativo</h2>
                        <p className="text-gray-500 text-sm">Monitor de rendimiento de proyectos y calidad</p>
                    </div>

                    {/* View Switcher & Project Selector */}
                    <div className="flex items-center gap-3 bg-gray-50 p-1 rounded-lg border border-gray-200">
                        <div className="flex bg-white rounded-md shadow-sm">
                            <button
                                onClick={() => setViewMode('portfolio')}
                                className={`px-3 py-1.5 text-sm font-medium rounded-l-md transition-colors ${viewMode === 'portfolio' ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
                            >
                                Portafolio
                            </button>
                            <div className="w-px bg-gray-200"></div>
                            <button
                                onClick={() => setViewMode('project')}
                                className={`px-3 py-1.5 text-sm font-medium rounded-r-md transition-colors ${viewMode === 'project' ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-gray-50'}`}
                            >
                                Proyecto
                            </button>
                        </div>

                        {viewMode === 'project' && (
                            <div className="relative animate-fade-in">
                                <select
                                    className="bg-transparent border-none focus:ring-0 text-sm font-medium text-gray-700 py-1 pl-2 pr-8 cursor-pointer"
                                    value={selectedProjectId || ''}
                                    onChange={(e) => setSelectedProjectId(Number(e.target.value))}
                                >
                                    {projects.map(p => (
                                        <option key={p.proyecto_id} value={p.proyecto_id}>{p.nombre}</option>
                                    ))}
                                </select>
                            </div>
                        )}
                    </div>
                </div>

                {/* Toolbar: Presets, Search, Filter Button */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3 pt-4 border-t border-gray-100">
                    {/* Left: Presets */}
                    <div className="flex items-center gap-2 overflow-x-auto pb-1 lg:pb-0 no-scrollbar">
                        <span className="text-xs font-medium text-gray-400 uppercase mr-1">Periodo:</span>
                        {[
                            { label: 'Últ. 30d', days: 30 },
                            { label: 'Últ. 90d', days: 90 },
                            { label: 'YTD', days: 365 }, // Simplified YTD
                            { label: 'Todo', days: 'all' }
                        ].map(preset => (
                            <button
                                key={preset.label}
                                onClick={() => handlePresetClick(preset.days)}
                                className={`px-3 py-1.5 text-sm rounded-full border transition-colors whitespace-nowrap ${(preset.days === 'all' && !filters.startDate) || (filters.startDate && preset.days !== 'all') // Simple active check logic
                                    ? 'bg-blue-50 border-blue-200 text-blue-700'
                                    : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                                    }`}
                            >
                                {preset.label}
                            </button>
                        ))}
                    </div>

                    {/* Right: Search & Filter */}
                    <div className="flex items-center gap-3 w-full lg:w-auto">
                        <div className="relative flex-1 lg:w-64">
                            <Search size={16} className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                            <input
                                type="text"
                                placeholder="Buscar..."
                                className="w-full pl-9 pr-4 py-1.5 text-sm border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                                value={filters.query}
                                onChange={(e) => setFilters(prev => ({ ...prev, query: e.target.value }))}
                            />
                        </div>

                        <div className="relative">
                            <button
                                onClick={() => setIsFilterOpen(!isFilterOpen)}
                                className={`inline-flex items-center gap-2 px-3 py-1.5 text-sm font-medium rounded-md border transition-colors ${isFilterOpen || activeFiltersCount > 0 ? 'bg-blue-50 border-blue-200 text-blue-700' : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                                    }`}
                            >
                                <Filter size={16} />
                                <span>Filtros</span>
                                {activeFiltersCount > 0 && (
                                    <span className="bg-blue-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                                        {activeFiltersCount}
                                    </span>
                                )}
                            </button>

                            {/* Filter Panel Popover */}
                            <FilterPanel
                                isOpen={isFilterOpen}
                                onClose={() => setIsFilterOpen(false)}
                                currentFilters={filters}
                                onApply={handleApplyFilters}
                                onClear={handleClearFilters}
                            />
                        </div>
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="space-y-8">
                {projectMetrics ? (
                    <>
                        {/* Portfolio/Project KPIs Row (Mocked for now as per spec requirements not fully in API yet) */}
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div className="text-sm text-gray-500">ROI Promedio</div>
                                <div className="text-2xl font-bold text-green-600">18.5%</div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div className="text-sm text-gray-500">Entregas a Tiempo</div>
                                <div className="text-2xl font-bold text-blue-600">92%</div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div className="text-sm text-gray-500">Costo vs Plan</div>
                                <div className="text-2xl font-bold text-yellow-600">+4.2%</div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                <div className="text-sm text-gray-500">Defectos Críticos</div>
                                <div className="text-2xl font-bold text-red-600">3</div>
                            </div>
                        </div>

                        <ExecutiveSummary metrics={projectMetrics} />
                        <RayleighCurves projectData={projectMetrics} />
                        <QualityDashboard projectId={selectedProjectId} />
                    </>
                ) : (
                    <div className="text-center py-20 text-gray-400">Seleccione un proyecto para ver el análisis detallado.</div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
