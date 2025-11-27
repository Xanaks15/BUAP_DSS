import React, { useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Lock } from 'lucide-react';

const Login = () => {
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const location = useLocation();

    // Get the page they were trying to visit
    const from = location.state?.from?.pathname || "/rayleigh";

    const handleLogin = (e) => {
        e.preventDefault();
        // Simple hardcoded password for demonstration
        if (password === 'admin123' || password === 'buap2025') {
            localStorage.setItem('isAuthenticated', 'true');
            navigate(from, { replace: true });
        } else {
            setError('Contraseña incorrecta');
        }
    };

    return (
        <div className="min-h-[80vh] flex items-center justify-center">
            <div className="bg-white p-8 rounded-xl shadow-lg border border-gray-100 w-full max-w-md">
                <div className="flex flex-col items-center mb-6">
                    <div className="bg-blue-50 p-3 rounded-full mb-4">
                        <Lock className="text-corporate-blue" size={32} />
                    </div>
                    <h2 className="text-2xl font-bold text-gray-800">Acceso Restringido</h2>
                    <p className="text-gray-500 text-center mt-2">
                        El Modelo Rayleigh es exclusivo para Project Managers.
                    </p>
                </div>

                <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña de Acceso</label>
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-corporate-blue focus:border-transparent outline-none transition-all"
                            placeholder="Ingrese su contraseña"
                            autoFocus
                        />
                    </div>

                    {error && (
                        <div className="text-red-500 text-sm bg-red-50 p-2 rounded border border-red-100 text-center">
                            {error}
                        </div>
                    )}

                    <button
                        type="submit"
                        className="w-full bg-corporate-blue text-white font-medium py-2.5 rounded-lg hover:bg-blue-700 transition-colors shadow-sm"
                    >
                        Ingresar
                    </button>
                </form>

                <div className="mt-6 text-center text-xs text-gray-400">
                    BUAP DSS &copy; 2025
                </div>
            </div>
        </div>
    );
};

export default Login;
