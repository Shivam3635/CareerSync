import React from 'react';
import type { EligibilityStatus } from '../types';
import { CheckCircle2, AlertTriangle, XCircle } from 'lucide-react';

interface EligibilityBadgeProps {
  status: EligibilityStatus;
  size?: 'sm' | 'md';
}

export const EligibilityBadge: React.FC<EligibilityBadgeProps> = ({ status, size = 'md' }) => {
  if (status === 'eligible') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-bold uppercase tracking-wider bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow-sm ${
          size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-3 py-1 text-xs'
        }`}
      >
        <CheckCircle2 size={size === 'sm' ? 12 : 14} className="stroke-[2.5]" />
        ELIGIBLE
      </span>
    );
  }

  if (status === 'review_required') {
    return (
      <span
        className={`inline-flex items-center gap-1.5 font-bold uppercase tracking-wider bg-[#FFFFFF] text-[#111111] border-2 border-[#111111] brutal-shadow-sm ${
          size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-3 py-1 text-xs'
        }`}
      >
        <AlertTriangle size={size === 'sm' ? 12 : 14} className="stroke-[2.5] text-[#E08700]" />
        REVIEW REQUIRED
      </span>
    );
  }

  return (
    <span
      className={`inline-flex items-center gap-1.5 font-bold uppercase tracking-wider bg-[#FF6B4A] text-white border-2 border-[#111111] brutal-shadow-sm ${
        size === 'sm' ? 'px-2 py-0.5 text-[11px]' : 'px-3 py-1 text-xs'
      }`}
    >
      <XCircle size={size === 'sm' ? 12 : 14} className="stroke-[2.5]" />
      NOT ELIGIBLE
    </span>
  );
};
