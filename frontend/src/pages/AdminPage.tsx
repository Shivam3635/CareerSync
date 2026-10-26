import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { Job } from '../types';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { AdminAddJobModal } from '../components/AdminAddJobModal';
import { DeleteConfirmModal } from '../components/DeleteConfirmModal';
import { 
  Search, 
  CheckCircle2, 
  Bell, 
  Trash2, 
  Edit3, 
  ExternalLink, 
  Sparkles,
  Layers,
  AlertTriangle,
  FileText,
  Globe,
  Clock,
  XCircle,
  FileCheck
} from 'lucide-react';

export const AdminPage: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // Guard: Must be admin
  useEffect(() => {
    if (!authLoading) {
      if (!user) {
        navigate('/auth?mode=login');
      } else if (user.role !== 'admin') {
        navigate('/dashboard');
      }
    }
  }, [user, authLoading, navigate]);

  // Tab State: 'jobs' | 'students'
  const [activeTab, setActiveTab] = useState<'jobs' | 'students'>('jobs');

  // Stats state
  const [stats, setStats] = useState<any>(null);

  // Jobs state
  const [jobs, setJobs] = useState<Job[]>([]);
  const [statusFilter, setStatusFilter] = useState<'all' | 'pending_review' | 'published' | 'draft' | 'rejected' | 'expired'>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [loadingJobs, setLoadingJobs] = useState(true);

  // Students state
  const [students, setStudents] = useState<any[]>([]);
  const [loadingStudents, setLoadingStudents] = useState(false);

  // Modal State
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  // Delete Confirmation Modal State
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [jobToDelete, setJobToDelete] = useState<{ id: number; title: string; organization?: string; category?: string } | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  // Feedback Banner
  const [feedback, setFeedback] = useState<{ type: 'success' | 'error'; message: string } | null>(null);

  const fetchStats = async () => {
    try {
      const data = await api.getAdminStats();
      setStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchJobs = useCallback(async () => {
    setLoadingJobs(true);
    try {
      const data = await api.getAdminJobs({
        status: statusFilter,
        q: searchTerm,
      });
      setJobs(data);
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to load jobs.' });
    } finally {
      setLoadingJobs(false);
    }
  }, [statusFilter, searchTerm]);

  const fetchStudents = async () => {
    setLoadingStudents(true);
    try {
      const data = await api.getAdminStudents();
      setStudents(data);
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to load students.' });
    } finally {
      setLoadingStudents(false);
    }
  };

  useEffect(() => {
    if (user && user.role === 'admin') {
      fetchStats();
      fetchJobs();
    }
  }, [user, fetchJobs]);

  useEffect(() => {
    if (activeTab === 'students' && user && user.role === 'admin') {
      fetchStudents();
    }
  }, [activeTab, user]);

  const handleTogglePublish = async (jobId: number) => {
    try {
      const res = await api.togglePublishAdminJob(jobId);
      setFeedback({
        type: 'success',
        message: res.message || 'Job publish status updated.'
      });
      fetchJobs();
      fetchStats();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to toggle status.' });
    }
  };

  const promptDeleteJob = (job: Job) => {
    setJobToDelete({
      id: job.id,
      title: job.title,
      organization: job.organization,
      category: job.category,
    });
    setDeleteModalOpen(true);
  };

  const confirmDeleteJob = async () => {
    if (!jobToDelete) return;
    setIsDeleting(true);
    try {
      await api.deleteAdminJob(jobToDelete.id);
      setFeedback({ type: 'success', message: `Deleted "${jobToDelete.title}".` });
      setDeleteModalOpen(false);
      setJobToDelete(null);
      fetchJobs();
      fetchStats();
    } catch (err: any) {
      setFeedback({ type: 'error', message: err.message || 'Failed to delete job.' });
    } finally {
      setIsDeleting(false);
    }
  };

  const openCreateModal = () => {
    setSelectedJob(null);
    setModalOpen(true);
  };

  const openReviewModal = (job: Job) => {
    setSelectedJob(job);
    setModalOpen(true);
  };

  const handleJobSaved = (msg: string) => {
    setFeedback({ type: 'success', message: msg });
    fetchJobs();
    fetchStats();
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F0E8] text-[#111111]">
      <Navbar />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 space-y-6">
        
        {/* Admin Header with AI Add Option */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b-2 border-[#111111] pb-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-black uppercase tracking-wider bg-[#FF6B4A] text-white px-2 py-0.5 border border-[#111111]">
                Admin Console
              </span>
              <span className="text-xs font-bold text-[#555555]">
                Platform Control & AI-Assisted Recruitment Management
              </span>
            </div>

            <h1 className="font-heading font-black text-3xl sm:text-4xl text-[#111111] tracking-tight">
              Recruitment Operations
            </h1>

            <p className="text-sm text-[#444444] font-medium">
              Create, review, approve, and publish government recruitment opportunities.
            </p>
          </div>

          <div className="flex items-center gap-3">
            <Link
              to="/dashboard"
              className="px-4 py-2.5 text-xs font-black uppercase tracking-wider bg-white border-2 border-[#111111] brutal-shadow-sm hover:bg-[#E8E2D8] transition-colors"
            >
              Candidate View →
            </Link>

            {/* Prominent "+ Add Job" Button */}
            <button
              onClick={openCreateModal}
              className="inline-flex items-center gap-2 px-5 py-2.5 bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow font-heading font-black text-xs uppercase tracking-wider hover:translate-x-[-1px] hover:translate-y-[-1px] active:translate-x-[1px] active:translate-y-[1px] transition-transform"
            >
              <Sparkles size={16} className="text-[#111111] stroke-[2.5]" />
              <span>Add Job (URL / PDF / Manual)</span>
            </button>
          </div>
        </div>

        {/* Feedback Alert */}
        {feedback && (
          <div className={`p-3.5 border-2 border-[#111111] brutal-shadow-sm text-xs font-bold flex items-center justify-between ${
            feedback.type === 'success' ? 'bg-[#D9FF43] text-[#111111]' : 'bg-[#FFF0ED] text-[#D12E00]'
          }`}>
            <div className="flex items-center gap-2">
              <Sparkles size={16} />
              <span>{feedback.message}</span>
            </div>
            <button onClick={() => setFeedback(null)} className="p-0.5 hover:opacity-75 font-mono text-sm">
              ✕
            </button>
          </div>
        )}

        {/* Platform Stat Cards */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
          <div className="bg-white border-2 border-[#111111] brutal-shadow p-4">
            <span className="text-[10px] font-black uppercase tracking-wider text-[#666666] block mb-1">
              Total Opportunities
            </span>
            <div className="flex items-baseline justify-between">
              <span className="font-heading font-black text-3xl text-[#111111]">
                {stats?.total_jobs ?? '...'}
              </span>
              <Layers size={18} className="text-[#666666]" />
            </div>
          </div>

          <div className={`border-2 border-[#111111] brutal-shadow p-4 ${
            (stats?.pending_review_jobs ?? 0) > 0 ? 'bg-amber-300' : 'bg-white'
          }`}>
            <span className="text-[10px] font-black uppercase tracking-wider text-[#111111] block mb-1">
              Pending Review (AI Drafts)
            </span>
            <div className="flex items-baseline justify-between">
              <span className="font-heading font-black text-3xl text-[#111111]">
                {stats?.pending_review_jobs ?? '0'}
              </span>
              <Clock size={18} className="text-[#111111]" />
            </div>
          </div>

          <div className="bg-[#D9FF43] border-2 border-[#111111] brutal-shadow p-4">
            <span className="text-[10px] font-black uppercase tracking-wider text-[#111111] block mb-1">
              Published & Active
            </span>
            <div className="flex items-baseline justify-between">
              <span className="font-heading font-black text-3xl text-[#111111]">
                {stats?.published_jobs ?? '...'}
              </span>
              <CheckCircle2 size={18} className="text-[#111111]" />
            </div>
          </div>

          <div className="bg-[#FF6B4A] text-white border-2 border-[#111111] brutal-shadow p-4">
            <span className="text-[10px] font-black uppercase tracking-wider text-white/90 block mb-1">
              Alerts Dispatched
            </span>
            <div className="flex items-baseline justify-between">
              <span className="font-heading font-black text-3xl text-white">
                {stats?.total_notifications_sent ?? '...'}
              </span>
              <Bell size={18} className="text-white" />
            </div>
          </div>
        </div>

        {/* Section Tabs */}
        <div className="flex items-center gap-2 border-b-2 border-[#111111] pb-2">
          <button
            onClick={() => setActiveTab('jobs')}
            className={`px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-[#111111] transition-transform ${
              activeTab === 'jobs'
                ? 'bg-[#111111] text-[#D9FF43] brutal-shadow translate-x-[-1px] translate-y-[-1px]'
                : 'bg-white text-[#555555] hover:text-[#111111]'
            }`}
          >
            Recruitment Notices ({jobs.length})
          </button>

          <button
            onClick={() => setActiveTab('students')}
            className={`px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-[#111111] transition-transform ${
              activeTab === 'students'
                ? 'bg-[#111111] text-[#D9FF43] brutal-shadow translate-x-[-1px] translate-y-[-1px]'
                : 'bg-white text-[#555555] hover:text-[#111111]'
            }`}
          >
            Registered Aspirants ({stats?.total_students ?? '...'})
          </button>
        </div>

        {/* Tab 1: Recruitment Notices */}
        {activeTab === 'jobs' && (
          <div className="space-y-4">
            {/* Filter & Search Bar */}
            <div className="bg-white border-2 border-[#111111] brutal-shadow p-3 grid grid-cols-1 sm:grid-cols-12 gap-3 items-center">
              <div className="sm:col-span-5 relative">
                <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#777777]" />
                <input
                  type="text"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  placeholder="Search by title, organization, advt no..."
                  className="w-full pl-9 pr-3 py-1.5 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-hidden focus:bg-white"
                />
              </div>

              <div className="sm:col-span-7 flex flex-wrap gap-1.5 justify-end">
                {[
                  { id: 'all', label: 'All' },
                  { id: 'pending_review', label: 'Pending Review' },
                  { id: 'published', label: 'Approved / Published' },
                  { id: 'draft', label: 'Drafts' },
                  { id: 'rejected', label: 'Rejected' },
                  { id: 'expired', label: 'Expired' }
                ].map((st) => (
                  <button
                    key={st.id}
                    onClick={() => setStatusFilter(st.id as any)}
                    className={`px-2.5 py-1 text-[11px] font-bold uppercase tracking-wider border border-[#111111] transition-colors ${
                      statusFilter === st.id
                        ? st.id === 'pending_review' 
                          ? 'bg-amber-300 text-[#111111] font-black' 
                          : 'bg-[#D9FF43] text-[#111111] font-black'
                        : 'bg-[#F5F0E8] text-[#555555] hover:bg-white'
                    }`}
                  >
                    {st.label}
                  </button>
                ))}
              </div>
            </div>

            {/* Jobs List */}
            {loadingJobs ? (
              <div className="bg-white border-2 border-[#111111] brutal-shadow p-8 text-center text-xs font-bold text-[#555555]">
                Loading recruitment notifications...
              </div>
            ) : jobs.length > 0 ? (
              <div className="space-y-3">
                {jobs.map((job) => {
                  const isPending = job.status === 'pending_review';
                  const hasConflicts = job.ai_extraction_metadata?.conflicts && job.ai_extraction_metadata.conflicts.length > 0;
                  const hasWarnings = job.ai_extraction_metadata?.warnings && job.ai_extraction_metadata.warnings.length > 0;

                  return (
                    <div
                      key={job.id}
                      className={`bg-white border-2 border-[#111111] brutal-shadow p-4 flex flex-col md:flex-row md:items-center justify-between gap-4 transition-all ${
                        isPending ? 'border-l-8 border-l-amber-400 bg-amber-50/40' : ''
                      }`}
                    >
                      <div className="space-y-1.5 flex-1 min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="font-mono text-[10px] uppercase font-bold bg-[#111111] text-[#D9FF43] px-2 py-0.5">
                            {job.category}
                          </span>

                          {/* Workflow Status Badge */}
                          {isPending ? (
                            <span className="font-black text-[10px] uppercase bg-amber-300 text-[#111111] border border-[#111111] px-2 py-0.5 flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              Pending Admin Review
                            </span>
                          ) : job.status === 'approved' || (job.is_published && job.status !== 'rejected') ? (
                            <span className="font-bold text-[10px] uppercase bg-[#D9FF43] text-[#111111] border border-[#111111] px-2 py-0.5 flex items-center gap-1">
                              <CheckCircle2 className="w-3 h-3" />
                              Published
                            </span>
                          ) : job.status === 'rejected' ? (
                            <span className="font-bold text-[10px] uppercase bg-[#FF6B4A] text-white border border-[#111111] px-2 py-0.5 flex items-center gap-1">
                              <XCircle className="w-3 h-3" />
                              Rejected
                            </span>
                          ) : (
                            <span className="font-bold text-[10px] uppercase bg-[#E8E2D8] text-[#555555] border border-[#111111] px-2 py-0.5">
                              Draft
                            </span>
                          )}

                          {/* Source indicator */}
                          {job.source_type === 'url' && (
                            <span className="text-[10px] font-mono text-blue-700 bg-blue-50 border border-blue-300 px-1.5 py-0.5 flex items-center gap-1">
                              <Globe className="w-2.5 h-2.5" /> URL Draft
                            </span>
                          )}
                          {job.source_type === 'pdf' && (
                            <span className="text-[10px] font-mono text-purple-700 bg-purple-50 border border-purple-300 px-1.5 py-0.5 flex items-center gap-1">
                              <FileText className="w-2.5 h-2.5" /> PDF Draft
                            </span>
                          )}

                          {/* Conflict & Warning indicators */}
                          {hasConflicts && (
                            <span className="font-bold text-[10px] uppercase bg-[#FF6B4A] text-white px-2 py-0.5 flex items-center gap-1">
                              <AlertTriangle className="w-3 h-3" />
                              Conflict Detected
                            </span>
                          )}

                          {hasWarnings && !hasConflicts && (
                            <span className="font-bold text-[10px] uppercase bg-amber-100 text-amber-900 border border-amber-300 px-1.5 py-0.5">
                              Verify Details
                            </span>
                          )}

                          {job.is_expired && (
                            <span className="font-bold text-[10px] uppercase bg-[#FF6B4A] text-white border border-[#111111] px-2 py-0.5">
                              Expired
                            </span>
                          )}
                        </div>

                        <h3 className="font-heading font-black text-lg text-[#111111] leading-tight">
                          {job.title}
                        </h3>

                        <div className="flex flex-wrap items-center gap-2 text-xs font-semibold text-[#555555]">
                          <span>{job.organization}</span>
                          {job.advertisement_number && (
                            <>
                              <span>•</span>
                              <span className="font-mono text-[#111111]">Advt: {job.advertisement_number}</span>
                            </>
                          )}
                          {job.total_vacancies && (
                            <>
                              <span>•</span>
                              <span className="font-mono text-[#111111] font-bold">{job.total_vacancies.toLocaleString()} Posts</span>
                            </>
                          )}
                        </div>

                        <div className="flex flex-wrap items-center gap-3 text-xs text-[#444444] pt-1">
                          <span>Min Qual: <strong>{job.rule?.min_qualification_level || 'Graduate'}</strong></span>
                          <span>•</span>
                          <span>Age Limit: <strong>{job.min_age} - {job.max_age} yrs</strong></span>
                          <span>•</span>
                          <span>Deadline: <strong>{job.application_deadline || 'Not set'}</strong></span>
                        </div>
                      </div>

                      {/* Admin Action Buttons */}
                      <div className="flex flex-wrap items-center gap-2 pt-2 md:pt-0 border-t md:border-t-0 border-[#E8E2D8]">
                        {isPending ? (
                          <button
                            onClick={() => openReviewModal(job)}
                            className="px-4 py-2 text-xs font-black uppercase tracking-wider bg-[#D9FF43] hover:bg-[#cbf532] text-[#111111] border-2 border-[#111111] shadow-[2px_2px_0px_#111111] flex items-center gap-1.5 transition-transform active:translate-x-0.5 active:translate-y-0.5"
                          >
                            <FileCheck className="w-4 h-4 stroke-[2.5]" />
                            Review & Approve
                          </button>
                        ) : (
                          <button
                            onClick={() => handleTogglePublish(job.id)}
                            className={`px-3 py-1.5 text-xs font-bold uppercase tracking-wider border-2 border-[#111111] brutal-shadow-sm transition-colors ${
                              job.is_published
                                ? 'bg-white hover:bg-[#FF6B4A] hover:text-white'
                                : 'bg-[#D9FF43] hover:bg-[#cbf425]'
                            }`}
                          >
                            {job.is_published ? 'Unpublish' : 'Publish & Alert'}
                          </button>
                        )}

                        <button
                          onClick={() => openReviewModal(job)}
                          className="p-1.5 bg-white hover:bg-[#E8E2D8] border-2 border-[#111111] brutal-shadow-sm transition-colors"
                          title="Edit or review recruitment details"
                        >
                          <Edit3 size={15} />
                        </button>

                        {job.original_url && (
                          <a
                            href={job.original_url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-1.5 bg-white hover:bg-[#E8E2D8] border-2 border-[#111111] brutal-shadow-sm transition-colors"
                            title="View official notification link"
                          >
                            <ExternalLink size={15} />
                          </a>
                        )}

                        <button
                          onClick={() => promptDeleteJob(job)}
                          className="p-1.5 bg-white hover:bg-[#FF6B4A] hover:text-white border-2 border-[#111111] brutal-shadow-sm transition-colors"
                          title="Delete job notice"
                        >
                          <Trash2 size={15} />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="bg-white border-2 border-[#111111] brutal-shadow p-10 text-center space-y-3">
                <p className="font-bold text-sm text-[#111111]">No recruitment notifications match filter.</p>
                <button
                  onClick={openCreateModal}
                  className="px-4 py-2 bg-[#D9FF43] text-[#111111] border-2 border-[#111111] font-bold text-xs uppercase"
                >
                  Add Job Now
                </button>
              </div>
            )}
          </div>
        )}

        {/* Tab 2: Registered Aspirants */}
        {activeTab === 'students' && (
          <div className="bg-white border-2 border-[#111111] brutal-shadow overflow-x-auto">
            {loadingStudents ? (
              <div className="p-8 text-center text-xs font-bold text-[#555555]">
                Loading student profiles...
              </div>
            ) : students.length > 0 ? (
              <table className="w-full text-left text-xs">
                <thead className="bg-[#111111] text-[#D9FF43] font-mono uppercase text-[11px]">
                  <tr>
                    <th className="p-3">Student Email</th>
                    <th className="p-3">Full Name</th>
                    <th className="p-3">Category</th>
                    <th className="p-3">Domicile</th>
                    <th className="p-3">Date of Birth</th>
                    <th className="p-3">Qualifications</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[#111111]">
                  {students.map((st) => (
                    <tr key={st.id} className="hover:bg-[#F5F0E8] transition-colors font-semibold">
                      <td className="p-3 font-mono font-bold text-[#111111]">{st.email}</td>
                      <td className="p-3">{st.full_name}</td>
                      <td className="p-3">
                        <span className="font-mono bg-[#E8E2D8] px-1.5 py-0.5 border border-[#111111]">
                          {st.category}
                        </span>
                      </td>
                      <td className="p-3">{st.domicile_state}</td>
                      <td className="p-3 font-mono">{st.date_of_birth || 'Not Set'}</td>
                      <td className="p-3">
                        <div className="flex flex-wrap gap-1">
                          {st.qualifications && st.qualifications.length > 0 ? (
                            st.qualifications.map((q: any, i: number) => (
                              <span key={i} className="text-[10px] bg-white border border-[#111111] px-1 py-0.5 font-mono">
                                {q.level} ({q.status})
                              </span>
                            ))
                          ) : (
                            <span className="text-gray-400 font-mono">None</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-xs font-bold text-[#555555]">
                No student profiles registered yet.
              </div>
            )}
          </div>
        )}
      </main>

      <Footer />

      {/* Add / Review Job Modal */}
      <AdminAddJobModal
        job={selectedJob}
        isOpen={modalOpen}
        onClose={() => setModalOpen(false)}
        onSaved={handleJobSaved}
      />

      {/* Delete Confirmation Dialog */}
      <DeleteConfirmModal
        isOpen={deleteModalOpen}
        job={jobToDelete}
        isDeleting={isDeleting}
        onConfirm={confirmDeleteJob}
        onCancel={() => {
          if (!isDeleting) {
            setDeleteModalOpen(false);
            setJobToDelete(null);
          }
        }}
      />
    </div>
  );
};
