import React, { useEffect, useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ComposedChart, Line, Bar } from 'recharts';
import { predictDefects } from '../services/api';

const RayleighCurves = ({ projectData }) => {
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (projectData) {
            // Mock inputs for prediction based on project data
            // In real app, these would come from project estimation inputs
            const fetchPrediction = async () => {
                setLoading(true);
                try {
                    // Estimate inputs
                    const totalDefects = Math.max(50, Math.floor(projectData.pv / 1000)); // Rough estimate
                    const duration = 20; // weeks
                    const peak = duration * 0.4; // Peak usually at 40%

                    const data = await predictDefects({
                        total_defects: totalDefects,
                        peak_time: peak,
                        duration_weeks: duration
                    });
                    setPrediction(data);
                } catch (error) {
                    console.error("Prediction error:", error);
                } finally {
                    setLoading(false);
                }
            };
            fetchPrediction();
        }
    }, [projectData]);

    if (loading || !prediction) return <div>Loading Rayleigh Model...</div>;

    return (
        <div className="space-y-6 mt-8">
            <h2 className="text-xl font-bold text-corporate-dark border-b pb-2">2. Curvas Rayleigh (Defectos y Esfuerzo)</h2>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Defect Curve */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-corporate-blue">Defectos Esperados vs Reales</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <ComposedChart data={prediction.weekly_predictions}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="week" label={{ value: 'Semana', position: 'insideBottom', offset: -5 }} />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Area type="monotone" dataKey="defects" fill="#E0F2FE" stroke="#0074C8" name="Rayleigh Est." />
                                {/* Mock Real Data */}
                                <Bar dataKey="defects" fill="#00A65A" name="Defectos Reales" barSize={10} fillOpacity={0.6} />
                            </ComposedChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="mt-4 text-sm text-gray-600 grid grid-cols-2 gap-4">
                        <div><strong>Total Est:</strong> {prediction.total_defects_estimated}</div>
                        <div><strong>Peak Week:</strong> {prediction.peak_week}</div>
                    </div>
                </div>

                {/* Effort Profile (Staffing) - Mocked for now as Rayleigh PDF also applies to staffing */}
                <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
                    <h3 className="text-lg font-semibold mb-4 text-corporate-blue">Perfil de Esfuerzo (Staffing)</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={prediction.weekly_predictions}>
                                <CartesianGrid strokeDasharray="3 3" vertical={false} />
                                <XAxis dataKey="week" />
                                <YAxis />
                                <Tooltip />
                                <Legend />
                                <Area type="monotone" dataKey="cumulative" stackId="1" stroke="#82ca9d" fill="#82ca9d" name="Esfuerzo Acumulado" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RayleighCurves;
