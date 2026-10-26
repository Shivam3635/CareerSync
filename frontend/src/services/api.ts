import type { User, JobMatchesResponse, StudentProfile, Job } from '../types';

const BASE_URL = '/api';

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const isFormData = typeof FormData !== 'undefined' && options.body instanceof FormData;
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...(isFormData ? {} : { 'Content-Type': 'application/json' }),
    ...(options.headers as Record<string, string> || {}),
  };

  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // important for session cookies
  });

  const contentType = response.headers.get('content-type');
  let data: any = null;
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
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
    }
    throw new Error(errorMsg);
  }

  return data as T;
}

export const api = {
  // Auth
  async getCurrentUser(): Promise<User | null> {
    const res = await request<any>('/auth/me/');
    if (res && res.authenticated === false) {
      return null;
    }
    return res as User;
  },

  async login(email: string, password: string): Promise<User> {
    return request<User>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  },

  async demoLogin(accountType: 'student' | 'admin'): Promise<User> {
    return request<User>('/auth/demo-login/', {
      method: 'POST',
      body: JSON.stringify({ account_type: accountType }),
    });
  },

  async register(data: any): Promise<User> {
    return request<User>('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  async logout(): Promise<void> {
    await request('/auth/logout/', {
      method: 'POST',
    });
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
};
