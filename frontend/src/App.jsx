import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import BalancedScorecard from './pages/BalancedScorecard';
import RayleighModel from './pages/RayleighModel';

function App() {
    return (
        <Router>
            <Layout>
                <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/bsc" element={<BalancedScorecard />} />
                    <Route path="/rayleigh" element={<RayleighModel />} />
                </Routes>
            </Layout>
        </Router>
    );
}

export default App;
