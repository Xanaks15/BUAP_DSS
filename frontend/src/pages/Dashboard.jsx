import React, { useEffect, useState } from 'react';
import { getProjects, getProjectMetrics } from '../services/api';
import ExecutiveSummary from '../components/ExecutiveSummary';
import RayleighCurves from '../components/RayleighCurves';
import QualityDashboard from '../components/QualityDashboard';
import { Filter, Calendar, Users, Briefcase } from 'lucide-react';

const Dashboard = () => {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null); // Null means "All Projects" / Portfolio View
    const [projectMetrics, setProjectMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    // Filters state
    const [filters, setFilters] = useState({
        startDate: '',
        endDate: '',
        type: 'all',
        status: 'all',
        client: 'all'
    });

    useEffect(() => {
        // Fetch projects list
        getProjects().then(data => {
            setProjects(data);
            // Default to first project for now, or null for portfolio
            if (data.length > 0) {
                setSelectedProjectId(data[0].proyecto_id);
            }
            setLoading(false);
        }).catch(err => {
            console.error("Error fetching projects:", err);
            setLoading(false);
        });
    }, []);

    useEffect(() => {
        if (selectedProjectId) {
            getProjectMetrics(selectedProjectId).then(setProjectMetrics).catch(console.error);
        } else {
            setProjectMetrics(null);
        }
    }, [selectedProjectId]);

    if (loading) return <div className="flex items-center justify-center h-full text-corporate-blue">Cargando DSS...</div>;

    return (
        <div className="space-y-8 font-sans text-gray-800">
            {/* Header & Filters */}
            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 space-y-6">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                    <div>
                        <h2 className="text-2xl font-bold text-gray-800">Dashboard Operativo</h2>
                        <p className="text-gray-500">Monitor de rendimiento de proyectos y calidad</p>
                    </div>

                    {/* Project Selector */}
                    <div className="flex items-center space-x-3 bg-gray-50 px-4 py-2 rounded-lg border border-gray-200">
                        <Briefcase size={18} className="text-gray-500" />
                        <select
                            className="bg-transparent border-none focus:ring-0 text-gray-700 font-medium"
                            value={selectedProjectId || ''}
                            onChange={(e) => setSelectedProjectId(Number(e.target.value))}
                        >
                            {projects.map(p => (
                                <option key={p.proyecto_id} value={p.proyecto_id}>{p.nombre}</option>
                            ))}
                        </select>
                    </div>
                </div>

                {/* Filters Bar */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 pt-4 border-t border-gray-100">
                    <div className="flex items-center space-x-2">
                        <Calendar size={16} className="text-gray-400" />
                        <input
                            type="date"
                            className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                            value={filters.startDate}
                            onChange={(e) => setFilters({ ...filters, startDate: e.target.value })}
                        />
                    </div>
                    <div className="flex items-center space-x-2">
                        <Filter size={16} className="text-gray-400" />
                        <select
                            className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 w-full"
                            value={filters.type}
                            onChange={(e) => setFilters({ ...filters, type: e.target.value })}
                        >
                            <option value="all">Todos los Tipos</option>
                            <option value="desarrollo">Desarrollo</option>
                            <option value="mantenimiento">Mantenimiento</option>
                        </select>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Filter size={16} className="text-gray-400" />
                        <select
                            className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 w-full"
                            value={filters.status}
                            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
                        >
                            <option value="all">Todos los Estados</option>
                            <option value="activo">Activo</option>
                            <option value="completado">Completado</option>
                        </select>
                    </div>
                    <div className="flex items-center space-x-2">
                        <Users size={16} className="text-gray-400" />
                        <select
                            className="text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500 w-full"
                            value={filters.client}
                            onChange={(e) => setFilters({ ...filters, client: e.target.value })}
                        >
                            <option value="all">Todos los Clientes</option>
                            {/* Mock clients */}
                            <option value="cliente1">Cliente A</option>
                            <option value="cliente2">Cliente B</option>
                        </select>
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
