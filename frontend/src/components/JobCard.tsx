import React from 'react';
import type { Job } from '../types';
import { EligibilityBadge } from './EligibilityBadge';
import { ExternalLink, HelpCircle, Calendar, GraduationCap } from 'lucide-react';

interface JobCardProps {
  job: Job;
  onExplain: (job: Job) => void;
}

export const JobCard: React.FC<JobCardProps> = ({ job, onExplain }) => {
  const status = job.eligibility?.status || 'review_required';
  const minQual = job.rule?.min_qualification_level || 'Graduate';

  // Timezone-safe date formatting for YYYY-MM-DD
  const formatDeadline = (dateStr: string) => {
    if (!dateStr) return '';
    const parts = dateStr.split('-').map(Number);
    if (parts.length === 3 && parts[0] && parts[1] && parts[2]) {
      const d = new Date(parts[0], parts[1] - 1, parts[2]);
      return d.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    }
    return dateStr;
  };

  const formattedDeadline = formatDeadline(job.application_deadline);

  return (
    <div className="bg-[#FFFFFF] border-2 border-[#111111] brutal-shadow p-4 sm:p-5 transition-transform hover:translate-x-[-1px] hover:translate-y-[-1px]">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        {/* Left Section: Job info & Meta */}
        <div className="space-y-1.5 flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-mono text-[10px] uppercase font-bold tracking-wider bg-[#111111] text-[#D9FF43] px-2 py-0.5">
              {job.category}
            </span>
            <span className="text-xs text-[#666666] font-semibold truncate">
              {job.source_name || 'Official Notification'}
            </span>
          </div>

          <h3 className="font-heading font-black text-lg sm:text-xl text-[#111111] leading-tight tracking-tight">
            {job.title}
          </h3>

          <p className="text-sm font-semibold text-[#444444]">
            {job.organization}
          </p>

          <div className="flex flex-wrap items-center gap-x-4 gap-y-1 pt-1 text-xs text-[#555555] font-medium">
            <span className="inline-flex items-center gap-1">
              <GraduationCap size={14} className="text-[#111111]" />
              <strong className="text-[#111111]">{minQual}</strong>
              {job.rule?.allowed_status === 'appearing_allowed' && (
                <span className="text-[11px] text-[#008000] font-bold">(Final Year Allowed)</span>
              )}
            </span>

            {job.rule?.additional_certification_requirement && (
              <>
                <span className="text-[#888888]">|</span>
                <span className="inline-flex items-center gap-1 text-[11px] bg-[#F5F0E8] border border-[#111111] px-1.5 py-0.5 font-bold text-[#111111]" title={job.rule.additional_certification_requirement}>
                  <span>Req:</span>
                  <span className="truncate max-w-[130px] sm:max-w-[220px]">
                    {job.rule.additional_certification_requirement}
                  </span>
                </span>
              </>
            )}

            <span className="text-[#888888]">|</span>

            <span className="inline-flex items-center gap-1">
              <Calendar size={14} className="text-[#111111]" />
              <span>Last Date:</span>
              <strong className="text-[#111111]">{formattedDeadline}</strong>
            </span>

            {job.is_expired && (
              <span className="bg-[#FF6B4A] text-white px-1.5 py-0.2 text-[10px] font-bold uppercase">
                EXPIRED
              </span>
            )}
          </div>
        </div>

        {/* Right Section: Eligibility Status & Action Buttons */}
        <div className="flex flex-row md:flex-col items-center md:items-end justify-between md:justify-center gap-2.5 sm:gap-3 pt-3 md:pt-0 border-t-2 md:border-t-0 border-[#E8E2D8]">
          <div className="flex items-center gap-1.5 sm:gap-2">
            <EligibilityBadge status={status} />
            
            <button
              onClick={() => onExplain(job)}
              className="p-1.5 text-[#666666] hover:text-[#111111] hover:bg-[#E8E2D8] border border-transparent hover:border-[#111111] transition-all min-w-[28px] min-h-[28px] flex items-center justify-center cursor-pointer"
              title="Explain eligibility reasons"
              aria-label="Explain eligibility"
            >
              <HelpCircle size={16} />
            </button>
          </div>

          <a
            href={job.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 sm:px-4 py-2 text-xs font-black uppercase tracking-wider bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow-sm hover:bg-[#cbf425] active:translate-x-[1px] active:translate-y-[1px] transition-all whitespace-nowrap"
          >
            <span>Show Details</span>
            <ExternalLink size={13} className="stroke-[2.5]" />
          </a>
        </div>
      </div>
    </div>
  );
};
