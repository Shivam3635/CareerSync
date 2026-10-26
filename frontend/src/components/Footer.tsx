import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="w-full bg-[#FFFFFF] border-t-2 border-[#111111] py-8 px-4 sm:px-6 mt-auto">
      <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <span className="w-5 h-5 bg-[#D9FF43] border border-[#111111] inline-block"></span>
            <span className="font-heading font-black text-lg text-[#111111]">
              CareerSync
            </span>
          </div>
          <p className="text-xs text-[#555555] max-w-sm">
            Personalized government job eligibility discovery for Indian exam aspirants.
          </p>
        </div>

        <div className="text-xs text-[#555555] space-y-1">
          <p className="font-bold text-[#111111]">
            Disclaimer & Authoritative Notice:
          </p>
          <p className="max-w-md text-[11px] leading-relaxed">
            CareerSync acts as an informational filter. Always review the official recruitment notification from the issuing authority before submitting applications.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-4 text-xs font-bold text-[#111111]">
          <span>About</span>
          <span>•</span>
          <span>Privacy Policy</span>
          <span>•</span>
          <span>© {new Date().getFullYear()} CareerSync</span>
        </div>
      </div>
    </footer>
  );
};
