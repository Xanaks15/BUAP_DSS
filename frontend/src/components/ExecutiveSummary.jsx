import React from 'react';
import KPIWidget from './KPIWidget';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const ExecutiveSummary = ({ metrics }) => {
    if (!metrics) return <div>Loading...</div>;

    const { spi, cpi, risk_status, productivity, ev, pv, ac } = metrics;

    // Determine colors based on values
    const spiColor = spi >= 1 ? '#00A65A' : spi >= 0.8 ? '#F59E0B' : '#C80000';
    const cpiColor = cpi >= 1 ? '#00A65A' : cpi >= 0.8 ? '#F59E0B' : '#C80000';
    const riskColor = risk_status === 'Low' ? '#00A65A' : risk_status === 'Medium' ? '#F59E0B' : '#C80000';

    // Mock S-Curve Data (since we don't have historical time-series for single project in this endpoint yet)
    // In a real app, we'd fetch historical EV/PV/AC
    const sCurveData = [
        { name: 'Start', pv: 0, ev: 0, ac: 0 },
        { name: '25%', pv: pv * 0.25, ev: ev * 0.2, ac: ac * 0.25 },
        { name: '50%', pv: pv * 0.50, ev: ev * 0.45, ac: ac * 0.55 },
        { name: '75%', pv: pv * 0.75, ev: ev * 0.7, ac: ac * 0.8 },
        { name: 'Now', pv: pv, ev: ev, ac: ac },
    ];

    return (
        <div className="space-y-6">
            <h2 className="text-xl font-bold text-corporate-dark border-b pb-2">1. Vista Ejecutiva del Proyecto</h2>

            {/* KPI Widgets Carousel */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <KPIWidget title="SPI (Schedule)" value={spi} type="gauge" color={spiColor} />
                <KPIWidget title="CPI (Cost)" value={cpi} type="gauge" color={cpiColor} />
                <KPIWidget title="Productivity ($/hr)" value={`$${productivity}`} />
                <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center justify-center">
                    <h3 className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wide">Riesgo</h3>
                    <div className={`text-2xl font-bold px-4 py-1 rounded-full text-white`} style={{ backgroundColor: riskColor }}>
                        {risk_status}
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
                            <YAxis />
                            <Tooltip />
                            <Legend />
                            <Line type="monotone" dataKey="pv" stroke="#0074C8" name="Planned Value (PV)" strokeWidth={2} />
                            <Line type="monotone" dataKey="ev" stroke="#00A65A" name="Earned Value (EV)" strokeWidth={2} />
                            <Line type="monotone" dataKey="ac" stroke="#C80000" name="Actual Cost (AC)" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                </div>
            </div>
        </div>
    );
};

export default ExecutiveSummary;
