import React, { useEffect, useState } from 'react';
import api from '../services/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PerspectiveCard = ({ title, color, chartData, barColor }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className={`text-lg font-bold mb-4 ${color}`}>{title}</h3>

        {/* Chart Section */}
        <div className="h-64 mt-4">
            <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" />
                    <YAxis dataKey="name" type="category" width={90} tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="Actual" fill={barColor} radius={[0, 4, 4, 0]} barSize={20} />
                    <Bar dataKey="Meta" fill="#6B7280" radius={[0, 4, 4, 0]} barSize={20} />
                </BarChart>
            </ResponsiveContainer>
        </div>
    </div>
);

const BalancedScorecard = () => {
    const [metrics, setMetrics] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.get('/dashboard/kpis/okrs')
            .then(res => {
                setMetrics(res.data);
                setLoading(false);
            })
            .catch(err => {
                console.error("Error fetching OKRs:", err);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="text-center py-10">Cargando Scorecard...</div>;
    if (!metrics) return <div className="text-center py-10">No hay datos disponibles.</div>;

    // Construct Perspectives Data
    const perspectives = [
        {
            title: "Financiera",
            color: "text-blue-600",
            barColor: "#2563EB",
            chartData: [
                { name: 'ROI (%)', Actual: metrics.financial.roi, Meta: 12 },
                { name: 'Desv. Costo (%)', Actual: metrics.financial.cost_dev, Meta: 10 },
                { name: 'Proy. Rentables (%)', Actual: metrics.financial.profitable_projects_pct, Meta: 85 }
            ]
        },
        {
            title: "Cliente",
            color: "text-green-600",
            barColor: "#16A34A",
            chartData: [
                { name: 'A Tiempo (%)', Actual: metrics.customer.on_time_pct, Meta: 90 },
                { name: 'Sin Def. Crit. (%)', Actual: metrics.customer.defect_free_pct, Meta: 95 },
                { name: 'Retraso OK (%)', Actual: metrics.customer.acceptable_delay_pct, Meta: 80 }
            ]
        },
        {
            title: "Procesos Internos",
            color: "text-purple-600",
            barColor: "#9333EA",
            chartData: [
                { name: 'Defectos (Prom)', Actual: metrics.internal.avg_defects, Meta: 25 },
                { name: 'Tareas OK (%)', Actual: metrics.internal.tasks_completed_pct, Meta: 90 }
            ]
        },
        {
            title: "Aprendizaje y Crecimiento",
            color: "text-orange-600",
            barColor: "#EA580C",
            chartData: [
                { name: 'Productividad (%)', Actual: metrics.learning.productivity_pct, Meta: 85 },
                { name: 'Uso Modelo (%)', Actual: metrics.learning.model_usage_pct, Meta: 70 }
            ]
        }
    ];

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-2xl font-bold text-gray-800">Balanced Scorecard</h2>
                <p className="text-gray-500">Monitoreo de objetivos estratégicos y OKRs (Datos Reales)</p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {perspectives.map((p, idx) => (
                    <PerspectiveCard key={idx} {...p} />
                ))}
            </div>
        </div>
    );
};

export default BalancedScorecard;
