import type { User, JobMatchesResponse, StudentProfile, Job } from '../types';

const ACCESS_TOKEN_KEY = 'careersync_access_token';
const REFRESH_TOKEN_KEY = 'careersync_refresh_token';

export function getStoredAccessToken(): string | null {
  try {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getStoredRefreshToken(): string | null {
  try {
    return localStorage.getItem(REFRESH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setStoredTokens(tokens: { access?: string; refresh?: string }) {
  try {
    if (tokens.access) localStorage.setItem(ACCESS_TOKEN_KEY, tokens.access);
    if (tokens.refresh) localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh);
  } catch (e) {
    console.warn('Failed to save tokens in localStorage:', e);
  }
}

export function clearStoredTokens() {
  try {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
  } catch (e) {
    console.warn('Failed to clear tokens from localStorage:', e);
  }
}

function extractAndSaveTokens(res: any) {
  if (res && typeof res === 'object') {
    const access = res.access || res.tokens?.access;
    const refresh = res.refresh || res.tokens?.refresh;
    if (access || refresh) {
      setStoredTokens({ access, refresh });
    }
  }
}

let envApiUrl = (import.meta as any).env?.VITE_API_URL;
// Auto-correct missing unique suffix if misconfigured in deployment environment variables
if (envApiUrl && envApiUrl.includes('careersync-api.onrender.com') && !envApiUrl.includes('careersync-api-unpo.onrender.com')) {
  envApiUrl = envApiUrl.replace('careersync-api.onrender.com', 'careersync-api-unpo.onrender.com');
}
const isDev = Boolean((import.meta as any).env?.DEV);

// Use explicit environment variable if set.
// Otherwise, in local dev use '/api' (proxied by Vite to 127.0.0.1:8000).
// In production builds, default directly to the live Render backend URL so requests never fail due to missing env vars.
const BASE_URL = envApiUrl
  ? (envApiUrl.endsWith('/api') ? envApiUrl : `${envApiUrl.replace(/\/$/, '')}/api`)
  : isDev
  ? '/api'
  : 'https://careersync-api-unpo.onrender.com/api';

async function request<T>(endpoint: string, options: RequestInit = {}, isRetry: boolean = false): Promise<T> {
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers as Record<string, string> || {}),
  };

  const token = getStoredAccessToken();
  if (token && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${endpoint}`, {
      ...options,
      headers,
      credentials: 'include', // important for session cookies & cross-origin hybrid
    });
  } catch (err: any) {
    throw new Error(
      'Unable to connect to CareerSync server. If the server was idle, Render may be waking up (takes ~30-50s on free tier). Please retry in a few moments.'
    );
  }

  // Handle Token Expiry & Automatic Refresh on 401
  if (response.status === 401 && !isRetry && !endpoint.includes('/auth/login') && !endpoint.includes('/auth/register') && !endpoint.includes('/auth/token/refresh')) {
    const refreshToken = getStoredRefreshToken();
    if (refreshToken) {
      try {
        const refreshResp = await fetch(`${BASE_URL}/auth/token/refresh/`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
          body: JSON.stringify({ refresh: refreshToken }),
        });
        if (refreshResp.ok) {
          const refreshData = await refreshResp.json();
          if (refreshData.access) {
            setStoredTokens({ access: refreshData.access });
            const retryHeaders = {
              ...headers,
              Authorization: `Bearer ${refreshData.access}`,
            };
            return request<T>(endpoint, { ...options, headers: retryHeaders }, true);
          }
        } else {
          clearStoredTokens();
        }
      } catch {
        clearStoredTokens();
      }
    }
  }

  const contentType = response.headers.get('content-type') || '';
  let data: any = null;

  if (contentType.includes('application/json')) {
    data = await response.json();
  } else {
    const rawText = await response.text();
    if (rawText.trim().startsWith('<!doctype') || rawText.trim().startsWith('<html')) {
      throw new Error(
        'Backend connection error: The API request was handled by the static frontend server instead of your Render backend. Please set VITE_API_URL in your Vercel project settings to your Render backend URL.'
      );
    }
    data = rawText;
  }

  if (!response.ok) {
    let errorMsg = `Request failed with status ${response.status}`;
    if (data && typeof data === 'object') {
      if (data.error) {
        errorMsg = data.error;
      } else if (data.message) {
        errorMsg = data.message;
      } else {
        errorMsg = Object.values(data).flat().join(' ');
      }
    } else if (typeof data === 'string' && data.length > 0) {
      errorMsg = data.slice(0, 200);
    }
    throw new Error(errorMsg);
  }

  return data as T;
}

export const api = {
  // Auth
  async getCurrentUser(): Promise<User | null> {
    try {
      const res = await request<any>('/auth/me/');
      if (!res || typeof res !== 'object' || res.authenticated === false || !res.email) {
        return null;
      }
      return res as User;
    } catch {
      return null;
    }
  },

  async login(email: string, password: string): Promise<User> {
    const res = await request<User>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    extractAndSaveTokens(res);
    return res;
  },

  async demoLogin(accountType: 'student' | 'admin'): Promise<User> {
    const res = await request<User>('/auth/demo-login/', {
      method: 'POST',
      body: JSON.stringify({ account_type: accountType }),
    });
    extractAndSaveTokens(res);
    return res;
  },

  async register(data: any): Promise<User> {
    const res = await request<User>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
    extractAndSaveTokens(res);
    return res;
  },

  async logout(): Promise<void> {
    try {
      await request('/auth/logout/', {
        method: 'POST',
      });
    } finally {
      clearStoredTokens();
    }
  },

  async refreshToken(): Promise<string | null> {
    const refreshToken = getStoredRefreshToken();
    if (!refreshToken) return null;
    try {
      const res = await fetch(`${BASE_URL}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
        body: JSON.stringify({ refresh: refreshToken }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.access) {
          setStoredTokens({ access: data.access });
          return data.access;
        }
      }
    } catch {
      clearStoredTokens();
    }
    return null;
  },

  // Student Profile
  async getProfile(): Promise<StudentProfile> {
    return request<StudentProfile>('/profile/');
  },

  async updateProfile(data: Partial<StudentProfile>): Promise<StudentProfile> {
    return request<StudentProfile>('/profile/', {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Jobs
  async getJobMatches(params: {
    status?: string;
    q?: string;
    category?: string;
    qualification?: string;
  } = {}): Promise<JobMatchesResponse> {
    const query = new URLSearchParams();
    if (params.status) query.set('status', params.status);
    if (params.q) query.set('q', params.q);
    if (params.category && params.category !== 'all') query.set('category', params.category);
    if (params.qualification && params.qualification !== 'all') query.set('qualification', params.qualification);

    return request<JobMatchesResponse>(`/jobs/matches/?${query.toString()}`);
  },

  async getPublicJobs(params: { q?: string; category?: string; qualification?: string } = {}): Promise<Job[]> {
    const query = new URLSearchParams();
    if (params.q) query.set('q', params.q);
    if (params.category && params.category !== 'all') query.set('category', params.category);
    if (params.qualification && params.qualification !== 'all') query.set('qualification', params.qualification);
    return request<Job[]>(`/jobs/?${query.toString()}`);
  },

  async getCategories(): Promise<{ category: string; count: number }[]> {
    return request<{ category: string; count: number }[]>('/jobs/categories/');
  },

  // Custom Admin API
  async getAdminStats(): Promise<{
    total_jobs: number;
    published_jobs: number;
    pending_review_jobs?: number;
    draft_jobs?: number;
    rejected_jobs?: number;
    active_jobs: number;
    expired_jobs: number;
    total_students: number;
    total_notifications_sent: number;
    category_breakdown: { category: string; count: number }[];
  }> {
    return request('/admin/stats/');
  },

  async getAdminJobs(params: { status?: string; q?: string } = {}): Promise<Job[]> {
    const query = new URLSearchParams();
    if (params.status && params.status !== 'all') query.set('status', params.status);
    if (params.q) query.set('q', params.q);
    return request(`/admin/jobs/?${query.toString()}`);
  },

  async createAdminJob(data: any): Promise<{ job: Job; notifications_sent: number; message: string }> {
    return request('/admin/jobs/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async updateAdminJob(id: number, data: any): Promise<{ job: Job; notifications_sent: number; message: string }> {
    return request(`/admin/jobs/${id}/`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  async deleteAdminJob(id: number): Promise<{ message: string }> {
    return request(`/admin/jobs/${id}/`, {
      method: 'DELETE',
    });
  },

  async togglePublishAdminJob(id: number): Promise<{ is_published: boolean; status: string; notifications_sent: number; message: string }> {
    return request(`/admin/jobs/${id}/toggle-publish/`, {
      method: 'POST',
    });
  },

  // AI Assisted Extraction Endpoints
  async getAiStatus(): Promise<{
    gemini_configured: boolean;
    default_model: string;
    supported_models: string[];
    fallback_engine: string;
  }> {
    return request('/admin/ai-status/');
  },

  async testGeminiKey(apiKey: string): Promise<{ valid: boolean; model?: string; message?: string; error?: string }> {
    return request('/admin/ai-status/', {
      method: 'POST',
      body: JSON.stringify({ api_key: apiKey }),
    });
  },

  async extractJobFromUrl(url: string): Promise<{ job: Job; metadata: any; message: string }> {
    return request('/admin/jobs/extract-url/', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  },

  async extractJobFromPdf(file: File): Promise<{ job: Job; metadata: any; message: string }> {
    const formData = new FormData();
    formData.append('pdf_file', file);
    return request('/admin/jobs/extract-pdf/', {
      method: 'POST',
      body: formData,
    });
  },

  async approveAdminJob(id: number, reviewNotes?: string): Promise<{ job: Job; notifications_sent: number; message: string }> {
    return request(`/admin/jobs/${id}/approve/`, {
      method: 'POST',
      body: JSON.stringify({ review_notes: reviewNotes || '' }),
    });
  },

  async rejectAdminJob(id: number, reviewNotes?: string): Promise<{ job: Job; message: string }> {
    return request(`/admin/jobs/${id}/reject/`, {
      method: 'POST',
      body: JSON.stringify({ review_notes: reviewNotes || '' }),
    });
  },

  async getAdminStudents(): Promise<any[]> {
    return request('/admin/students/');
  },

  async runAutoDiscover(limit: number = 3): Promise<{ report: any; message: string; ingested_count: number }> {
    return request('/admin/jobs/auto-discover/', {
      method: 'POST',
      body: JSON.stringify({ limit }),
    });
  },
};
