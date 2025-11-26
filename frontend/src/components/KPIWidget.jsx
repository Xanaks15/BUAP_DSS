import React from 'react';
import { PieChart, Pie, Cell, ResponsiveContainer } from 'recharts';

const Gauge = ({ value, label, color }) => {
    const data = [
        { name: 'Value', value: value },
        { name: 'Rest', value: 2 - value }, // Assuming max 2 for SPI/CPI
    ];

    // Cap value at 2 for visualization
    if (value > 2) data[0].value = 2;
    data[1].value = 2 - data[0].value;

    return (
        <div className="flex flex-col items-center justify-center h-full">
            <div className="h-24 w-full">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={data}
                            cx="50%"
                            cy="100%"
                            startAngle={180}
                            endAngle={0}
                            innerRadius={60}
                            outerRadius={80}
                            paddingAngle={0}
                            dataKey="value"
                        >
                            <Cell key="cell-0" fill={color} />
                            <Cell key="cell-1" fill="#e5e7eb" />
                        </Pie>
                    </PieChart>
                </ResponsiveContainer>
            </div>
            <div className="text-2xl font-bold -mt-8">{value}</div>
            <div className="text-sm text-gray-500 mt-2">{label}</div>
        </div>
    );
};

const KPIWidget = ({ title, value, type, color = "#0074C8" }) => {
    return (
        <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-100 flex flex-col items-center">
            <h3 className="text-gray-500 text-sm font-medium mb-2 uppercase tracking-wide">{title}</h3>
            {type === 'gauge' ? (
                <Gauge value={value} label={title} color={color} />
            ) : (
                <div className="text-3xl font-bold text-corporate-dark mt-4">{value}</div>
            )}
        </div>
    );
};

export default KPIWidget;
