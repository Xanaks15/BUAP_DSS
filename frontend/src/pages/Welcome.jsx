import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, Zap, Search, ChevronRight } from 'lucide-react';

const Welcome = () => {
    const navigate = useNavigate();
    const [showFullText, setShowFullText] = useState(false);

    // Removed auto-redirect to allow viewing Welcome page anytime

    const handleEnter = () => {
        localStorage.setItem('seen_welcome', 'true');
        navigate('/dashboard');
    };

    const MISSION_SHORT = "Desarrollar soluciones de software de alta calidad que optimicen los procesos de nuestros clientes mediante la innovación tecnológica...";
    const MISSION_FULL = "Desarrollar soluciones de software de alta calidad que optimicen los procesos de nuestros clientes mediante la innovación tecnológica, la eficiencia operativa y la mejora continua; ofreciendo productos sostenibles, escalables y alineados con las necesidades de negocio mientras se promueve la trazabilidad, la colaboración interdisciplinaria y el uso ético de los datos.";

    const VISION_SHORT = "Ser una empresa líder en el desarrollo de software inteligente que impulse la transformación digital a través de soluciones confiables...";
    const VISION_FULL = "Ser una empresa líder en el desarrollo de software inteligente que impulse la transformación digital a través de soluciones confiables, medibles y centradas en la toma de decisiones basadas en datos. Aspiramos a consolidarnos como un referente en la creación de plataformas donde la analítica de desempeño, la gestión del conocimiento y la automatización se integren para orientar la estrategia empresarial hacia la excelencia y la innovación sostenible.";

    return (
        <div className="h-screen overflow-hidden bg-white font-sans text-gray-900 flex flex-col">
            {/* Skip Link */}
            <button
                onClick={handleEnter}
                className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 bg-blue-600 text-white px-4 py-2 rounded-md z-50"
            >
                Saltar bienvenida y entrar al DSS
            </button>

            {/* Hero Section */}
            <section className="flex-1 flex items-center relative overflow-hidden">
                <div className="container mx-auto px-4 py-6 lg:py-10 grid lg:grid-cols-2 gap-8 items-center relative z-10">

                    {/* Text Content */}
                    <div className="space-y-6 animate-fade-in-up">
                        <div>
                            <div className="flex items-center space-x-2 mb-3">
                                <div className="w-8 h-8 bg-corporate-blue rounded-lg flex items-center justify-center">
                                    <span className="text-white font-bold text-lg">D</span>
                                </div>
                                <span className="text-xl font-bold text-gray-900 tracking-tight">NESKAN-DSS</span>
                            </div>
                            <h1 className="text-3xl lg:text-5xl font-extrabold tracking-tight text-gray-900 mb-4">
                                Plataforma <span className="text-corporate-blue">DSS</span>
                            </h1>

                            {/* Mission / Vision */}
                            <div className="bg-gray-50 p-5 rounded-xl border border-gray-100 shadow-sm">
                                <div className="space-y-3">
                                    <div>
                                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Misión</h3>
                                        <p className="text-sm text-gray-700 leading-relaxed">
                                            {showFullText ? MISSION_FULL : MISSION_SHORT}
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-1">Visión</h3>
                                        <p className="text-sm text-gray-700 leading-relaxed">
                                            {showFullText ? VISION_FULL : VISION_SHORT}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setShowFullText(!showFullText)}
                                        className="text-corporate-blue text-xs font-semibold hover:text-blue-800 flex items-center transition-colors"
                                    >
                                        {showFullText ? "Ver menos" : "Ver completa"}
                                        <ChevronRight size={14} className={`ml-1 transform transition-transform ${showFullText ? 'rotate-90' : ''}`} />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Value Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="w-8 h-8 bg-blue-50 rounded-full flex items-center justify-center mb-2 text-blue-600">
                                    <Search size={16} />
                                </div>
                                <h3 className="font-bold text-gray-900 text-sm mb-1">Trazabilidad</h3>
                                <p className="text-xs text-gray-500">Seguimiento total del ciclo de vida.</p>
                            </div>
                            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="w-8 h-8 bg-purple-50 rounded-full flex items-center justify-center mb-2 text-purple-600">
                                    <BarChart3 size={16} />
                                </div>
                                <h3 className="font-bold text-gray-900 text-sm mb-1">Decisiones</h3>
                                <p className="text-xs text-gray-500">Basadas en datos reales y métricas.</p>
                            </div>
                            <div className="bg-white p-3 rounded-xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="w-8 h-8 bg-green-50 rounded-full flex items-center justify-center mb-2 text-green-600">
                                    <Zap size={16} />
                                </div>
                                <h3 className="font-bold text-gray-900 text-sm mb-1">Eficiencia</h3>
                                <p className="text-xs text-gray-500">Optimización operativa continua.</p>
                            </div>
                        </div>

                        {/* Predictive Models Highlight */}
                        <div className="mt-4 bg-gradient-to-r from-blue-50 to-purple-50 p-3 rounded-xl border border-blue-100">
                            <h3 className="font-bold text-gray-900 text-sm mb-1 flex items-center">
                                <span className="mr-2">🤖</span> Modelo Predictivo
                            </h3>
                            <p className="text-xs text-gray-600">
                                Incorporamos el <strong>Modelo Rayleigh</strong> para la estimación precisa de defectos.
                            </p>
                        </div>

                        {/* CTAs */}
                        <div className="flex flex-col sm:flex-row gap-4 pt-2">
                            <button
                                onClick={handleEnter}
                                className="bg-blue-600 text-white rounded-lg px-6 py-3 font-semibold text-base hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-200 transform hover:-translate-y-1"
                                aria-label="Entrar al Dashboard del Sistema de Soporte a Decisiones"
                            >
                                Entrar al DSS
                            </button>

                        </div>
                    </div>

                    {/* Dashboard Preview */}
                    <div className="hidden lg:flex justify-center items-center relative h-full">
                        <div className="absolute inset-0 bg-gradient-to-tr from-blue-100/50 to-purple-100/50 rounded-full filter blur-3xl opacity-50"></div>

                        <div className="relative z-10 w-full max-w-xl bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden transform rotate-2 hover:rotate-0 transition-all duration-700">
                            <div className="flex h-64 md:h-72">
                                {/* Sidebar */}
                                <div className="w-14 bg-gray-50 border-r border-gray-100 flex flex-col items-center py-4 space-y-3">
                                    <div className="w-6 h-6 bg-blue-600 rounded-lg"></div>
                                    <div className="w-6 h-6 bg-gray-200 rounded-lg"></div>
                                    <div className="w-6 h-6 bg-gray-200 rounded-lg"></div>
                                    <div className="w-6 h-6 bg-gray-200 rounded-lg"></div>
                                </div>

                                {/* Main Content */}
                                <div className="flex-1 p-3 bg-gray-50/30 flex flex-col">
                                    {/* Header */}
                                    <div className="h-8 bg-white rounded-lg shadow-sm border border-gray-100 mb-3 flex items-center px-3 justify-between">
                                        <div className="w-20 h-2 bg-gray-200 rounded-full"></div>
                                        <div className="flex space-x-2">
                                            <div className="w-4 h-4 bg-gray-200 rounded-full"></div>
                                            <div className="w-4 h-4 bg-gray-200 rounded-full"></div>
                                        </div>
                                    </div>

                                    {/* Dashboard Grid */}
                                    <div className="grid grid-cols-3 gap-2 flex-1">
                                        {/* Large Card */}
                                        <div className="col-span-2 bg-white rounded-lg shadow-sm border border-gray-100 p-2">
                                            <div className="w-16 h-2 bg-gray-200 rounded-full mb-2"></div>
                                            <div className="flex items-end space-x-1 h-20 mt-1">
                                                <div className="w-full bg-blue-100 rounded-t-sm h-[40%]"></div>
                                                <div className="w-full bg-blue-200 rounded-t-sm h-[70%]"></div>
                                                <div className="w-full bg-blue-300 rounded-t-sm h-[50%]"></div>
                                                <div className="w-full bg-blue-400 rounded-t-sm h-[80%]"></div>
                                                <div className="w-full bg-blue-500 rounded-t-sm h-[60%]"></div>
                                            </div>
                                        </div>

                                        {/* Side Cards */}
                                        <div className="space-y-2">
                                            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-2 h-16">
                                                <div className="w-6 h-6 bg-green-100 rounded-full mb-1"></div>
                                                <div className="w-10 h-2 bg-gray-200 rounded-full"></div>
                                            </div>
                                            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-2 h-16">
                                                <div className="w-6 h-6 bg-purple-100 rounded-full mb-1"></div>
                                                <div className="w-10 h-2 bg-gray-200 rounded-full"></div>
                                            </div>
                                        </div>

                                        {/* Bottom Card */}
                                        <div className="col-span-3 bg-white rounded-lg shadow-sm border border-gray-100 p-2 h-12 flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-gray-100 rounded-full"></div>
                                            <div className="flex-1 space-y-1">
                                                <div className="w-full h-2 bg-gray-100 rounded-full"></div>
                                                <div className="w-2/3 h-2 bg-gray-100 rounded-full"></div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default Welcome;
