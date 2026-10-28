import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import type { Job, JobMatchesResponse } from '../types';
import { api } from '../services/api';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { JobCard } from '../components/JobCard';
import { EligibilityModal } from '../components/EligibilityModal';
import { ProfileDrawer } from '../components/ProfileDrawer';
import { 
  Search, 
  Filter, 
  RotateCcw, 
  CheckCircle2, 
  AlertTriangle, 
  XCircle, 
  Layers, 
} from 'lucide-react';

export const DashboardPage: React.FC = () => {
  const { user, loading: authLoading } = useAuth();
  const navigate = useNavigate();

  // Redirect if not logged in
  useEffect(() => {
    if (!authLoading && !user) {
      navigate('/auth?mode=login');
    }
  }, [user, authLoading, navigate]);

  // Filters state - Default is 'eligible' as required by product spec!
  const [statusFilter, setStatusFilter] = useState<'eligible' | 'all' | 'review_required' | 'not_eligible'>('eligible');
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedQualification, setSelectedQualification] = useState<string>('all');

  // Debounce search input by 250ms
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearch(searchTerm);
    }, 250);
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Data state
  const [matchesData, setMatchesData] = useState<JobMatchesResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // Modals state
  const [explainingJob, setExplainingJob] = useState<Job | null>(null);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  // Fetch job matches from API
  const fetchMatches = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await api.getJobMatches({
        status: statusFilter,
        q: debouncedSearch,
        category: selectedCategory,
        qualification: selectedQualification,
      });
      setMatchesData(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load matching opportunities.');
    } finally {
      setLoading(false);
    }
  }, [statusFilter, debouncedSearch, selectedCategory, selectedQualification]);

  useEffect(() => {
    if (user) {
      fetchMatches();
    }
  }, [user, fetchMatches]);

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(e.target.value);
  };

  const handleResetFilters = () => {
    setStatusFilter('eligible');
    setSearchTerm('');
    setSelectedCategory('all');
    setSelectedQualification('all');
  };

  const summary = matchesData?.summary;
  const jobs = matchesData?.jobs || [];

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-[#F5F0E8]">
        <div className="p-6 bg-white border-2 border-[#111111] brutal-shadow flex items-center gap-3">
          <div className="w-5 h-5 border-2 border-[#111111] border-t-transparent animate-spin" />
          <span className="font-heading font-black text-xs uppercase tracking-wider text-[#111111]">
            Loading candidate profile & matches...
          </span>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F0E8] text-[#111111]">
      <Navbar onOpenProfile={() => setIsProfileOpen(true)} />

      <main className="flex-1 max-w-6xl w-full mx-auto px-4 sm:px-6 py-8 space-y-6">
        {/* Top Header & Dynamic Eligibility Summary */}
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 border-b-2 border-[#111111] pb-6">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-mono text-xs font-black uppercase tracking-wider bg-[#111111] text-[#D9FF43] px-2 py-0.5">
                Dashboard
              </span>
              {user?.student_profile && (
                <span className="text-xs font-bold text-[#555555]">
                  Evaluating as {user.student_profile.category} • {user.student_profile.domicile_state}
                </span>
              )}
            </div>

            <h1 className="font-heading font-black text-3xl sm:text-4xl text-[#111111] tracking-tight">
              Your Opportunities
            </h1>

            <p className="text-sm text-[#444444] font-medium">
              Government jobs matched to your eligibility.
            </p>
          </div>

          {/* Dynamic matching counter */}
          <div className="bg-[#FFFFFF] border-2 border-[#111111] brutal-shadow px-4 py-2.5 flex items-center gap-3">
            <div className="w-8 h-8 bg-[#D9FF43] border border-[#111111] flex items-center justify-center font-mono font-black text-lg">
              {summary?.eligible_count ?? '...'}
            </div>
            <div>
              <span className="text-xs font-black uppercase tracking-wider block text-[#111111]">
                {summary?.eligible_count === 1 ? '1 Matching Opportunity' : `${summary?.eligible_count ?? 0} Matching Opportunities`}
              </span>
              <span className="text-[11px] text-[#666666]">
                out of {summary?.total_jobs ?? 0} active recruitments
              </span>
            </div>
          </div>
        </div>

        {/* Profile Incomplete / Setup Banner */}
        {matchesData && !matchesData.has_profile && (
          <div className="bg-[#FFF4E5] border-2 border-[#111111] brutal-shadow p-3.5 sm:p-4 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
            <div className="space-y-0.5">
              <span className="font-mono text-[10px] font-black uppercase text-[#E08700] flex items-center gap-1.5">
                <AlertTriangle size={13} />
                Profile Setup Required for Custom Eligibility
              </span>
              <p className="text-xs font-semibold text-[#111111]">
                Currently displaying all active government exam opportunities. Add your Date of Birth & Category to calculate exact personal eligibility!
              </p>
            </div>
            <button
              onClick={() => setIsProfileOpen(true)}
              className="px-3.5 py-1.5 bg-[#D9FF43] text-[#111111] border-2 border-[#111111] font-bold text-xs uppercase tracking-wider brutal-shadow-sm hover:translate-x-[-1px] hover:translate-y-[-1px] transition-transform shrink-0"
            >
              Complete Profile
            </button>
          </div>
        )}

        {/* Status Filter Tabs (Eligible is default) */}
        <div className="grid grid-cols-2 sm:flex sm:flex-wrap gap-2">
          <button
            onClick={() => setStatusFilter('eligible')}
            className={`flex items-center justify-center sm:justify-start gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-[#111111] transition-transform ${
              statusFilter === 'eligible'
                ? 'bg-[#D9FF43] text-[#111111] brutal-shadow translate-x-[-1px] translate-y-[-1px]'
                : 'bg-[#FFFFFF] text-[#555555] hover:text-[#111111] hover:bg-[#E8E2D8]'
            }`}
          >
            <CheckCircle2 size={15} className="stroke-[2.5] shrink-0" />
            <span className="truncate">Eligible</span>
            {summary && (
              <span className="bg-[#111111] text-[#D9FF43] px-1.5 py-0.2 font-mono text-[10px] shrink-0">
                {summary.eligible_count}
              </span>
            )}
          </button>

          <button
            onClick={() => setStatusFilter('all')}
            className={`flex items-center justify-center sm:justify-start gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-[#111111] transition-transform ${
              statusFilter === 'all'
                ? 'bg-[#111111] text-white brutal-shadow translate-x-[-1px] translate-y-[-1px]'
                : 'bg-[#FFFFFF] text-[#555555] hover:text-[#111111] hover:bg-[#E8E2D8]'
            }`}
          >
            <Layers size={15} className="shrink-0" />
            <span className="truncate">All Jobs</span>
            {summary && (
              <span className="bg-[#E8E2D8] text-[#111111] px-1.5 py-0.2 font-mono text-[10px] shrink-0">
                {summary.total_jobs}
              </span>
            )}
          </button>

          <button
            onClick={() => setStatusFilter('review_required')}
            className={`flex items-center justify-center sm:justify-start gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-[#111111] transition-transform ${
              statusFilter === 'review_required'
                ? 'bg-[#FFFFFF] text-[#111111] brutal-shadow translate-x-[-1px] translate-y-[-1px] ring-2 ring-[#111111]'
                : 'bg-[#FFFFFF] text-[#555555] hover:text-[#111111] hover:bg-[#E8E2D8]'
            }`}
          >
            <AlertTriangle size={15} className="text-[#E08700] stroke-[2.5] shrink-0" />
            <span className="truncate">Review</span>
            {summary && (
              <span className="bg-[#E8E2D8] text-[#111111] px-1.5 py-0.2 font-mono text-[10px] shrink-0">
                {summary.review_required_count}
              </span>
            )}
          </button>

          <button
            onClick={() => setStatusFilter('not_eligible')}
            className={`flex items-center justify-center sm:justify-start gap-1.5 sm:gap-2 px-3 sm:px-4 py-2 text-xs font-black uppercase tracking-wider border-2 border-[#111111] transition-transform ${
              statusFilter === 'not_eligible'
                ? 'bg-[#FF6B4A] text-white brutal-shadow translate-x-[-1px] translate-y-[-1px]'
                : 'bg-[#FFFFFF] text-[#555555] hover:text-[#111111] hover:bg-[#E8E2D8]'
            }`}
          >
            <XCircle size={15} className="stroke-[2.5] shrink-0" />
            <span className="truncate">Not Eligible</span>
            {summary && (
              <span className="bg-[#111111] text-white px-1.5 py-0.2 font-mono text-[10px] shrink-0">
                {summary.not_eligible_count}
              </span>
            )}
          </button>
        </div>

        {/* Search & Compact Secondary Filter Controls */}
        <div className="bg-[#FFFFFF] border-2 border-[#111111] brutal-shadow p-3 sm:p-4 grid grid-cols-1 md:grid-cols-12 gap-3 items-center">
          {/* Search Field */}
          <div className="md:col-span-5 relative">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-[#777777]" />
            <input
              type="text"
              value={searchTerm}
              onChange={handleSearchChange}
              placeholder="Search by job title, organization, or role..."
              className="w-full pl-9 pr-3 py-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
            />
          </div>

          {/* Category Filter */}
          <div className="md:col-span-3">
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full py-2 px-2.5 bg-[#F5F0E8] border border-[#111111] text-xs font-bold focus:outline-none focus:bg-white"
            >
              <option value="all">All Recruitment Categories</option>
              <option value="Civil Services">Civil Services</option>
              <option value="Banking">Banking & Finance</option>
              <option value="Railways">Railways</option>
              <option value="Defense">Defense</option>
              <option value="Engineering & Tech">Engineering & Tech</option>
              <option value="Teaching">Teaching</option>
              <option value="Police & Security">Police & Security</option>
            </select>
          </div>

          {/* Qualification Filter */}
          <div className="md:col-span-3">
            <select
              value={selectedQualification}
              onChange={(e) => setSelectedQualification(e.target.value)}
              className="w-full py-2 px-2.5 bg-[#F5F0E8] border border-[#111111] text-xs font-bold focus:outline-none focus:bg-white"
            >
              <option value="all">All Qualifications</option>
              <option value="10th">10th Standard / Matric</option>
              <option value="12th">12th Standard / Inter</option>
              <option value="Graduate">Graduate / Bachelor</option>
              <option value="Post Graduate">Post Graduate / Master</option>
              <option value="Doctorate">Doctorate / Ph.D.</option>
            </select>
          </div>

          {/* Reset button */}
          <div className="md:col-span-1 flex justify-end">
            <button
              onClick={handleResetFilters}
              title="Reset all filters"
              className="p-2 border border-[#111111] bg-[#F5F0E8] hover:bg-[#FF6B4A] hover:text-white transition-colors"
            >
              <RotateCcw size={15} />
            </button>
          </div>
        </div>

        {/* Error message */}
        {error && (
          <div className="p-3 bg-[#FFF0ED] border-2 border-[#111111] text-xs font-bold text-[#D12E00]">
            {error}
          </div>
        )}

        {/* Job Notification List */}
        <div className="space-y-3">
          {loading ? (
            <div className="bg-[#FFFFFF] border-2 border-[#111111] brutal-shadow p-12 text-center space-y-2">
              <div className="inline-block w-8 h-8 border-3 border-[#111111] border-t-[#D9FF43] rounded-full animate-spin"></div>
              <p className="text-xs font-bold text-[#555555] uppercase tracking-wider">
                Evaluating Eligibility Criteria...
              </p>
            </div>
          ) : jobs.length > 0 ? (
            jobs.map((job) => (
              <JobCard
                key={job.id}
                job={job}
                onExplain={(j) => setExplainingJob(j)}
              />
            ))
          ) : (
            <div className="bg-[#FFFFFF] border-2 border-[#111111] brutal-shadow p-10 text-center space-y-3">
              <div className="w-12 h-12 bg-[#F5F0E8] border-2 border-[#111111] flex items-center justify-center mx-auto text-[#666666]">
                <Filter size={24} />
              </div>
              <h3 className="font-heading font-black text-lg text-[#111111]">
                No jobs match the selected filter.
              </h3>
              <p className="text-xs text-[#555555] max-w-sm mx-auto">
                {statusFilter === 'eligible' 
                  ? "You don't have any matching jobs under the current criteria. Try switching to 'All Jobs' or adjusting your eligibility profile."
                  : "No recruitment notifications found matching your search or filters."}
              </p>
              <div className="pt-2 flex justify-center gap-3">
                <button
                  onClick={() => setStatusFilter('all')}
                  className="px-4 py-2 bg-[#D9FF43] text-[#111111] border-2 border-[#111111] text-xs font-black uppercase tracking-wider brutal-shadow-sm hover:translate-x-[-1px] hover:translate-y-[-1px]"
                >
                  View All Jobs
                </button>
                <button
                  onClick={() => setIsProfileOpen(true)}
                  className="px-4 py-2 bg-[#FFFFFF] text-[#111111] border-2 border-[#111111] text-xs font-black uppercase tracking-wider brutal-shadow-sm hover:bg-[#E8E2D8]"
                >
                  Update Profile
                </button>
              </div>
            </div>
          )}
        </div>
      </main>

      {/* Eligibility Explanation Modal */}
      <EligibilityModal
        job={explainingJob}
        onClose={() => setExplainingJob(null)}
      />

      {/* Interactive Profile Drawer / Modal */}
      <ProfileDrawer
        isOpen={isProfileOpen}
        onClose={() => setIsProfileOpen(false)}
        onProfileUpdated={fetchMatches}
      />

      <Footer />
    </div>
  );
};
