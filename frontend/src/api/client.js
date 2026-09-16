const API_BASE = 'http://localhost:8000';

function getAuthHeaders(isFormData = false) {
  const token = localStorage.getItem('mota_token');
  const headers = {};
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  if (!isFormData) {
    headers['Content-Type'] = 'application/json';
  }
  return headers;
}

async function request(endpoint, options = {}) {
  const isFormData = options.body instanceof FormData;
  const headers = { ...getAuthHeaders(isFormData), ...options.headers };
  
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorMsg = 'An unexpected error occurred';
    try {
      const errData = await response.json();
      errorMsg = errData.detail || errData.message || errorMsg;
    } catch (_) {}
    throw new Error(errorMsg);
  }

  return response.json();
}

export const api = {
  auth: {
    login: (email, password) =>
      request('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify({ email, password }),
      }),
    register: (userData) =>
      request('/api/auth/register', {
        method: 'POST',
        body: JSON.stringify(userData),
      }),
    getMe: () => request('/api/auth/me'),
  },

  schemes: {
    getAll: () => request('/api/schemes'),
    getById: (id) => request(`/api/schemes/${id}`),
  },

  documents: {
    scan: (docType, hints, file) => {
      const formData = new FormData();
      formData.append('doc_type', docType);
      formData.append('form_hints_json', JSON.stringify(hints || {}));
      formData.append('file', file);
      return request('/api/documents/scan', {
        method: 'POST',
        body: formData,
      });
    },
  },

  applications: {
    submit: (payload) =>
      request('/api/applications/apply', {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
    getMy: () => request('/api/applications/my'),
    getDetail: (id) => request(`/api/applications/${id}`),
    resubmit: (id, payload) =>
      request(`/api/applications/${id}/resubmit`, {
        method: 'POST',
        body: JSON.stringify(payload),
      }),
  },

  admin: {
    getApplications: (params = {}) => {
      const query = new URLSearchParams();
      if (params.scheme) query.append('scheme', params.scheme);
      if (params.status) query.append('status', params.status);
      if (params.state) query.append('state', params.state);
      if (params.search) query.append('search', params.search);
      return request(`/api/admin/applications?${query.toString()}`);
    },
    getApplicationDetail: (id) => request(`/api/admin/applications/${id}`),
    takeAction: (id, actionData) =>
      request(`/api/admin/applications/${id}/action`, {
        method: 'POST',
        body: JSON.stringify(actionData),
      }),
    getMeritRanking: (weights = { marks_weight: 0.7, income_weight: 0.3 }) =>
      request('/api/admin/merit-ranking', {
        method: 'POST',
        body: JSON.stringify(weights),
      }),
    getAnalytics: () => request('/api/admin/analytics'),
  },
};
