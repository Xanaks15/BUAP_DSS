import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000';

const api = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const getGeneralKPIs = async (filters = {}) => {
    // Map frontend filters to backend query params
    const params = {};
    if (filters.startDate) params.start_date = filters.startDate;
    if (filters.endDate) params.end_date = filters.endDate;
    if (filters.type && filters.type !== 'all') params.project_type = filters.type;
    if (filters.status && filters.status !== 'all') params.status = filters.status;
    if (filters.client && filters.client !== 'all') params.client = filters.client;

    const response = await api.get('/dashboard/kpis/general', { params });
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
