import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calculator, Play } from 'lucide-react';

const RayleighModel = () => {
    const [inputs, setInputs] = useState({
        horasEstimadas: 1000,
        duracionSemanas: 12,
        complejidad: 'media',
        tipoProyecto: 'desarrollo'
    });

    const [results, setResults] = useState(null);

    const calculateRayleigh = () => {
        const { horasEstimadas, duracionSemanas } = inputs;

        // 1. Calculate Sigma
        const sigma = duracionSemanas / 2.5;

        // 2. Calculate Peak Time
        const tPeak = sigma * Math.sqrt(2);

        // 3. Estimate Total Defects (Calibration: 0.05 defects per hour approx)
        const defectsPerHour = 0.05;
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

        setResults({
            sigma: sigma.toFixed(2),
            tPeak: tPeak.toFixed(2),
            totalDefects: Math.round(totalDefects),
            data
        });
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
                            {/* Stats Cards */}
                            <div className="grid grid-cols-3 gap-4">
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                    <div className="text-sm text-gray-500">Defectos Totales (Est.)</div>
                                    <div className="text-2xl font-bold text-blue-600">{results.totalDefects}</div>
                                </div>
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                    <div className="text-sm text-gray-500">Semana Pico (t_peak)</div>
                                    <div className="text-2xl font-bold text-purple-600">{results.tPeak}</div>
                                </div>
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
                                    <div className="text-sm text-gray-500">Sigma (σ)</div>
                                    <div className="text-2xl font-bold text-orange-600">{results.sigma}</div>
                                </div>
                            </div>

                            {/* Chart */}
                            <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                                <h3 className="text-lg font-bold mb-4 text-gray-800">Curva de Descubrimiento de Defectos</h3>
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
