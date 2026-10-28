import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { api } from '../services/api';
import type { Job } from '../types';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { ArrowRight, CheckCircle2, Sparkles, ExternalLink, Calendar, Users, GraduationCap, Building2 } from 'lucide-react';

export const LandingPage: React.FC = () => {
  const { user } = useAuth();
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([]);
  const [loadingJobs, setLoadingJobs] = useState<boolean>(true);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const data = await api.getPublicJobs();
        setFeaturedJobs(data.slice(0, 6));
      } catch (err) {
        console.error('Failed to load featured jobs', err);
      } finally {
        setLoadingJobs(false);
      }
    };
    fetchJobs();
  }, []);

  const destinationUrl = user ? (user.role === 'admin' ? '/admin' : '/dashboard') : '/auth?mode=register';
  const ctaText = user ? (user.role === 'admin' ? 'Open Admin Console' : 'Go to Dashboard') : 'Get Started';

  return (
    <div className="min-h-screen flex flex-col bg-[#F5F0E8] text-[#111111]">
      <Navbar />

      {/* Hero Section */}
      <section className="max-w-6xl mx-auto px-4 sm:px-6 pt-12 sm:pt-20 pb-16 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          {/* Hero Left */}
          <div className="lg:col-span-7 space-y-6">
            <div className="inline-flex items-center gap-2 bg-[#D9FF43] border-2 border-[#111111] px-3 py-1 font-bold text-xs uppercase tracking-wider brutal-shadow-sm">
              <Sparkles size={14} />
              <span>Personalized Government Exam Tracker</span>
            </div>

            <h1 className="font-heading font-black text-3xl sm:text-5xl lg:text-7xl leading-[1.05] tracking-tight text-[#111111]">
              Government Jobs.
              <br />
              <span className="bg-[#111111] text-[#D9FF43] px-2 box-decoration-clone">
                Matched to You.
              </span>
            </h1>

            <p className="text-sm sm:text-lg text-[#333333] font-medium max-w-xl leading-relaxed">
              Stop checking every notification. Discover government exams that match your age, qualification, and eligibility.
            </p>

            <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 pt-2">
              <Link
                to={destinationUrl}
                className="inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-[#D9FF43] text-[#111111] font-heading font-black text-sm uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:translate-x-[-2px] hover:translate-y-[-2px] hover:bg-[#c9f22e] active:translate-x-[2px] active:translate-y-[2px] transition-transform text-center"
              >
                <span>{ctaText}</span>
                <ArrowRight size={18} />
              </Link>

              <a
                href="#latest-jobs"
                className="inline-flex items-center justify-center gap-2 px-6 py-3.5 bg-[#FFFFFF] text-[#111111] font-heading font-black text-sm uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#E8E2D8] transition-colors text-center"
              >
                <span>Explore Latest Jobs ({featuredJobs.length > 0 ? `${featuredJobs.length}+` : 'Browse'})</span>
              </a>
            </div>

            <div className="pt-2 sm:pt-4 flex flex-col sm:flex-row sm:items-center gap-3 sm:gap-6 text-xs font-bold text-[#555555]">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-[#111111] shrink-0" />
                Zero Spam / No Coaching Sell
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-[#111111] shrink-0" />
                Deterministic Age & Category Math
              </span>
            </div>
          </div>

          {/* Hero Right: Neo-Brutalist Interactive Preview Card */}
          <div className="lg:col-span-5">
            <div className="bg-[#FFFFFF] border-3 border-[#111111] brutal-shadow-lg p-4 sm:p-6 relative space-y-4">
              <div className="absolute -top-3.5 right-4 bg-[#FF6B4A] text-white border-2 border-[#111111] px-3 py-0.5 text-xs font-black uppercase tracking-wider">
                Live Sample Match
              </div>

              <div className="space-y-1">
                <span className="font-mono text-[10px] font-black uppercase bg-[#111111] text-[#D9FF43] px-2 py-0.5">
                  Civil Services
                </span>
                <h3 className="font-heading font-black text-xl text-[#111111] pt-1">
                  UPSC Civil Services (CSE) 2026
                </h3>
                <p className="text-xs text-[#555555] font-semibold">
                  Union Public Service Commission
                </p>
              </div>

              <div className="bg-[#F5F0E8] border-2 border-[#111111] p-3 text-xs space-y-2">
                <div className="flex justify-between items-center">
                  <span className="font-bold text-[#777777]">Your Status:</span>
                  <span className="bg-[#D9FF43] border border-[#111111] px-2 py-0.5 font-black text-[11px]">
                    ELIGIBLE (Age 26 + OBC +3)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-bold text-[#777777]">Requirement:</span>
                  <span className="font-mono font-bold text-[#111111]">Graduate Degree</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="font-bold text-[#777777]">Last Date:</span>
                  <span className="font-bold text-[#111111]">05 Dec 2026</span>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs font-bold text-[#666666]">
                  Redirects to official portal
                </span>
                <Link
                  to="/auth"
                  className="inline-flex items-center gap-1 text-xs font-black bg-[#D9FF43] border-2 border-[#111111] px-3 py-1.5 brutal-shadow-sm hover:bg-[#cbf425]"
                >
                  <span>Check Eligibility</span>
                  <ExternalLink size={12} />
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Latest Government Jobs Section */}
      <section id="latest-jobs" className="bg-[#FFFFFF] border-y-2 border-[#111111] py-16 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto space-y-8">
          <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
            <div className="space-y-1.5">
              <span className="font-mono text-xs font-black uppercase tracking-wider text-[#FF6B4A]">
                Official 2026 Recruitment Bulletins
              </span>
              <h2 className="font-heading font-black text-2xl sm:text-4xl text-[#111111]">
                Latest Government Exam Opportunities
              </h2>
              <p className="text-xs sm:text-sm text-[#555555]">
                Verified openings across Civil Services, Defense, Railways, Banking, Engineering & State PSCs.
              </p>
            </div>
            <Link
              to="/auth"
              className="inline-flex items-center justify-center gap-2 px-5 py-2.5 bg-[#D9FF43] text-[#111111] font-bold text-xs uppercase tracking-wider border-2 border-[#111111] brutal-shadow-sm hover:translate-x-[-1px] hover:translate-y-[-1px] transition-transform self-start sm:self-auto"
            >
              <span>View All on Dashboard</span>
              <ArrowRight size={14} />
            </Link>
          </div>

          {loadingJobs ? (
            <div className="p-12 text-center text-sm font-bold text-[#555555]">
              Loading latest recruitment notices...
            </div>
          ) : featuredJobs.length === 0 ? (
            <div className="p-12 text-center bg-[#F5F0E8] border-2 border-[#111111] brutal-shadow text-sm font-bold text-[#555555]">
              No active recruitment listings found. Check back shortly!
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {featuredJobs.map((job) => {
                const minQual = job.rule?.min_qualification_level || 'Graduate';
                return (
                  <div
                    key={job.id}
                    className="bg-[#F5F0E8] border-2 border-[#111111] brutal-shadow p-5 flex flex-col justify-between hover:translate-y-[-2px] transition-transform space-y-4"
                  >
                    <div className="space-y-3">
                      <div className="flex items-center justify-between gap-2">
                        <span className="font-mono text-[10px] uppercase font-bold bg-[#111111] text-[#D9FF43] px-2 py-0.5">
                          {job.category}
                        </span>
                        {job.total_vacancies && (
                          <span className="font-mono text-[11px] font-black bg-[#D9FF43] border border-[#111111] px-2 py-0.5 flex items-center gap-1">
                            <Users size={12} />
                            {job.total_vacancies.toLocaleString()} Posts
                          </span>
                        )}
                      </div>

                      <div>
                        <h3 className="font-heading font-black text-base text-[#111111] leading-snug line-clamp-2">
                          {job.title}
                        </h3>
                        <p className="text-xs text-[#555555] font-semibold flex items-center gap-1 mt-1">
                          <Building2 size={13} className="shrink-0" />
                          <span className="truncate">{job.organization}</span>
                        </p>
                      </div>

                      <div className="bg-white border border-[#111111] p-2.5 space-y-1.5 text-xs">
                        <div className="flex items-center justify-between">
                          <span className="text-[#666666] flex items-center gap-1">
                            <GraduationCap size={13} />
                            Min Qual:
                          </span>
                          <span className="font-mono font-bold text-[#111111]">{minQual}</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-[#666666]">Age Limit:</span>
                          <span className="font-mono font-bold text-[#111111]">
                            {job.min_age} - {job.max_age} yrs
                          </span>
                        </div>
                        {job.application_deadline && (
                          <div className="flex items-center justify-between">
                            <span className="text-[#666666] flex items-center gap-1">
                              <Calendar size={13} />
                              Last Date:
                            </span>
                            <span className="font-bold text-[#FF6B4A]">
                              {job.application_deadline}
                            </span>
                          </div>
                        )}
                      </div>
                    </div>

                    <div className="pt-2 border-t border-[#D9D4CC] flex items-center justify-between gap-2">
                      <Link
                        to="/auth"
                        className="flex-1 text-center py-2 px-3 bg-[#111111] text-[#D9FF43] font-bold text-xs uppercase tracking-wider hover:bg-[#222222] transition-colors"
                      >
                        Check Eligibility
                      </Link>
                      {job.original_url && (
                        <a
                          href={job.original_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          title="Official Notification Link"
                          className="p-2 bg-white border border-[#111111] hover:bg-[#E8E2D8] transition-colors"
                        >
                          <ExternalLink size={14} />
                        </a>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="bg-[#FFFFFF] border-y-2 border-[#111111] py-16 px-4 sm:px-6">
        <div className="max-w-6xl mx-auto space-y-10">
          <div className="max-w-xl space-y-2">
            <span className="font-mono text-xs font-black uppercase tracking-wider text-[#FF6B4A]">
              Clear & Simple Workflow
            </span>
            <h2 className="font-heading font-black text-3xl sm:text-4xl text-[#111111]">
              How CareerSync Works
            </h2>
            <p className="text-sm text-[#555555]">
              No complicated questionnaires or ads. Three simple steps to discover eligible exams.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Step 1 */}
            <div className="bg-[#F5F0E8] border-2 border-[#111111] brutal-shadow p-6 space-y-4">
              <div className="font-mono font-black text-3xl sm:text-4xl text-[#111111] bg-[#D9FF43] border-2 border-[#111111] w-14 h-14 flex items-center justify-center">
                01
              </div>
              <h3 className="font-heading font-black text-xl text-[#111111]">
                Create Your Profile
              </h3>
              <p className="text-sm text-[#444444] leading-relaxed">
                Add your date of birth, qualification, and category once.
              </p>
            </div>

            {/* Step 2 */}
            <div className="bg-[#F5F0E8] border-2 border-[#111111] brutal-shadow p-6 space-y-4">
              <div className="font-mono font-black text-3xl sm:text-4xl text-[#111111] bg-[#FFFFFF] border-2 border-[#111111] w-14 h-14 flex items-center justify-center">
                02
              </div>
              <h3 className="font-heading font-black text-xl text-[#111111]">
                Discover Eligible Jobs
              </h3>
              <p className="text-sm text-[#444444] leading-relaxed">
                CareerSync matches your profile with currently open government recruitment opportunities.
              </p>
            </div>

            {/* Step 3 */}
            <div className="bg-[#F5F0E8] border-2 border-[#111111] brutal-shadow p-6 space-y-4">
              <div className="font-mono font-black text-3xl sm:text-4xl text-white bg-[#111111] border-2 border-[#111111] w-14 h-14 flex items-center justify-center">
                03
              </div>
              <h3 className="font-heading font-black text-xl text-[#111111]">
                Read the Original Notification
              </h3>
              <p className="text-sm text-[#444444] leading-relaxed">
                Open the original recruitment notification to verify details and apply.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 px-4 sm:px-6 max-w-4xl mx-auto text-center space-y-6">
        <div className="bg-[#D9FF43] border-3 border-[#111111] brutal-shadow-lg p-8 sm:p-12 space-y-4">
          <h2 className="font-heading font-black text-3xl sm:text-5xl text-[#111111] tracking-tight">
            Find your next opportunity.
          </h2>
          <p className="text-sm sm:text-base text-[#222222] font-semibold max-w-md mx-auto">
            Zero noise. Deterministic eligibility matching directly against official recruitment criteria.
          </p>
          <div className="pt-2">
            <Link
              to={destinationUrl}
              className="inline-flex items-center gap-2 px-8 py-4 bg-[#111111] text-[#D9FF43] font-heading font-black text-base uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#222222] active:translate-x-[2px] active:translate-y-[2px] transition-transform"
            >
              <span>{ctaText}</span>
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};
