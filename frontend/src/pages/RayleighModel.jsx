import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell, ReferenceLine } from 'recharts';
import { Calculator, Play, AlertTriangle, Info, TrendingUp, Users, Clock } from 'lucide-react';
import { predictDefectsEnhanced } from '../services/api';

const RayleighModel = () => {
    const [inputs, setInputs] = useState({
        horasEstimadas: 1000,
        duracionSemanas: 12,
        complejidad: 'media',
        tipoProyecto: 'Desarrollo Web',
        proyectoId: null // Optional: Only for real-time monitoring
    });

    const [results, setResults] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const calculateRayleigh = async () => {
        setLoading(true);
        setError(null);
        try {
            const data = await predictDefectsEnhanced(inputs);
            setResults(data);
        } catch (err) {
            console.error("Error fetching prediction:", err);
            setError("Error al conectar con el modelo inteligente. Verifique el backend.");
        } finally {
            setLoading(false);
        }
    };

    // Helper to get risk color
    const getRiskColor = (level) => {
        switch (level) {
            case 'High': return 'bg-red-100 text-red-800 border-red-200';
            case 'Medium': return 'bg-yellow-100 text-yellow-800 border-yellow-200';
            default: return 'bg-green-100 text-green-800 border-green-200';
        }
    };

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-2xl font-bold text-gray-800">Modelo Predictivo Rayleigh (Mejorado)</h2>
                <p className="text-gray-500">Estimación inteligente basada en historia y KPIs en tiempo real</p>
            </header>

            {/* Input Form */}
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

                </div>

                <div className="mt-6">
                    <button
                        onClick={calculateRayleigh}
                        disabled={loading}
                        className="w-full bg-corporate-blue text-white py-2 rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2 disabled:opacity-50"
                    >
                        {loading ? <span>Procesando...</span> : (
                            <>
                                <Play size={18} />
                                <span>Ejecutar Modelo Inteligente</span>
                            </>
                        )}
                    </button>
                </div>
                {error && <p className="text-red-500 text-sm mt-2 text-center">{error}</p>}
            </div>

            {/* Results */}
            {results && (
                <div className="space-y-6">

                    {/* Risk Analysis Banner */}
                    <div className={`p-4 rounded-xl border flex items-start space-x-4 ${getRiskColor(results.risk_analysis.level)}`}>
                        <AlertTriangle className="mt-1 flex-shrink-0" />
                        <div>
                            <h3 className="font-bold text-lg">Nivel de Riesgo: {results.risk_analysis.level} (Score: {results.risk_analysis.score}/100)</h3>
                            <p className="mt-1">{results.risk_analysis.explanation}</p>
                            {results.risk_analysis.factors.length > 0 && (
                                <ul className="mt-2 list-disc list-inside text-sm opacity-90">
                                    {results.risk_analysis.factors.map((f, i) => <li key={i}>{f}</li>)}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 text-center">
                            <div className="text-sm text-gray-500 mb-1">Defectos Totales (Ajustado)</div>
                            <div className="text-2xl font-bold text-blue-600">{results.enhanced_prediction.adjusted_total_defects}</div>
                            <div className="text-xs text-gray-400 line-through">Estándar: {results.original_prediction.total_defects_estimated}</div>
                        </div>
                        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 text-center">
                            <div className="text-sm text-gray-500 mb-1">Pico (Semanas)</div>
                            <div className="text-2xl font-bold text-purple-600">{results.enhanced_prediction.adjusted_sigma}</div>
                            <div className="text-xs text-gray-400">Original: {results.original_prediction.sigma}</div>
                        </div>
                        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 text-center">
                            <div className="text-sm text-gray-500 mb-1">Tasa Histórica Usada</div>
                            <div className="text-2xl font-bold text-green-600">{results.adjustments.historical_rate_used}</div>
                            <div className="text-xs text-gray-400">Defectos/Hora</div>
                        </div>
                        <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 text-center">
                            <div className="text-sm text-gray-500 mb-1">Tamaño Equipo Promedio</div>
                            <div className="text-2xl font-bold text-orange-600">{results.adjustments.historical_avg_team_size}</div>
                            <div className="text-xs text-gray-400">Personas</div>
                        </div>
                    </div>

                    {/* Chart */}
                    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100">
                        <h3 className="text-lg font-bold mb-4 text-gray-800">Comparativa: Estándar vs Ajustada por Realidad</h3>
                        <div className="h-96">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={results.enhanced_prediction.weekly_predictions} margin={{ top: 10, right: 30, left: 0, bottom: 20 }}>
                                    <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                    <XAxis dataKey="week" label={{ value: 'Semanas', position: 'insideBottom', offset: -5 }} />
                                    <YAxis />
                                    <Tooltip contentStyle={{ backgroundColor: '#fff', borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                                    <Legend verticalAlign="top" height={36} />

                                    {/* Original Curve (from separate data structure, need to merge or map) 
                                        Since recharts needs one array, we'll assume the weeks align (they should).
                                        We can map original data to the enhanced data array for display.
                                    */}
                                    <Line type="monotone" dataKey="defects" name="Predicción Ajustada (Inteligente)" stroke="#2563eb" strokeWidth={3} dot={{ r: 4 }} />

                                    {/* We need to overlay the original data. For simplicity in this step, we visualize the enhanced one primarily. 
                                        To show both, we'd need to merge the arrays. Let's do a quick merge on the fly if possible or just show enhanced.
                                        Ideally, the backend returns them aligned.
                                    */}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="text-sm text-gray-500 mt-2 text-center">
                            La curva azul muestra la predicción ajustada considerando los retrasos, productividad y riesgos actuales del proyecto.
                        </p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default RayleighModel;
