import React, { useEffect, useState } from 'react';
import { getProjects, getProjectMetrics } from '../services/api';
import ExecutiveSummary from '../components/ExecutiveSummary';
import RayleighCurves from '../components/RayleighCurves';
import QualityDashboard from '../components/QualityDashboard';

const Dashboard = () => {
    const [projects, setProjects] = useState([]);
    const [selectedProjectId, setSelectedProjectId] = useState(null);
    const [projectMetrics, setProjectMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch projects list
        getProjects().then(data => {
            setProjects(data);
            if (data.length > 0) {
                setSelectedProjectId(data[0].proyecto_id); // Default to first project
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
        }
    }, [selectedProjectId]);

    if (loading) return <div className="flex items-center justify-center h-screen text-corporate-blue">Cargando DSS...</div>;

    return (
        <div className="min-h-screen bg-gray-50 p-8 font-sans text-gray-800">
            {/* Header */}
            <header className="flex justify-between items-center mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-corporate-blue">BUAP DSS</h1>
                    <p className="text-gray-500">Sistema de Soporte a la Decisión - Gestión de Proyectos</p>
                </div>

                {/* Project Selector */}
                <div className="flex items-center space-x-4">
                    <label className="font-medium text-gray-700">Proyecto:</label>
                    <select
                        className="border border-gray-300 rounded-md px-3 py-2 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-corporate-blue"
                        value={selectedProjectId || ''}
                        onChange={(e) => setSelectedProjectId(Number(e.target.value))}
                    >
                        {projects.map(p => (
                            <option key={p.proyecto_id} value={p.proyecto_id}>{p.nombre}</option>
                        ))}
                    </select>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto space-y-8">
                {projectMetrics ? (
                    <>
                        <ExecutiveSummary metrics={projectMetrics} />
                        <RayleighCurves projectData={projectMetrics} />
                        <QualityDashboard projectId={selectedProjectId} />
                    </>
                ) : (
                    <div className="text-center py-20 text-gray-400">Seleccione un proyecto para ver el análisis.</div>
                )}
            </main>
        </div>
    );
};

export default Dashboard;
