import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import BalancedScorecard from './pages/BalancedScorecard';
import RayleighModel from './pages/RayleighModel';
import Welcome from './pages/Welcome';
import Login from './pages/Login';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    const location = useLocation();

    if (!isAuthenticated) {
        // Redirect to login, but save the location they were trying to go to
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return children;
};

// Welcome Guard Component
const WelcomeGuard = ({ children }) => {
    const seenWelcome = localStorage.getItem('seen_welcome') === 'true';

    if (!seenWelcome) {
        return <Navigate to="/welcome" replace />;
    }

    return children;
};

function App() {
    return (
        <Router future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
            <Routes>
                {/* Welcome Route (No Layout) */}
                <Route path="/welcome" element={<Welcome />} />

                {/* Login Route (No Layout) */}
                <Route path="/login" element={<Login />} />

                {/* Main App Routes (With Layout & Guards) */}
                <Route
                    path="*"
                    element={
                        <WelcomeGuard>
                            <Layout>
                                <Routes>
                                    <Route path="/" element={<Dashboard />} />
                                    <Route path="/dashboard" element={<Dashboard />} />
                                    <Route path="/bsc" element={<BalancedScorecard />} />
                                    <Route
                                        path="/rayleigh"
                                        element={
                                            <ProtectedRoute>
                                                <RayleighModel />
                                            </ProtectedRoute>
                                        }
                                    />
                                </Routes>
                            </Layout>
                        </WelcomeGuard>
                    }
                />
            </Routes>
        </Router>
    );
}

export default App;
