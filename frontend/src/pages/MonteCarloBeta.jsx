import React, { useState } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Calculator, BarChart2, AlertTriangle } from 'lucide-react';

const MonteCarloBeta = () => {
    const [inputs, setInputs] = useState({
        horasEstimadas: 1000,
        complejidad: 'media',
        tipoProyecto: 'Desarrollo Web'
    });

    const [simulationResults, setSimulationResults] = useState(null);
    const [simLoading, setSimLoading] = useState(false);
    const [error, setError] = useState(null);

    const runMonteCarlo = async () => {
        setSimLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/predictions/monte-carlo', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    horasEstimadas: inputs.horasEstimadas,
                    complejidad: inputs.complejidad,
                    tipoProyecto: inputs.tipoProyecto
                })
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();

            // Process distribution for histogram
            const dist = data.distribution;
            if (!dist || dist.length === 0) {
                throw new Error("No data returned from simulation");
            }

            const min = Math.min(...dist);
            const max = Math.max(...dist);
            const bins = 20;
            const step = (max - min) / bins;
            const histogramData = [];

            for (let i = 0; i < bins; i++) {
                const start = min + i * step;
                const end = start + step;
                const count = dist.filter(v => v >= start && v < end).length;
                histogramData.push({
                    range: `${Math.round(start)}-${Math.round(end)}`,
                    count: count,
                    mid: (start + end) / 2
                });
            }

            setSimulationResults({
                ...data,
                histogramData
            });
        } catch (error) {
            console.error("Error running simulation:", error);
            setError(error.message);
        } finally {
            setSimLoading(false);
        }
    };

    return (
        <div className="space-y-6">
            <header className="flex items-center space-x-3">
                <h2 className="text-2xl font-bold text-gray-800">Simulación Monte Carlo</h2>
                <span className="bg-purple-100 text-purple-800 text-xs font-medium px-2.5 py-0.5 rounded border border-purple-400">BETA</span>
            </header>

            <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
                <div className="flex">
                    <div className="flex-shrink-0">
                        <AlertTriangle className="h-5 w-5 text-yellow-400" aria-hidden="true" />
                    </div>
                    <div className="ml-3">
                        <p className="text-sm text-yellow-700">
                            Esta función está en fase beta. Los resultados pueden variar y están sujetos a revisión.
                            Compara la predicción del modelo con 5000 escenarios posibles basados en datos históricos.
                        </p>
                    </div>
                </div>
            </div>

            {/* Input Form */}
            <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100">
                <div className="flex items-center space-x-2 mb-4 text-purple-600 border-b pb-2">
                    <Calculator size={20} />
                    <h3 className="text-lg font-bold">Parámetros de Simulación</h3>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 items-end">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Horas Estimadas</label>
                        <input
                            type="number"
                            value={inputs.horasEstimadas}
                            onChange={(e) => setInputs({ ...inputs, horasEstimadas: Number(e.target.value) })}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Proyecto</label>
                        <select
                            value={inputs.tipoProyecto}
                            onChange={(e) => setInputs({ ...inputs, tipoProyecto: e.target.value })}
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
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
                            className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-purple-500 outline-none"
                        >
                            <option value="baja">Baja</option>
                            <option value="media">Media</option>
                            <option value="alta">Alta</option>
                        </select>
                    </div>

                    <button
                        onClick={runMonteCarlo}
                        disabled={simLoading}
                        className="w-full bg-purple-600 text-white py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                    >
                        {simLoading ? <div className="animate-spin rounded-full h-4 w-4 border-2 border-white"></div> : <BarChart2 size={18} />}
                        <span>Ejecutar Simulación</span>
                    </button>
                </div>

                {error && (
                    <div className="mt-4 p-3 bg-red-50 text-red-700 rounded-lg text-sm">
                        Error: {error}
                    </div>
                )}
            </div>

            {/* Results */}
            {simulationResults && (
                <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 animate-fade-in">
                    <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-bold text-gray-800">Resultados (5000 Escenarios)</h3>
                        <div className="text-sm text-gray-500">
                            Promedio Histórico ({inputs.tipoProyecto}): <span className="font-bold text-green-600">{simulationResults.historical_average}</span>
                        </div>
                    </div>
                    <div className="h-96">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={simulationResults.histogramData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="range" tick={{ fontSize: 10 }} label={{ value: 'Rango de Defectos', position: 'insideBottom', offset: -5 }} />
                                <YAxis label={{ value: 'Frecuencia', angle: -90, position: 'insideLeft' }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                />
                                <Legend />
                                <Bar dataKey="count" name="Escenarios" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4 text-center text-sm">
                        <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                            <div className="text-gray-500 mb-1">Promedio Simulado</div>
                            <div className="font-bold text-2xl text-gray-800">{simulationResults.stats.mean}</div>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                            <div className="text-gray-500 mb-1">Rango Probable (5% - 95%)</div>
                            <div className="font-bold text-2xl text-gray-800">{simulationResults.stats.p5} - {simulationResults.stats.p95}</div>
                        </div>
                        <div className="p-4 bg-gray-50 rounded-lg border border-gray-100">
                            <div className="text-gray-500 mb-1">Certeza vs Histórico</div>
                            <div className={`font-bold text-2xl ${Math.abs(simulationResults.stats.mean - simulationResults.historical_average) < simulationResults.stats.mean * 0.2 ? 'text-green-600' : 'text-orange-600'
                                }`}>
                                {Math.abs(simulationResults.stats.mean - simulationResults.historical_average) < simulationResults.stats.mean * 0.2 ? 'Alta' : 'Baja'}
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default MonteCarloBeta;
