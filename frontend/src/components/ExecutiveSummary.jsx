import React from 'react';
import KPIWidget from './KPIWidget';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, BarChart, Bar, Cell, PieChart, Pie, LabelList } from 'recharts';

const ExecutiveSummary = ({ metrics }) => {
    if (!metrics) return <div>Loading...</div>;

    const { spi, cpi, risk_status, productivity, ev, pv, ac } = metrics;

    // Determine colors based on values
    const riskColor = risk_status === 'Low' ? '#00A65A' : risk_status === 'Medium' ? '#F59E0B' : '#C80000';

    // Mock S-Curve Data
    const sCurveData = [
        { name: 'Inicio', pv: 0, ev: 0, ac: 0 },
        { name: '25%', pv: pv * 0.25, ev: ev * 0.2, ac: ac * 0.25 },
        { name: '50%', pv: pv * 0.50, ev: ev * 0.45, ac: ac * 0.55 },
        { name: '75%', pv: pv * 0.75, ev: ev * 0.7, ac: ac * 0.8 },
        { name: 'Actual', pv: pv, ev: ev, ac: ac },
    ];

    // Helper for formatting
    const formatNumber = (num) => {
        if (num === undefined || num === null) return '0';
        return num.toLocaleString('en-US', { maximumFractionDigits: 2 });
    };

    // Calculate Planned Productivity
    const planned_hours = metrics.total_hours_planned || metrics.horas_planificadas || 1;
    const planned_productivity = (metrics.pv || 0) / (planned_hours > 0 ? planned_hours : 1);

    return (
        <div className="space-y-6">
            <h2 className="text-xl font-bold text-corporate-dark border-b pb-2">1. Vista Ejecutiva del Proyecto</h2>

            {/* KPI Widgets Carousel - 3 Columns now */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {/* Hours Chart */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col justify-center">
                    <h3 className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wide">Horas Plan vs Real</h3>
                    <div className="h-32">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                layout="vertical"
                                data={[
                                    { name: 'Plan', value: metrics.total_hours_planned || metrics.horas_planificadas || 0 },
                                    { name: 'Real', value: metrics.total_hours_real || metrics.horas_reales || 0 }
                                ]}
                                margin={{ top: 0, right: 45, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" width={30} tick={{ fontSize: 10 }} />
                                <Tooltip formatter={(value) => formatNumber(value)} />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                                    {
                                        [
                                            { name: 'Plan', value: metrics.total_hours_planned || metrics.horas_planificadas || 0 },
                                            { name: 'Real', value: metrics.total_hours_real || metrics.horas_reales || 0 }
                                        ].map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={index === 0 ? '#3B82F6' : (entry.value > (metrics.total_hours_planned || metrics.horas_planificadas || 0) ? '#EF4444' : '#10B981')} />
                                        ))
                                    }
                                    <LabelList dataKey="value" position="right" style={{ fontSize: '11px', fill: '#6B7280', fontWeight: 'bold' }} formatter={(val) => formatNumber(val)} />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Task Status Chart */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col justify-center">
                    <h3 className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wide">% Estado de Tareas</h3>
                    <div className="h-32">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                layout="vertical"
                                data={[
                                    { name: 'A Tiempo', value: Math.max(0, (metrics.tasks_completed_pct || 0) - (metrics.tasks_delayed_pct || 0)), fill: '#10B981' },
                                    { name: 'Retrasadas', value: metrics.tasks_delayed_pct || 0, fill: '#EF4444' },
                                    { name: 'No Comp.', value: metrics.tasks_not_completed_pct || 0, fill: '#9CA3AF' }
                                ]}
                                margin={{ top: 0, right: 35, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" width={60} tick={{ fontSize: 10 }} />
                                <Tooltip formatter={(value) => `${formatNumber(value)}%`} />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={20}>
                                    <LabelList dataKey="value" position="right" style={{ fontSize: '11px', fill: '#6B7280', fontWeight: 'bold' }} formatter={(val) => `${formatNumber(val)}%`} />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Productivity Chart (Plan vs Real) */}
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col justify-center">
                    <h3 className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wide">Productividad ($/hr)</h3>
                    <div className="h-32">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart
                                layout="vertical"
                                data={[
                                    { name: 'Plan', value: planned_productivity },
                                    { name: 'Real', value: productivity }
                                ]}
                                margin={{ top: 0, right: 45, left: 0, bottom: 0 }}
                            >
                                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" width={30} tick={{ fontSize: 10 }} />
                                <Tooltip formatter={(value) => `$${formatNumber(value)}`} />
                                <Bar dataKey="value" radius={[0, 4, 4, 0]} barSize={24}>
                                    {
                                        [
                                            { name: 'Plan', value: planned_productivity },
                                            { name: 'Real', value: productivity }
                                        ].map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={index === 0 ? '#3B82F6' : (entry.value >= planned_productivity ? '#10B981' : '#F59E0B')} />
                                        ))
                                    }
                                    <LabelList dataKey="value" position="right" style={{ fontSize: '11px', fill: '#6B7280', fontWeight: 'bold' }} formatter={(val) => `$${formatNumber(val)}`} />
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>

            {/* S-Curve */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                <h3 className="text-lg font-semibold mb-4 text-corporate-blue">Curva S de Avance (Valor Ganado)</h3>
                <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={sCurveData}>
                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                            <XAxis dataKey="name" />
                            <YAxis tickFormatter={(val) => `$${formatNumber(val)}`} width={80} />
                            <Tooltip formatter={(value) => `$${formatNumber(value)}`} />
                            <Legend />
                            <Line type="monotone" dataKey="pv" stroke="#0074C8" name="Valor Planificado (PV)" strokeWidth={2} />
                            <Line type="monotone" dataKey="ev" stroke="#00A65A" name="Valor Ganado (EV)" strokeWidth={2} />
                            <Line type="monotone" dataKey="ac" stroke="#C80000" name="Costo Real (AC)" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default ExecutiveSummary;
