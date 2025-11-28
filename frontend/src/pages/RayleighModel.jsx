import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, ReferenceLine } from 'recharts';
import { Calculator, Play } from 'lucide-react';

const RayleighModel = () => {
    const [inputs, setInputs] = useState({
        horasEstimadas: 1000,
        duracionSemanas: 12,
        complejidad: 'media',
        tipoProyecto: 'Desarrollo Web'
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

        const typeMultipliers = {
            'Desarrollo Web': 1.0,
            'Aplicación Móvil': 1.1,
            'Software Empresarial': 1.2,
            'Infraestructura Cloud': 0.9,
            'Consultoría Técnica': 0.7
        };

        const defectsPerHour = defectRates[inputs.complejidad] || 0.05;
        const typeMult = typeMultipliers[inputs.tipoProyecto] || 1.0;
        const totalDefects = defectsPerHour * horasEstimadas * typeMult;

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

            {/* Input Form - Moved to Top */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                <div className="flex items-center space-x-2 mb-4 text-corporate-blue border-b pb-2">
                    <Calculator size={20} />
                    <h3 className="text-lg font-bold">Parámetros del Proyecto</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
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
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Proyecto</label>
                        <select
                            value={inputs.tipoProyecto}
                            onChange={(e) => setInputs({ ...inputs, tipoProyecto: e.target.value })}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            <option value="Desarrollo Web">Desarrollo Web</option>
                            <option value="Aplicación Móvil">Aplicación Móvil</option>
                            <option value="Software Empresarial">Software Empresarial</option>
                            <option value="Infraestructura Cloud">Infraestructura Cloud</option>
                            <option value="Consultoría Técnica">Consultoría Técnica</option>
                        </select>
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
                        className="w-full bg-corporate-blue text-white py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
                    >
                        <Play size={18} />
                        <span>Ejecutar Modelo</span>
                    </button>
                </div>
            </div>

            {/* Results */}
            <div className="space-y-6">
                {results ? (
                    <>
                        {/* Top Row: Stats & Pie Chart */}
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            {/* Stats Cards (2/3 width) */}
                            <div className="lg:col-span-2 grid grid-cols-1 sm:grid-cols-3 gap-4 h-full">
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center">
                                    <div className="text-sm text-gray-500 mb-1">Defectos Totales (Est.)</div>
                                    <div className="text-3xl font-bold text-blue-600">{results.totalDefects}</div>
                                </div>
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center">
                                    <div className="text-sm text-gray-500 mb-1">Semana Pico (t_peak)</div>
                                    <div className="text-3xl font-bold text-purple-600">{results.tPeak}</div>
                                </div>
                                <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-center items-center text-center">
                                    <div className="text-sm text-gray-500 mb-1">Sigma (σ)</div>
                                    <div className="text-3xl font-bold text-orange-600">{results.sigma}</div>
                                </div>
                            </div>

                            {/* Phase Distribution (Where?) - Top Right (1/3 width) */}
                            <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 flex flex-col items-center justify-center">
                                <h3 className="text-sm font-bold mb-2 text-gray-800 w-full text-center">Distribución de Defectos</h3>
                                <div className="h-40 w-full flex items-center justify-center">
                                    <ResponsiveContainer width="100%" height="100%">
                                        <PieChart>
                                            <Pie
                                                data={phaseDistribution}
                                                cx="50%"
                                                cy="50%"
                                                innerRadius={40}
                                                outerRadius={60}
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
                                <div className="flex flex-wrap justify-center gap-3 mt-2 text-xs text-gray-500">
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
                            <div className="h-96">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={results.data} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                        <XAxis dataKey="semana" type="number" domain={['dataMin', 'dataMax']} label={{ value: 'Semanas', position: 'insideBottom', offset: -5 }} />
                                        <YAxis />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                        />
                                        <Legend verticalAlign="top" height={36} />
                                        <ReferenceLine x={Number(results.sigma)} stroke="#ea580c" strokeDasharray="3 3" label={{ value: `σ: ${results.sigma}`, position: 'top', fill: '#ea580c' }} />
                                        <Line type="monotone" dataKey="defectos" name="Defectos por Semana" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                                        <Line type="monotone" dataKey="acumulado" name="Defectos Acumulados" stroke="#9333ea" strokeWidth={2} strokeDasharray="5 5" dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </>
                ) : (
                    <div className="h-64 flex flex-col items-center justify-center bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 text-gray-400">
                        <Calculator size={48} className="mb-4 opacity-50" />
                        <p>Ingrese los parámetros arriba y ejecute el modelo para ver los resultados.</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RayleighModel;
