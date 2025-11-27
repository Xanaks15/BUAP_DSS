import React, { useEffect, useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell, PieChart, Pie } from 'recharts';
import { getProjectQuality } from '../services/api';

const QualityDashboard = ({ projectId, donutOnly = false, providedData = null }) => {
    const [qualityData, setQualityData] = useState(null);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (providedData) {
            setQualityData({ by_severity: providedData });
            return;
        }

        if (projectId) {
            getProjectQuality(projectId)
                .then(setQualityData)
                .catch(err => {
                    console.error(err);
                    setError("Error cargando métricas de calidad");
                });
        } else {
            // If no project ID and no provided data, reset
            setQualityData(null);
        }
    }, [projectId, providedData]);

    if (!projectId && !donutOnly && !providedData) return <div className="text-center text-gray-400 mt-8">Seleccione un proyecto para ver métricas de calidad (Drill-down).</div>;

    // If donutOnly is true but no data yet
    if (!qualityData && donutOnly) {
        return <div className="h-full flex items-center justify-center text-gray-400 text-sm">Cargando...</div>;
    }

    if (!qualityData) return <div>Cargando Métricas de Calidad...</div>;

    const severityData = qualityData.by_severity ? Object.entries(qualityData.by_severity).map(([name, value]) => ({ name, value })) : [];
    const phaseData = qualityData.by_phase ? Object.entries(qualityData.by_phase).map(([name, value]) => ({ name, value })) : [];

    const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#C80000'];

    if (donutOnly) {
        return (
            <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 h-full flex flex-col">
                <h3 className="text-sm font-semibold text-gray-600 mb-2">Distribución de Defectos</h3>
                <div className="flex-1 min-h-[200px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <PieChart>
                            <Pie
                                data={severityData}
                                cx="50%"
                                cy="50%"
                                innerRadius={60}
                                outerRadius={80}
                                fill="#8884d8"
                                paddingAngle={5}
                                dataKey="value"
                            >
                                {severityData.map((entry, index) => (
                                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                ))}
                            </Pie>
                            <Tooltip />
                            <Legend verticalAlign="bottom" height={36} />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 mt-8">
            <h2 className="text-xl font-bold text-corporate-dark border-b pb-2">4. Calidad y Defectos</h2>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 text-center">
                    <div className="text-gray-500 text-sm uppercase">Total Defectos</div>
                    <div className="text-3xl font-bold text-corporate-blue">{qualityData.total_defects}</div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 text-center">
                    <div className="text-gray-500 text-sm uppercase">Densidad de Defectos</div>
                    <div className="text-3xl font-bold text-corporate-blue">{qualityData.defect_density_per_100h} <span className="text-sm text-gray-400">/100h</span></div>
                </div>
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 text-center">
                    <div className="text-gray-500 text-sm uppercase">DRE (Est.)</div>
                    <div className="text-3xl font-bold text-corporate-green">95%</div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Severity Chart */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-corporate-blue">Defectos por Severidad</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={severityData} layout="vertical">
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" />
                                <YAxis dataKey="name" type="category" width={100} />
                                <Tooltip />
                                <Bar dataKey="value" fill="#0074C8">
                                    {severityData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Phase Chart */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-corporate-blue">Defectos por Fase SDLC</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={phaseData}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="name" />
                                <YAxis />
                                <Tooltip />
                                <Bar dataKey="value" fill="#00A65A" />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default QualityDashboard;
