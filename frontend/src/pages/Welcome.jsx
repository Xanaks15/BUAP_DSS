import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { BarChart3, Zap, Search, ChevronRight } from 'lucide-react';

const Welcome = () => {
    const navigate = useNavigate();
    const [showFullText, setShowFullText] = useState(false);

    useEffect(() => {
        // Redirect if already seen (unless explicitly visiting /welcome via menu)
        // Note: This check might be handled in App.jsx guard, but good to have here too if accessed directly
        // However, if we want "View Welcome" to work, we shouldn't auto-redirect here if the user intended to come here.
        // The requirement says: "Al montar Welcome, si localStorage.getItem('seen_welcome') === 'true', redirigir a /dashboard."
        // BUT also: "Añadir en el menú un item “Ver bienvenida” que limpia la marca (removeItem('seen_welcome')) y lleva a /welcome."
        // So if we come from the menu, the flag is cleared, so we stay. If we come manually and flag is set, we redirect.
        if (localStorage.getItem('seen_welcome') === 'true') {
            navigate('/dashboard');
        }
    }, [navigate]);

    const handleEnter = () => {
        localStorage.setItem('seen_welcome', 'true');
        navigate('/dashboard');
    };



    const MISSION_SHORT = "Desarrollar soluciones de software de alta calidad que optimicen procesos con innovación, eficiencia y mejora continua...";
    const MISSION_FULL = "Desarrollar soluciones de software de alta calidad que optimicen procesos con innovación, eficiencia y mejora continua; sostenibles, escalables y alineadas al negocio, promoviendo trazabilidad, colaboración interdisciplinaria y uso ético de los datos.";

    const VISION_SHORT = "Ser líderes en software inteligente para la transformación digital con soluciones confiables, medibles y centradas en datos...";
    const VISION_FULL = "Ser líderes en software inteligente para la transformación digital con soluciones confiables, medibles y centradas en datos; integrando analítica de desempeño, gestión del conocimiento y automatización para impulsar la estrategia hacia la excelencia y la innovación sostenible.";

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
                <div className="container mx-auto px-4 py-10 lg:py-14 grid lg:grid-cols-2 gap-12 items-center relative z-10">

                    {/* Text Content */}
                    <div className="space-y-8 animate-fade-in-up">
                        <div>
                            <div className="flex items-center space-x-2 mb-4">
                                <div className="w-8 h-8 bg-corporate-blue rounded-lg flex items-center justify-center">
                                    <span className="text-white font-bold text-lg">D</span>
                                </div>
                                <span className="text-xl font-bold text-gray-900 tracking-tight">BUAP DSS</span>
                            </div>
                            <h1 className="text-4xl lg:text-6xl font-extrabold tracking-tight text-gray-900 mb-6">
                                Plataforma <span className="text-corporate-blue">DSS</span>
                            </h1>

                            {/* Mission / Vision */}
                            <div className="bg-gray-50 p-6 rounded-2xl border border-gray-100 shadow-sm">
                                <div className="space-y-4">
                                    <div>
                                        <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-1">Misión</h3>
                                        <p className="text-gray-700 leading-relaxed">
                                            {showFullText ? MISSION_FULL : MISSION_SHORT}
                                        </p>
                                    </div>
                                    <div>
                                        <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-1">Visión</h3>
                                        <p className="text-gray-700 leading-relaxed">
                                            {showFullText ? VISION_FULL : VISION_SHORT}
                                        </p>
                                    </div>
                                    <button
                                        onClick={() => setShowFullText(!showFullText)}
                                        className="text-corporate-blue text-sm font-semibold hover:text-blue-800 flex items-center transition-colors"
                                    >
                                        {showFullText ? "Ver menos" : "Ver completa"}
                                        <ChevronRight size={16} className={`ml-1 transform transition-transform ${showFullText ? 'rotate-90' : ''}`} />
                                    </button>
                                </div>
                            </div>
                        </div>

                        {/* Value Cards */}
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center mb-3 text-blue-600">
                                    <Search size={20} />
                                </div>
                                <h3 className="font-bold text-gray-900 mb-1">Trazabilidad</h3>
                                <p className="text-sm text-gray-500">Seguimiento total del ciclo de vida.</p>
                            </div>
                            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="w-10 h-10 bg-purple-50 rounded-full flex items-center justify-center mb-3 text-purple-600">
                                    <BarChart3 size={20} />
                                </div>
                                <h3 className="font-bold text-gray-900 mb-1">Decisiones</h3>
                                <p className="text-sm text-gray-500">Basadas en datos reales y métricas.</p>
                            </div>
                            <div className="bg-white p-4 rounded-2xl shadow-sm border border-gray-100 hover:shadow-md transition-shadow">
                                <div className="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center mb-3 text-green-600">
                                    <Zap size={20} />
                                </div>
                                <h3 className="font-bold text-gray-900 mb-1">Eficiencia</h3>
                                <p className="text-sm text-gray-500">Optimización operativa continua.</p>
                            </div>
                        </div>

                        {/* CTAs */}
                        <div className="flex flex-col sm:flex-row gap-4 pt-4">
                            <button
                                onClick={handleEnter}
                                className="bg-blue-600 text-white rounded-xl px-8 py-4 font-semibold text-lg hover:bg-blue-700 transition-all shadow-lg hover:shadow-blue-200 transform hover:-translate-y-1"
                                aria-label="Entrar al Dashboard del Sistema de Soporte a Decisiones"
                            >
                                Entrar al DSS
                            </button>

                        </div>
                    </div>

                    {/* Dashboard Preview */}
                    <div className="hidden lg:flex justify-center items-center relative h-full">
                        <div className="absolute inset-0 bg-gradient-to-tr from-blue-100/50 to-purple-100/50 rounded-full filter blur-3xl opacity-50"></div>

                        <div className="relative z-10 w-full max-w-2xl bg-white rounded-xl shadow-2xl border border-gray-200 overflow-hidden transform rotate-2 hover:rotate-0 transition-all duration-700">
                            <div className="flex h-64 md:h-80">
                                {/* Sidebar */}
                                <div className="w-16 md:w-20 bg-gray-50 border-r border-gray-100 flex flex-col items-center py-4 space-y-4">
                                    <div className="w-8 h-8 bg-blue-600 rounded-lg"></div>
                                    <div className="w-8 h-8 bg-gray-200 rounded-lg"></div>
                                    <div className="w-8 h-8 bg-gray-200 rounded-lg"></div>
                                    <div className="w-8 h-8 bg-gray-200 rounded-lg"></div>
                                </div>

                                {/* Main Content */}
                                <div className="flex-1 p-4 bg-gray-50/30 flex flex-col">
                                    {/* Header */}
                                    <div className="h-10 bg-white rounded-lg shadow-sm border border-gray-100 mb-4 flex items-center px-4 justify-between">
                                        <div className="w-24 h-3 bg-gray-200 rounded-full"></div>
                                        <div className="flex space-x-2">
                                            <div className="w-6 h-6 bg-gray-200 rounded-full"></div>
                                            <div className="w-6 h-6 bg-gray-200 rounded-full"></div>
                                        </div>
                                    </div>

                                    {/* Dashboard Grid */}
                                    <div className="grid grid-cols-3 gap-3 flex-1">
                                        {/* Large Card */}
                                        <div className="col-span-2 bg-white rounded-lg shadow-sm border border-gray-100 p-3">
                                            <div className="w-20 h-3 bg-gray-200 rounded-full mb-3"></div>
                                            <div className="flex items-end space-x-2 h-24 mt-2">
                                                <div className="w-full bg-blue-100 rounded-t-sm h-[40%]"></div>
                                                <div className="w-full bg-blue-200 rounded-t-sm h-[70%]"></div>
                                                <div className="w-full bg-blue-300 rounded-t-sm h-[50%]"></div>
                                                <div className="w-full bg-blue-400 rounded-t-sm h-[80%]"></div>
                                                <div className="w-full bg-blue-500 rounded-t-sm h-[60%]"></div>
                                            </div>
                                        </div>

                                        {/* Side Cards */}
                                        <div className="space-y-3">
                                            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-3 h-20">
                                                <div className="w-8 h-8 bg-green-100 rounded-full mb-2"></div>
                                                <div className="w-12 h-2 bg-gray-200 rounded-full"></div>
                                            </div>
                                            <div className="bg-white rounded-lg shadow-sm border border-gray-100 p-3 h-20">
                                                <div className="w-8 h-8 bg-purple-100 rounded-full mb-2"></div>
                                                <div className="w-12 h-2 bg-gray-200 rounded-full"></div>
                                            </div>
                                        </div>

                                        {/* Bottom Card */}
                                        <div className="col-span-3 bg-white rounded-lg shadow-sm border border-gray-100 p-3 h-16 flex items-center space-x-4">
                                            <div className="w-10 h-10 bg-gray-100 rounded-full"></div>
                                            <div className="flex-1 space-y-2">
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
