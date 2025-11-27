import React from 'react';

const PerspectiveCard = ({ title, objectives, color }) => (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
        <h3 className={`text-lg font-bold mb-4 ${color}`}>{title}</h3>
        <div className="space-y-6">
            {objectives.map((obj, idx) => (
                <div key={idx} className="space-y-3">
                    <h4 className="font-medium text-gray-800">{obj.name}</h4>
                    <div className="space-y-2">
                        {obj.krs.map((kr, kIdx) => (
                            <div key={kIdx} className="bg-gray-50 p-3 rounded-lg text-sm">
                                <div className="flex justify-between mb-1">
                                    <span className="text-gray-600">{kr.name}</span>
                                    <span className={`font-semibold ${kr.status === 'success' ? 'text-green-600' : kr.status === 'warning' ? 'text-yellow-600' : 'text-red-600'}`}>
                                        {kr.value} <span className="text-xs text-gray-400 font-normal">(Meta: {kr.goal})</span>
                                    </span>
                                </div>
                                <div className="w-full bg-gray-200 rounded-full h-1.5">
                                    <div
                                        className={`h-1.5 rounded-full ${kr.status === 'success' ? 'bg-green-500' : kr.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'}`}
                                        style={{ width: kr.progress }}
                                    ></div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            ))}
        </div>
    </div>
);

const BalancedScorecard = () => {
    // Mock data based on specification
    const perspectives = [
        {
            title: "Financiera",
            color: "text-blue-600",
            objectives: [
                {
                    name: "F1. Asegurar la rentabilidad de los proyectos",
                    krs: [
                        { name: "F1.1 ROI promedio ≥ 12%", value: "15%", goal: "12%", progress: "100%", status: "success" },
                        { name: "F1.2 Desviación de costos ≤ 10%", value: "8%", goal: "10%", progress: "100%", status: "success" },
                        { name: "F1.3 ≥ 85% proyectos con ganancia > 0", value: "82%", goal: "85%", progress: "96%", status: "warning" }
                    ]
                }
            ]
        },
        {
            title: "Cliente",
            color: "text-green-600",
            objectives: [
                {
                    name: "C1. Entregar productos confiables y a tiempo",
                    krs: [
                        { name: "C1.1 ≥ 90% entregados a tiempo", value: "88%", goal: "90%", progress: "97%", status: "warning" },
                        { name: "C1.2 ≥ 95% sin defectos críticos", value: "92%", goal: "95%", progress: "96%", status: "warning" },
                        { name: "C1.3 ≥ 80% con retrasos ≤ 20%", value: "75%", goal: "80%", progress: "93%", status: "red" }
                    ]
                }
            ]
        },
        {
            title: "Procesos Internos",
            color: "text-purple-600",
            objectives: [
                {
                    name: "P1. Optimizar desarrollo y pruebas",
                    krs: [
                        { name: "P1.1 Defectos promedio ≤ 25", value: "22", goal: "25", progress: "100%", status: "success" },
                        { name: "P1.2 ≥ 90% tareas completadas", value: "94%", goal: "90%", progress: "100%", status: "success" },
                        { name: "P1.3 Pico defectos en primer 40%", value: "35%", goal: "40%", progress: "100%", status: "success" }
                    ]
                }
            ]
        },
        {
            title: "Aprendizaje y Crecimiento",
            color: "text-orange-600",
            objectives: [
                {
                    name: "A1. Fortalecer capacidad del equipo",
                    krs: [
                        { name: "A1.1 Productividad horas ≥ 85%", value: "87%", goal: "85%", progress: "100%", status: "success" },
                        { name: "A1.2 Uso modelo predictivo ≥ 70%", value: "60%", goal: "70%", progress: "85%", status: "red" }
                    ]
                }
            ]
        }
    ];

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-2xl font-bold text-gray-800">Balanced Scorecard</h2>
                <p className="text-gray-500">Monitoreo de objetivos estratégicos y OKRs</p>
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
