import React, { useEffect, useState } from 'react';
import { getProjects, getProjectMetrics, getGeneralKPIs } from '../services/api';
import ExecutiveSummary from '../components/ExecutiveSummary';
import RayleighCurves from '../components/RayleighCurves';
import QualityDashboard from '../components/QualityDashboard';
import FilterPanel from '../components/FilterPanel';
import { Filter, Search, CheckCircle, AlertTriangle, TrendingUp, DollarSign, Clock, Users, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

const Dashboard = () => {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null); // Null means "All Projects" / Portfolio View
    const [viewMode, setViewMode] = useState('portfolio'); // 'portfolio' | 'project'
    const [projectMetrics, setProjectMetrics] = useState(null);
    const [loading, setLoading] = useState(true);
    const [metricsLoading, setMetricsLoading] = useState(false);
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
            setLoading(false);
        }).catch(err => {
            console.error("Error fetching projects:", err);
            setLoading(false);
        });
    }, []);

    // Sync viewMode with selectedProjectId (which now acts as selectedType in project mode)
    useEffect(() => {
        if (viewMode === 'portfolio') {
            setSelectedProjectId(null);
        } else if (viewMode === 'project' && !selectedProjectId) {
            setSelectedProjectId('Desarrollo Web');
        }
    }, [viewMode]);

    useEffect(() => {
        setMetricsLoading(true);

        // If viewMode is 'project', we treat selectedProjectId as the selected TYPE string
        // If viewMode is 'portfolio', we use the global filters

        if (viewMode === 'project' && selectedProjectId) {
            // Fetch aggregated metrics for the selected TYPE
            // We reuse getGeneralKPIs but force the type filter
            const typeFilter = { ...filters, type: selectedProjectId };

            getGeneralKPIs(typeFilter).then(data => {
                // Calculate SPI and CPI from aggregated totals
                const total_ev = data.total_ev || 0;
                const total_pv = data.total_pv || 0;
                const total_ac = data.total_ac || 0;

                const spi = total_pv > 0 ? total_ev / total_pv : 0;
                const cpi = total_ac > 0 ? total_ev / total_ac : 0;

                setProjectMetrics({
                    name: `Tipo: ${selectedProjectId}`,
                    spi: parseFloat(spi.toFixed(2)),
                    cpi: parseFloat(cpi.toFixed(2)),
                    ev: total_ev,
                    tasks_completed_pct: data.tasks_completed_pct || 0,
                    tasks_delayed_pct: data.tasks_delayed_pct || 0,
                    tasks_not_completed_pct: data.tasks_not_completed_pct || 0,
                    hours_real_vs_planned_pct: data.hours_real_vs_planned_pct || 0,
                    cost_real_vs_planned_pct: data.cost_real_vs_planned_pct || 0,
                    avg_employees_assigned: data.avg_employees_assigned || 0,
                    projects_by_status: data.projects_by_status || {},

                    // New metrics from backend
                    avg_roi: data.avg_roi || 0,
                    delay_days: data.avg_delay_days || 0,
                    on_time_projects_pct: data.on_time_projects_pct || 0,
                    critical_defects: data.critical_defects || 0,
                    total_defects: data.total_defects || 0,
                    defects_by_phase: data.defects_by_phase || {},
                    defects_by_severity: data.defects_by_severity || {},

                    // Map specific fields expected by ExecutiveSummary
                    total_hours_planned: data.total_hours_planned,
                    total_hours_real: data.total_hours_real
                });
                setMetricsLoading(false);
            }).catch(err => {
                console.error(err);
                setMetricsLoading(false);
            });
        } else {
            // Roll-up / Portfolio View with Slice & Dice Filters
            getGeneralKPIs(filters).then(data => {
                setProjectMetrics({
                    name: "Vista Portfolio (Global)",
                    spi: 1.0, // Portfolio usually doesn't have single SPI/CPI, or it's 1.0 baseline
                    cpi: 1.0,
                    ev: data.total_ev || 0,
                    pv: data.total_pv || 0,
                    ac: data.total_ac || 0,
                    risk_status: data.risk_status || "Low",
                    progress_pct: data.tasks_completed_pct || 0,
                    productivity: data.productivity || 0,
                    isPortfolio: true,
                    // New metrics from backend
                    avg_roi: data.avg_roi || 0,
                    delay_days: data.avg_delay_days || 0,
                    on_time_projects_pct: data.on_time_projects_pct || 0,
                    critical_defects: data.critical_defects || 0,
                    total_defects: data.total_defects || 0,
                    defects_by_phase: data.defects_by_phase || {},
                    defects_by_severity: data.defects_by_severity || {},
                    tasks_completed_pct: data.tasks_completed_pct || 0,
                    tasks_delayed_pct: data.tasks_delayed_pct || 0,
                    tasks_not_completed_pct: data.tasks_not_completed_pct || 0,
                    hours_real_vs_planned_pct: data.hours_real_vs_planned_pct || 0,
                    cost_real_vs_planned_pct: data.cost_real_vs_planned_pct || 0,
                    avg_employees_assigned: data.avg_employees_assigned || 0,
                    projects_by_status: data.projects_by_status || {},

                    total_hours_planned: data.total_hours_planned,
                    total_hours_real: data.total_hours_real
                });
                setMetricsLoading(false);
            }).catch(err => {
                console.error(err);
                setMetricsLoading(false);
            });
        }
    }, [selectedProjectId, filters, viewMode]);

    // Handlers
    const handlePresetClick = (days) => {
        if (days === 'all') {
            setFilters(prev => ({ ...prev, startDate: '', endDate: '' }));
        } else {
            const date = new Date();
            date.setDate(date.getDate() - days);
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

    if (loading) return (
        <div className="flex items-center justify-center h-screen">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
        </div>
    );

    // Helper to calculate Cost vs Plan %
    const calculateCostVsPlan = (metrics) => {
        if (!metrics || !metrics.pv || metrics.pv === 0) return 0;
        const diff = metrics.ac - metrics.pv;
        const pct = (diff / metrics.pv) * 100;
        return pct.toFixed(1);
    };

    const costVsPlanVal = parseFloat(calculateCostVsPlan(projectMetrics));
    const isOverBudget = costVsPlanVal > 0;
    const costIcon = isOverBudget ? <TrendingUp size={20} /> : <TrendingUp size={20} className="transform rotate-180" />;

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];
    const TASK_COLORS = ['#10B981', '#EF4444', '#F59E0B'];

    return (
        <div className="space-y-6 font-sans text-gray-800">
            {/* Header & Toolbar */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 space-y-4">
                {/* Top Row: Title & View Switcher */}
                <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Dashboard Operativo</h2>
                        <p className="text-gray-500 text-sm">Software de alta calidad para decisiones basadas en datos: eficiencia, trazabilidad y uso ético de la información.</p>
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
                                    value={selectedProjectId || 'Desarrollo Web'}
                                    onChange={(e) => setSelectedProjectId(e.target.value)}
                                >
                                    <option value="Desarrollo Web">Desarrollo Web</option>
                                    <option value="Aplicación Móvil">Aplicación Móvil</option>
                                    <option value="Software Empresarial">Software Empresarial</option>
                                    <option value="Infraestructura Cloud">Infraestructura Cloud</option>
                                    <option value="Consultoría Técnica">Consultoría Técnica</option>
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
                            { label: 'Últimos 30 días', days: 30 },
                            { label: 'Últimos 90 días', days: 90 },
                            { label: 'Año Actual (YTD)', days: 365 },
                            { label: 'Todo el Histórico', days: 'all' }
                        ].map(preset => {
                            const isActive = () => {
                                if (preset.days === 'all') return !filters.startDate;
                                if (!filters.startDate) return false;
                                const date = new Date();
                                date.setDate(date.getDate() - preset.days);
                                const isoDate = date.toISOString().split('T')[0];
                                return filters.startDate === isoDate;
                            };

                            return (
                                <button
                                    key={preset.label}
                                    onClick={() => handlePresetClick(preset.days)}
                                    className={`px-3 py-1.5 text-sm rounded-full border transition-colors whitespace-nowrap ${isActive()
                                        ? 'bg-blue-50 border-blue-200 text-blue-700'
                                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'
                                        }`}
                                >
                                    {preset.label}
                                </button>
                            );
                        })}
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
            <div className="space-y-6">
                {metricsLoading ? (
                    <div className="flex items-center justify-center h-64">
                        <div className="animate-spin rounded-full h-12 w-12 border-t-4 border-b-4 border-blue-600"></div>
                    </div>
                ) : projectMetrics ? (
                    <>
                        {/* 5 KPIs Row */}
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                                <div className="p-3 bg-green-50 rounded-full text-green-600">
                                    <Activity size={24} />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">{projectMetrics.isPortfolio ? 'ROI Promedio' : 'ROI del Proyecto'}</div>
                                    <div className="text-2xl font-bold text-gray-800">{projectMetrics.avg_roi}%</div>
                                </div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                                <div className={`p-3 rounded-full ${projectMetrics.isPortfolio || projectMetrics.on_time_projects_pct === 100 ? 'bg-blue-50 text-blue-600' : 'bg-orange-50 text-orange-600'}`}>
                                    {projectMetrics.isPortfolio || projectMetrics.on_time_projects_pct === 100 ? <CheckCircle size={24} /> : <Clock size={24} />}
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">
                                        {projectMetrics.isPortfolio ? 'Proyectos a Tiempo' : (projectMetrics.on_time_projects_pct === 100 ? 'Proyectos a Tiempo' : 'Retraso del Proyecto')}
                                    </div>
                                    <div className={`text-2xl font-bold ${projectMetrics.isPortfolio || projectMetrics.on_time_projects_pct === 100 ? 'text-gray-800' : 'text-orange-600'}`}>
                                        {projectMetrics.isPortfolio ? `${projectMetrics.on_time_projects_pct}%` : (projectMetrics.on_time_projects_pct === 100 ? '100%' : `${projectMetrics.delay_days || 0} días`)}
                                    </div>
                                </div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                                <div className={`p-3 rounded-full ${isOverBudget ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                                    <DollarSign size={24} />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Costo Real vs Planificado</div>
                                    <div className={`text-2xl font-bold flex items-center gap-1 ${isOverBudget ? 'text-red-600' : 'text-green-600'}`}>
                                        {isOverBudget ? '+' : ''}{Math.abs(costVsPlanVal)}%
                                    </div>
                                    <div className={`text-xs font-medium ${isOverBudget ? 'text-red-500' : 'text-green-500'}`}>
                                        {isOverBudget ? 'Sobrecosto' : 'Ahorro'}
                                    </div>
                                </div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                                <div className="p-3 bg-red-50 rounded-full text-red-600">
                                    <AlertTriangle size={24} />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">Defectos Críticos</div>
                                    <div className="text-2xl font-bold text-gray-800">{projectMetrics.critical_defects || 0}</div>
                                </div>
                            </div>
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex items-center gap-4">
                                <div className="p-3 bg-purple-50 rounded-full text-purple-600">
                                    <Users size={24} />
                                </div>
                                <div>
                                    <div className="text-sm text-gray-500">{projectMetrics.isPortfolio ? 'Prom. Empleados' : 'Empleados Asignados'}</div>
                                    <div className="text-2xl font-bold text-gray-800">{projectMetrics.avg_employees_assigned || projectMetrics.employees_assigned || 0}</div>
                                </div>
                            </div>
                        </div>

                        {/* Graphical Charts Section */}
                        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                            {/* Defects by Phase Chart - Extended */}
                            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 lg:col-span-2">
                                <h3 className="text-lg font-semibold text-gray-800 mb-4">
                                    Defectos por Fase <span className="text-sm font-normal text-gray-500 ml-2">(Total: {projectMetrics.total_defects || 0})</span>
                                </h3>
                                <div className="h-48">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={Object.entries(projectMetrics.defects_by_phase || {}).map(([name, value]) => ({ name, value }))}>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                            <XAxis dataKey="name" tick={{ fontSize: 10 }} interval={0} angle={-45} textAnchor="end" height={60} />
                                            <YAxis />
                                            <Tooltip formatter={(value) => value.toLocaleString('en-US', { maximumFractionDigits: 2 })} />
                                            <Bar dataKey="value" fill="#3B82F6" radius={[4, 4, 0, 0]} name="Defectos" />
                                        </BarChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>

                            {/* Defect Distribution Chart (Always Visible) */}
                            <div className="h-full">
                                <QualityDashboard
                                    projectId={viewMode === 'project' ? null : selectedProjectId}
                                    donutOnly={true}
                                    providedData={projectMetrics.defects_by_severity}
                                />
                            </div>

                            {/* Projects Status Chart (Always Visible) */}
                            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 flex flex-col">
                                <h3 className="text-lg font-semibold text-gray-800 mb-2">Estado de Proyectos</h3>
                                <div className="flex-1 flex flex-col justify-center">
                                    {/* Bar Chart: Status */}
                                    <div className="h-48">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <BarChart
                                                layout="vertical"
                                                data={[
                                                    { name: 'Completado', value: projectMetrics.projects_by_status?.['Completado'] || 0 },
                                                    { name: 'Cancelado', value: projectMetrics.projects_by_status?.['Cancelado'] || 0 }
                                                ]}
                                                margin={{ top: 5, right: 30, left: 20, bottom: 5 }}
                                            >
                                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                                <XAxis type="number" hide />
                                                <YAxis dataKey="name" type="category" width={70} tick={{ fontSize: 11 }} />
                                                <Tooltip formatter={(value) => value.toLocaleString('en-US', { maximumFractionDigits: 2 })} />
                                                <Bar dataKey="value" radius={[0, 4, 4, 0]} label={{ position: 'right', fill: '#6B7280', fontSize: 12, formatter: (val) => val.toLocaleString('en-US', { maximumFractionDigits: 2 }) }}>
                                                    {
                                                        [
                                                            { name: 'Completado', value: projectMetrics.projects_by_status?.['Completado'] || 0 },
                                                            { name: 'Cancelado', value: projectMetrics.projects_by_status?.['Cancelado'] || 0 }
                                                        ].map((entry, index) => (
                                                            <Cell key={`cell-${index}`} fill={entry.name === 'Completado' ? '#10B981' : '#EF4444'} />
                                                        ))
                                                    }
                                                </Bar>
                                            </BarChart>
                                        </ResponsiveContainer>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <ExecutiveSummary metrics={projectMetrics} />
                    </>
                ) : (
                    <div className="text-center py-20 text-gray-400">Seleccione un proyecto para ver el análisis detallado.</div>
                )}
            </div>
        </div>
    );
};

export default Dashboard;
