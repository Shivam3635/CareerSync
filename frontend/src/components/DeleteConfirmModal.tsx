import React, { useEffect } from 'react';
import { AlertTriangle, Trash2, X, Loader2 } from 'lucide-react';

interface DeleteConfirmModalProps {
  isOpen: boolean;
  job: {
    id: number;
    title: string;
    organization?: string;
    category?: string;
  } | null;
  isDeleting?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

export const DeleteConfirmModal: React.FC<DeleteConfirmModalProps> = ({
  isOpen,
  job,
  isDeleting = false,
  onConfirm,
  onCancel,
}) => {
  // Close on Escape key press
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && isOpen && !isDeleting) {
        onCancel();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, isDeleting, onCancel]);

  if (!isOpen || !job) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#111111]/70 backdrop-blur-xs animate-in fade-in duration-150"
      onClick={(e) => {
        if (e.target === e.currentTarget && !isDeleting) {
          onCancel();
        }
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="delete-dialog-title"
    >
      <div className="w-full max-w-md bg-white border-3 border-[#111111] shadow-[6px_6px_0px_#111111] overflow-hidden">
        {/* Header Bar */}
        <div className="bg-[#FFF0ED] border-b-2 border-[#111111] px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-[#FF6B4A] text-white border-2 border-[#111111] shadow-[2px_2px_0px_#111111]">
              <AlertTriangle className="w-5 h-5 stroke-[2.5]" />
            </div>
            <div>
              <h3
                id="delete-dialog-title"
                className="font-heading font-black text-sm uppercase tracking-wider text-[#111111]"
              >
                Delete Recruitment Post
              </h3>
              <p className="text-[11px] text-[#D12E00] font-bold">
                Permanent admin action
              </p>
            </div>
          </div>
          <button
            type="button"
            onClick={onCancel}
            disabled={isDeleting}
            className="p-1 border-2 border-[#111111] bg-white hover:bg-[#111111] hover:text-white transition-colors disabled:opacity-50"
            aria-label="Close dialog"
          >
            <X size={16} />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-5 space-y-4">
          <p className="text-xs text-[#333333] font-medium leading-relaxed">
            Are you sure you want to permanently delete this government job notification? It will be immediately removed from the portal and aspirants will no longer be matched with it.
          </p>

          {/* Job details preview box */}
          <div className="bg-[#F5F0E8] border-2 border-[#111111] p-3 space-y-1.5">
            <div className="flex items-center gap-2">
              <span className="font-mono text-[10px] uppercase font-bold tracking-wider bg-[#111111] text-[#D9FF43] px-2 py-0.5">
                Post #{job.id}
              </span>
              {job.category && (
                <span className="font-mono text-[10px] uppercase font-bold text-[#666666]">
                  {job.category}
                </span>
              )}
            </div>

            <h4 className="font-heading font-black text-sm text-[#111111] leading-snug">
              {job.title}
            </h4>

            {job.organization && (
              <p className="text-xs text-[#555555] font-bold">
                {job.organization}
              </p>
            )}
          </div>

          {/* Warning notice */}
          <div className="border-l-4 border-[#FF6B4A] bg-[#FFF0ED] p-2.5 text-[11px] font-bold text-[#D12E00] flex items-center gap-2">
            <Trash2 className="w-4 h-4 shrink-0 stroke-[2.5]" />
            <span>This action cannot be undone. All linked eligibility rules will be removed.</span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="bg-[#F5F0E8] border-t-2 border-[#111111] px-5 py-3.5 flex items-center justify-end gap-3">
          <button
            type="button"
            onClick={onCancel}
            disabled={isDeleting}
            className="px-4 py-2 text-xs font-black uppercase tracking-wider bg-white hover:bg-[#E8E2D8] text-[#111111] border-2 border-[#111111] shadow-[2px_2px_0px_#111111] active:translate-x-0.5 active:translate-y-0.5 transition-all disabled:opacity-50"
          >
            Cancel
          </button>

          <button
            type="button"
            onClick={onConfirm}
            disabled={isDeleting}
            className="px-4 py-2 text-xs font-black uppercase tracking-wider bg-[#FF6B4A] hover:bg-[#e85330] text-white border-2 border-[#111111] shadow-[2px_2px_0px_#111111] active:translate-x-0.5 active:translate-y-0.5 transition-all flex items-center gap-1.5 disabled:opacity-60"
          >
            {isDeleting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Deleting...</span>
              </>
            ) : (
              <>
                <Trash2 className="w-4 h-4 stroke-[2.5]" />
                <span>Yes, Delete Post</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
