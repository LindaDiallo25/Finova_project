import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_URL,
});

export const analysisApi = {
  uploadFile: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await apiClient.post('/api/analysis/upload-file', formData);
    return response.data;
  },

  getAnalysis: async (analysisId) => {
    const response = await apiClient.get(`/api/analysis/analysis/${analysisId}`);
    return response.data;
  },

  generateScenarios: async (analysisId) => {
    const response = await apiClient.post(`/api/analysis/generate-scenarios/${analysisId}`);
    return response.data;
  },

  getScenarios: async (analysisId) => {
    const response = await apiClient.get(`/api/analysis/scenarios/${analysisId}`);
    return response.data;
  },

  healthCheck: async () => {
    const response = await apiClient.get('/api/health/');
    return response.data;
  }
};
