import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LayoutDashboard, BarChart3, TrendingUp, LogOut } from 'lucide-react';

const Layout = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: LayoutDashboard },
        { path: '/bsc', label: 'Balanced Scorecard', icon: BarChart3 },
        { path: '/rayleigh', label: 'Modelo Rayleigh', icon: TrendingUp },
    ];

    const handleLogout = () => {
        localStorage.removeItem('isAuthenticated');
        window.location.href = '/';
    };

    return (
        <div className="min-h-screen bg-gray-50 flex flex-col">
            {/* Top Navbar */}
            <header className="bg-white shadow-sm z-10">
                <div className="w-full px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        {/* Logo & Brand */}
                        <div className="flex items-center">
                            <div className="flex-shrink-0 flex items-center">
                                <h1 className="text-2xl font-bold text-corporate-blue">NESKAN-DSS</h1>
                                <span className="ml-2 text-xs text-gray-400 hidden sm:block">Decision Support System</span>
                            </div>

                            {/* Desktop Nav */}
                            <nav className="hidden sm:ml-10 sm:flex sm:space-x-8">
                                {navItems.map((item) => {
                                    const Icon = item.icon;
                                    const isActive = location.pathname === item.path;
                                    return (
                                        <Link
                                            key={item.path}
                                            to={item.path}
                                            onClick={() => {
                                                if (item.path === '/welcome') {
                                                    localStorage.removeItem('seen_welcome');
                                                }
                                            }}
                                            className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium transition-colors ${isActive
                                                ? 'border-corporate-blue text-gray-900'
                                                : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                                                }`}
                                        >
                                            <Icon size={16} className="mr-2" />
                                            {item.label}
                                        </Link>
                                    );
                                })}
                            </nav>
                        </div>

                        {/* Right Side (Logout/User) */}
                        <div className="flex items-center">
                            {localStorage.getItem('isAuthenticated') && (
                                <button
                                    onClick={handleLogout}
                                    className="text-gray-500 hover:text-red-600 p-2 rounded-full transition-colors"
                                    title="Cerrar Sesión"
                                >
                                    <LogOut size={20} />
                                </button>
                            )}
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="flex-1">
                <div className="w-full py-8 px-4 sm:px-6 lg:px-8">
                    {children}
                </div>
            </main>
        </div>
    );
};

export default Layout;
