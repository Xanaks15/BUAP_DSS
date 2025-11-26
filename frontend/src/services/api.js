import axios from 'axios';

const API_URL = 'http://127.0.0.1:8001';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getGeneralKPIs = async () => {
    const response = await api.get('/dashboard/kpis/general');
    return response.data;
};

export const getProjects = async (limit = 100) => {
    const response = await api.get(`/dashboard/projects?limit=${limit}`);
    return response.data;
};

export const getProjectMetrics = async (projectId) => {
    const response = await api.get(`/dashboard/projects/${projectId}/metrics`);
    return response.data;
};

export const getProjectQuality = async (projectId) => {
    const response = await api.get(`/dashboard/projects/${projectId}/quality`);
    return response.data;
};

export const predictDefects = async (data) => {
    const response = await api.post('/predictions/predict', data, {
        headers: { 'X-Role': 'ProjectManager' }
    });
    return response.data;
};

export default api;
