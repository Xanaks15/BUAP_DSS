import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Calculator, Play } from 'lucide-react';

const RayleighModel = () => {
    const [inputs, setInputs] = useState({
        horasEstimadas: 1000,
        duracionSemanas: 12,
        complejidad: 'media',
        tipoProyecto: 'desarrollo'
    });

    const [results, setResults] = useState(null);
    const [phaseDistribution, setPhaseDistribution] = useState([]);

    const calculateRayleigh = () => {
        const { horasEstimadas, duracionSemanas } = inputs;

        // 1. Calculate Sigma
        const sigma = duracionSemanas / 2.5;

        // 2. Calculate Peak Time
        const tPeak = sigma * Math.sqrt(2);

        // 3. Estimate Total Defects (Calibration based on complexity)
        const defectRates = {
            baja: 0.03,
            media: 0.05,
            alta: 0.08
        };
        const defectsPerHour = defectRates[inputs.complejidad] || 0.05;
        const totalDefects = defectsPerHour * horasEstimadas;

        // 4. Generate Curve Points
        const data = [];
        let cumulativeDefects = 0;

        for (let t = 1; t <= duracionSemanas; t++) {
            // PDF: f(t) = (t / sigma^2) * exp(-t^2 / 2sigma^2)
            // We scale PDF by totalDefects to get defects per week
            const pdf = (t / (sigma * sigma)) * Math.exp(-(t * t) / (2 * sigma * sigma));
            const defectsThisWeek = totalDefects * pdf;

            cumulativeDefects += defectsThisWeek;

            data.push({
                semana: t,
                defectos: Number(defectsThisWeek.toFixed(2)),
                acumulado: Number(cumulativeDefects.toFixed(2))
            });
        }

        // 5. Calculate Phase Distribution (Where?)
        const phases = [
            { name: 'Requisitos', value: Math.round(totalDefects * 0.15), color: '#3B82F6' },
            { name: 'Diseño', value: Math.round(totalDefects * 0.25), color: '#8B5CF6' },
            { name: 'Codificación', value: Math.round(totalDefects * 0.40), color: '#EF4444' },
            { name: 'Pruebas', value: Math.round(totalDefects * 0.20), color: '#10B981' }
        ];

        setResults({
            sigma: sigma.toFixed(2),
            tPeak: tPeak.toFixed(2),
            totalDefects: Math.round(totalDefects),
            data
        });
        setPhaseDistribution(phases);
    };

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-2xl font-bold text-gray-800">Modelo Predictivo Rayleigh</h2>
                <p className="text-gray-500">Estimación de defectos y distribución temporal</p>
            </header>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Input Form */}
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-fit">
                    <div className="flex items-center space-x-2 mb-6 text-corporate-blue">
                        <Calculator size={24} />
                        <h3 className="text-lg font-bold">Parámetros del Proyecto</h3>
                    </div>

                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Horas Estimadas</label>
                            <input
                                type="number"
                                value={inputs.horasEstimadas}
                                onChange={(e) => setInputs({ ...inputs, horasEstimadas: Number(e.target.value) })}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Duración (Semanas)</label>
                            <input
                                type="number"
                                value={inputs.duracionSemanas}
                                onChange={(e) => setInputs({ ...inputs, duracionSemanas: Number(e.target.value) })}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">Complejidad</label>
                            <select
                                value={inputs.complejidad}
                                onChange={(e) => setInputs({ ...inputs, complejidad: e.target.value })}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="baja">Baja</option>
                                <option value="media">Media</option>
                                <option value="alta">Alta</option>
                            </select>
                        </div>

                        <button
                            onClick={calculateRayleigh}
                            className="w-full bg-corporate-blue text-white py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 mt-4"
                        >
                            <Play size={18} />
                            <span>Ejecutar Modelo</span>
                        </button>
                    </div>
                </div>

                {/* Results */}
                <div className="lg:col-span-2 space-y-6">
                    {results ? (
                        <>
                            {/* Top Row: Stats & Pie Chart */}
                            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
                                {/* Stats Cards (2/3 width) */}
                                <div className="xl:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4 h-fit">
                                    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
                                        <div className="text-sm text-gray-500">Defectos Totales (Est.)</div>
                                        <div className="text-2xl font-bold text-blue-600">{results.totalDefects}</div>
                                    </div>
                                    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
                                        <div className="text-sm text-gray-500">Semana Pico (t_peak)</div>
                                        <div className="text-2xl font-bold text-purple-600">{results.tPeak}</div>
                                    </div>
                                    <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center">
                                        <div className="text-sm text-gray-500">Sigma (σ)</div>
                                        <div className="text-2xl font-bold text-orange-600">{results.sigma}</div>
                                    </div>
                                </div>

                                {/* Phase Distribution (Where?) - Top Right (1/3 width) */}
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center">
                                    <h3 className="text-sm font-bold mb-2 text-gray-800 w-full text-left">Distribución (Dónde)</h3>
                                    <div className="h-32 w-full flex items-center justify-center">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <PieChart>
                                                <Pie
                                                    data={phaseDistribution}
                                                    cx="50%"
                                                    cy="50%"
                                                    innerRadius={30}
                                                    outerRadius={50}
                                                    paddingAngle={5}
                                                    dataKey="value"
                                                >
                                                    {phaseDistribution.map((entry, index) => (
                                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                                    ))}
                                                </Pie>
                                                <Tooltip />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <div className="flex flex-wrap justify-center gap-2 mt-2 text-xs text-gray-500">
                                        {phaseDistribution.map((entry, index) => (
                                            <div key={index} className="flex items-center space-x-1">
                                                <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }}></div>
                                                <span>{entry.name}</span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>

                            {/* Bottom Row: Rayleigh Curve (Full Width) */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <h3 className="text-lg font-bold mb-4 text-gray-800">Curva de Descubrimiento de Defectos (Cuándo)</h3>
                                <div className="h-80">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={results.data}>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                            <XAxis dataKey="semana" label={{ value: 'Semanas', position: 'insideBottom', offset: -5 }} />
                                            <YAxis />
                                            <Tooltip
                                                contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            />
                                            <Legend />
                                            <Line type="monotone" dataKey="defectos" name="Defectos por Semana" stroke="#2563eb" strokeWidth={2} dot={{ r: 4 }} />
                                            <Line type="monotone" dataKey="acumulado" name="Defectos Acumulados" stroke="#9333ea" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                </div>
                            </div>
                        </>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 text-gray-400">
                            <Calculator size={48} className="mb-4 opacity-50" />
                            <p>Ingrese los parámetros y ejecute el modelo para ver los resultados.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default RayleighModel;
