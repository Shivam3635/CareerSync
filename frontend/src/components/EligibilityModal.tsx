import React from 'react';
import type { Job } from '../types';
import { EligibilityBadge } from './EligibilityBadge';
import { X, Check, AlertCircle, Info, ExternalLink } from 'lucide-react';

interface EligibilityModalProps {
  job: Job | null;
  onClose: () => void;
}

export const EligibilityModal: React.FC<EligibilityModalProps> = ({ job, onClose }) => {
  if (!job || !job.eligibility) return null;

  const { status, reasons, failed_criteria, warnings, details } = job.eligibility;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#111111]/70 backdrop-blur-xs animate-in fade-in duration-100">
      <div 
        className="w-full max-w-xl bg-[#F5F0E8] border-3 border-[#111111] brutal-shadow-lg p-6 max-h-[90vh] overflow-y-auto"
        role="dialog"
        aria-modal="true"
      >
        {/* Header */}
        <div className="flex items-start justify-between border-b-2 border-[#111111] pb-4 mb-4">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <EligibilityBadge status={status} />
              <span className="text-xs font-mono uppercase bg-[#111111] text-[#D9FF43] px-2 py-0.5 font-bold">
                {job.category}
              </span>
            </div>
            <h3 className="font-heading font-black text-xl text-[#111111] leading-tight">
              {job.title}
            </h3>
            <p className="text-xs text-[#555555] font-semibold mt-0.5">
              {job.organization}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1 border-2 border-[#111111] bg-white hover:bg-[#FF6B4A] hover:text-white brutal-shadow-sm transition-colors"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        {/* Explainability Breakdown */}
        <div className="space-y-4">
          {/* Key evaluation parameters */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 bg-[#FFFFFF] border-2 border-[#111111] p-3 text-xs">
            <div>
              <span className="text-[10px] uppercase font-bold text-[#777777] block">Your Age on Cutoff</span>
              <span className="font-mono font-bold text-sm">
                {details?.calculated_age !== null && details?.calculated_age !== undefined 
                  ? `${details.calculated_age} yrs` 
                  : 'N/A'}
              </span>
            </div>
            <div>
              <span className="text-[10px] uppercase font-bold text-[#777777] block">Permitted Age</span>
              <span className="font-mono font-bold text-sm">
                {job.min_age} – {details?.effective_max_age || job.max_age} yrs
              </span>
            </div>
            <div className="col-span-2 sm:col-span-1">
              <span className="text-[10px] uppercase font-bold text-[#777777] block">Category Relaxation</span>
              <span className="font-mono font-bold text-sm text-[#008000]">
                {details?.age_relaxation_applied ? `+${details.age_relaxation_applied} yrs` : '0 yrs'}
              </span>
            </div>
          </div>

          {/* Satisfied Criteria */}
          {reasons && reasons.length > 0 && (
            <div className="border-2 border-[#111111] bg-[#FFFFFF] p-3">
              <h4 className="text-xs font-black uppercase tracking-wider text-[#111111] mb-2 flex items-center gap-1.5">
                <Check size={14} className="text-[#008000] stroke-[3]" />
                Matching Criteria
              </h4>
              <ul className="space-y-1.5 text-xs text-[#222222]">
                {reasons.map((r, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="text-[#008000] font-black">•</span>
                    <span>{r}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Failed Criteria */}
          {failed_criteria && failed_criteria.length > 0 && (
            <div className="border-2 border-[#111111] bg-[#FFF0ED] p-3">
              <h4 className="text-xs font-black uppercase tracking-wider text-[#D12E00] mb-2 flex items-center gap-1.5">
                <AlertCircle size={14} className="stroke-[3]" />
                Unmet Criteria
              </h4>
              <ul className="space-y-1.5 text-xs text-[#111111]">
                {failed_criteria.map((f, i) => (
                  <li key={i} className="flex items-start gap-2 font-medium">
                    <span className="text-[#D12E00] font-black">•</span>
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Warnings or Missing Info */}
          {warnings && warnings.length > 0 && (
            <div className="border-2 border-[#111111] bg-[#FFFDE6] p-3">
              <h4 className="text-xs font-black uppercase tracking-wider text-[#9E6A00] mb-2 flex items-center gap-1.5">
                <Info size={14} className="stroke-[3]" />
                Important Notice / Incomplete Profile
              </h4>
              <ul className="space-y-1.5 text-xs text-[#443800]">
                {warnings.map((w, i) => (
                  <li key={i} className="flex items-start gap-2">
                    <span className="font-bold">•</span>
                    <span>{w}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Additional Certification Requirement */}
          {job.rule?.additional_certification_requirement && (
            <div className="text-xs bg-[#FFFDE6] border-2 border-[#111111] p-3">
              <span className="font-black text-[#111111] uppercase tracking-wider block mb-1">
                Additional Certification / Diploma Requirement:
              </span>
              <p className="font-semibold text-[#111111]">{job.rule.additional_certification_requirement}</p>
            </div>
          )}

          {/* Summary condition & Disclaimer */}
          {job.rule?.conditions_summary && (
            <div className="text-xs text-[#555555] bg-[#E8E2D8] border border-[#111111] p-2.5">
              <span className="font-bold text-[#111111] block mb-0.5">Notification Excerpt:</span>
              <p>{job.rule.conditions_summary}</p>
            </div>
          )}
        </div>

        {/* Footer Actions */}
        <div className="mt-5 pt-4 border-t-2 border-[#111111] flex items-center justify-between">
          <button
            onClick={onClose}
            className="px-4 py-2 text-xs font-bold uppercase bg-white border-2 border-[#111111] hover:bg-[#E8E2D8] brutal-shadow-sm"
          >
            Close
          </button>

          <a
            href={job.original_url}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-black uppercase bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow-sm hover:translate-x-[-1px] hover:translate-y-[-1px] transition-transform"
          >
            <span>Original Notification</span>
            <ExternalLink size={14} />
          </a>
        </div>
      </div>
    </div>
  );
};
