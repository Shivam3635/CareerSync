import React from 'react';
import { Link } from 'react-router-dom';
import { Navbar } from '../components/Navbar';
import { Footer } from '../components/Footer';
import { ArrowRight, CheckCircle2, Sparkles, ExternalLink } from 'lucide-react';

export const LandingPage: React.FC = () => {
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
              <span>Personalized Government Exam Filter</span>
            </div>

            <h1 className="font-heading font-black text-4xl sm:text-6xl lg:text-7xl leading-[1.05] tracking-tight text-[#111111]">
              Government Jobs.
              <br />
              <span className="bg-[#111111] text-[#D9FF43] px-2 box-decoration-clone">
                Matched to You.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-[#333333] font-medium max-w-xl leading-relaxed">
              Stop checking every notification. Discover government exams that match your age, qualification, and eligibility.
            </p>

            <div className="flex flex-wrap items-center gap-4 pt-2">
              <Link
                to="/auth?mode=register"
                className="inline-flex items-center gap-2 px-6 py-3.5 bg-[#D9FF43] text-[#111111] font-heading font-black text-sm uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:translate-x-[-2px] hover:translate-y-[-2px] hover:bg-[#c9f22e] active:translate-x-[2px] active:translate-y-[2px] transition-transform"
              >
                <span>Get Started</span>
                <ArrowRight size={18} />
              </Link>

              <a
                href="#how-it-works"
                className="inline-flex items-center gap-2 px-6 py-3.5 bg-[#FFFFFF] text-[#111111] font-heading font-black text-sm uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#E8E2D8] transition-colors"
              >
                <span>How It Works</span>
              </a>
            </div>

            <div className="pt-4 flex flex-wrap items-center gap-6 text-xs font-bold text-[#555555]">
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-[#111111]" />
                Zero Spam / No Coaching Sell
              </span>
              <span className="flex items-center gap-1.5">
                <CheckCircle2 size={16} className="text-[#111111]" />
                Deterministic Age & Category Math
              </span>
            </div>
          </div>

          {/* Hero Right: Neo-Brutalist Interactive Preview Card */}
          <div className="lg:col-span-5">
            <div className="bg-[#FFFFFF] border-3 border-[#111111] brutal-shadow-lg p-6 relative space-y-4">
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
                  <span className="font-bold text-[#111111]">30 Nov 2026</span>
                </div>
              </div>

              <div className="pt-2 flex items-center justify-between">
                <span className="text-xs font-bold text-[#666666]">
                  Redirects to official portal
                </span>
                <div className="inline-flex items-center gap-1 text-xs font-black bg-[#D9FF43] border-2 border-[#111111] px-3 py-1.5 brutal-shadow-sm">
                  <span>Show Details</span>
                  <ExternalLink size={12} />
                </div>
              </div>
            </div>
          </div>
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
              to="/auth?mode=register"
              className="inline-flex items-center gap-2 px-8 py-4 bg-[#111111] text-[#D9FF43] font-heading font-black text-base uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#222222] active:translate-x-[2px] active:translate-y-[2px] transition-transform"
            >
              <span>Get Started</span>
              <ArrowRight size={20} />
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
};
