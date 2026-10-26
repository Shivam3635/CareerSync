import React, { useState, useEffect } from 'react';
import type { Job, QualificationLevel } from '../types';
import { api } from '../services/api';
import { 
  X, 
  Sparkles, 
  Globe, 
  FileText, 
  Edit3, 
  AlertTriangle, 
  CheckCircle2, 
  ExternalLink, 
  Save, 
  XCircle,
  Loader2,
  Calendar,
  Building2,
  Award,
  Users,
  AlertCircle
} from 'lucide-react';

interface AdminAddJobModalProps {
  job: Job | null; // null for new job extraction/creation; Job object for reviewing existing
  isOpen: boolean;
  onClose: () => void;
  onSaved: (message: string) => void;
}

export const AdminAddJobModal: React.FC<AdminAddJobModalProps> = ({
  job,
  isOpen,
  onClose,
  onSaved,
}) => {
  // Navigation: 'choose_source' | 'review'
  const [step, setStep] = useState<'choose_source' | 'review'>(job ? 'review' : 'choose_source');
  const [sourceMethod, setSourceMethod] = useState<'url' | 'pdf' | 'manual'>('url');

  // Input states for Source Selection
  const [urlInput, setUrlInput] = useState('');
  const [pdfFile, setPdfFile] = useState<File | null>(null);
  const [extracting, setExtracting] = useState(false);
  const [extractError, setExtractError] = useState('');

  // Draft Data States
  const [draftJobId, setDraftJobId] = useState<number | null>(job?.id ?? null);
  const [status, setStatus] = useState<string>(job?.status ?? 'pending_review');
  const [title, setTitle] = useState('');
  const [organization, setOrganization] = useState('');
  const [advertisementNumber, setAdvertisementNumber] = useState('');
  const [recruitmentYear, setRecruitmentYear] = useState<number>(new Date().getFullYear());
  const [category, setCategory] = useState('Civil Services');
  const [sourceName, setSourceName] = useState('Official Portal');
  const [originalUrl, setOriginalUrl] = useState('');
  const [uploadedPdf, setUploadedPdf] = useState<string | null>(null);
  const [description, setDescription] = useState('');
  const [selectionProcess, setSelectionProcess] = useState('');

  // Dates
  const [startDate, setStartDate] = useState('');
  const [deadline, setDeadline] = useState('');
  const [cutoffDate, setCutoffDate] = useState('');

  // Ages
  const [minAge, setMinAge] = useState(18);
  const [maxAge, setMaxAge] = useState(30);

  // Vacancies and Fees
  const [totalVacancies, setTotalVacancies] = useState<number | ''>('');
  const [genFee, setGenFee] = useState('Rs. 500');
  const [scFee, setScFee] = useState('Rs. 0');

  // Rule fields
  const [minQual, setMinQual] = useState<QualificationLevel>('Graduate');
  const [allowedStatus, setAllowedStatus] = useState<'completed_only' | 'appearing_allowed'>('completed_only');
  const [domicile, setDomicile] = useState('All India');
  const [obcRelax, setObcRelax] = useState(3);
  const [scRelax, setScRelax] = useState(5);
  const [stRelax, setStRelax] = useState(5);
  const [ewsRelax, setEwsRelax] = useState(0);
  const [conditionsSummary, setConditionsSummary] = useState('');
  const [additionalCert, setAdditionalCert] = useState('');

  // AI Metadata and Review Notes
  const [aiMetadata, setAiMetadata] = useState<any>(null);
  const [reviewNotes, setReviewNotes] = useState('');
  const [savingAction, setSavingAction] = useState<'save' | 'approve' | 'reject' | null>(null);
  const [reviewError, setReviewError] = useState('');

  // Populate state when job prop changes
  useEffect(() => {
    if (job) {
      setStep('review');
      setDraftJobId(job.id);
      setStatus(job.status || 'pending_review');
      setTitle(job.title || '');
      setOrganization(job.organization || '');
      setAdvertisementNumber(job.advertisement_number || '');
      setRecruitmentYear(job.recruitment_year || new Date().getFullYear());
      setCategory(job.category || 'Civil Services');
      setSourceName(job.source_name || 'Official Portal');
      setOriginalUrl(job.original_url || '');
      setUploadedPdf(job.uploaded_pdf || null);
      setDescription(job.description || '');
      setSelectionProcess(job.selection_process || '');

      setStartDate(job.application_start_date || '');
      setDeadline(job.application_deadline || '');
      setCutoffDate(job.age_cutoff_date || '');

      setMinAge(job.min_age || 18);
      setMaxAge(job.max_age || 30);
      setTotalVacancies(job.total_vacancies ?? '');

      const fees = job.application_fee_details || {};
      setGenFee(fees['General/OBC'] || fees['General'] || 'Rs. 500');
      setScFee(fees['SC/ST'] || 'Rs. 0');

      if (job.rule) {
        setMinQual(job.rule.min_qualification_level || 'Graduate');
        setAllowedStatus(job.rule.allowed_status || 'completed_only');
        setDomicile(job.rule.domicile_requirement || 'All India');
        setConditionsSummary(job.rule.conditions_summary || '');
        setAdditionalCert(job.rule.additional_certification_requirement || '');
        const relaxations = job.rule.age_relaxations || {};
        setObcRelax(relaxations.OBC ?? 3);
        setScRelax(relaxations.SC ?? 5);
        setStRelax(relaxations.ST ?? 5);
        setEwsRelax(relaxations.EWS ?? 0);
      } else {
        setAdditionalCert('');
      }

      setAiMetadata(job.ai_extraction_metadata || null);
      setReviewNotes(job.review_notes || '');
    } else {
      // Clean slate for new creation
      setStep('choose_source');
      setDraftJobId(null);
      setStatus('pending_review');
      setUrlInput('');
      setPdfFile(null);
      setExtractError('');
      setReviewError('');
      setAiMetadata(null);
    }
  }, [job, isOpen]);

  const populateFromCreatedDraft = (newJob: Job, meta: any) => {
    setDraftJobId(newJob.id);
    setStatus(newJob.status || 'pending_review');
    setTitle(newJob.title || '');
    setOrganization(newJob.organization || '');
    setAdvertisementNumber(newJob.advertisement_number || '');
    setRecruitmentYear(newJob.recruitment_year || new Date().getFullYear());
    setCategory(newJob.category || 'Civil Services');
    setSourceName(newJob.source_name || 'Official Portal');
    setOriginalUrl(newJob.original_url || '');
    setUploadedPdf(newJob.uploaded_pdf || null);
    setDescription(newJob.description || '');
    setSelectionProcess(newJob.selection_process || '');

    setStartDate(newJob.application_start_date || '');
    setDeadline(newJob.application_deadline || '');
    setCutoffDate(newJob.age_cutoff_date || '');

    setMinAge(newJob.min_age || 18);
    setMaxAge(newJob.max_age || 30);
    setTotalVacancies(newJob.total_vacancies ?? '');

    const fees = newJob.application_fee_details || {};
    setGenFee(fees['General/OBC'] || fees['General'] || 'Rs. 500');
    setScFee(fees['SC/ST'] || 'Rs. 0');

    if (newJob.rule) {
      setMinQual(newJob.rule.min_qualification_level || 'Graduate');
      setAllowedStatus(newJob.rule.allowed_status || 'completed_only');
      setDomicile(newJob.rule.domicile_requirement || 'All India');
      setConditionsSummary(newJob.rule.conditions_summary || '');
      setAdditionalCert(newJob.rule.additional_certification_requirement || '');
      const relaxations = newJob.rule.age_relaxations || {};
      setObcRelax(relaxations.OBC ?? 3);
      setScRelax(relaxations.SC ?? 5);
      setStRelax(relaxations.ST ?? 5);
      setEwsRelax(relaxations.EWS ?? 0);
    } else {
      setAdditionalCert('');
    }

    setAiMetadata(meta || newJob.ai_extraction_metadata || null);
    setReviewNotes(newJob.review_notes || '');
    setStep('review');
  };

  // 1. Handle URL Extraction
  const handleExtractFromUrl = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!urlInput.trim()) {
      setExtractError('Please enter a valid job notification URL.');
      return;
    }
    setExtracting(true);
    setExtractError('');

    try {
      const res = await api.extractJobFromUrl(urlInput.trim());
      populateFromCreatedDraft(res.job, res.metadata);
    } catch (err: any) {
      setExtractError(err.message || 'Failed to extract job details from URL.');
    } finally {
      setExtracting(false);
    }
  };

  // 2. Handle PDF Upload Extraction
  const handleExtractFromPdf = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!pdfFile) {
      setExtractError('Please select a government notification PDF file.');
      return;
    }
    setExtracting(true);
    setExtractError('');

    try {
      const res = await api.extractJobFromPdf(pdfFile);
      populateFromCreatedDraft(res.job, res.metadata);
    } catch (err: any) {
      setExtractError(err.message || 'Failed to extract job details from PDF.');
    } finally {
      setExtracting(false);
    }
  };

  // 3. Handle Manual Entry Choice
  const handleStartManual = () => {
    const now = new Date();
    const todayStr = now.toISOString().split('T')[0];
    const nextMonth = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
    const cutoff = `${now.getFullYear()}-08-01`;

    setDraftJobId(null);
    setStatus('draft');
    setTitle('');
    setOrganization('');
    setAdvertisementNumber('');
    setRecruitmentYear(now.getFullYear());
    setCategory('Civil Services');
    setSourceName('Official Portal');
    setOriginalUrl('');
    setUploadedPdf(null);
    setDescription('');
    setSelectionProcess('Written Examination, Interview, Document Verification');
    setStartDate(todayStr);
    setDeadline(nextMonth);
    setCutoffDate(cutoff);
    setMinAge(18);
    setMaxAge(30);
    setTotalVacancies('');
    setGenFee('Rs. 500');
    setScFee('Rs. 0');
    setMinQual('Graduate');
    setAllowedStatus('completed_only');
    setDomicile('All India');
    setConditionsSummary('');
    setAdditionalCert('');
    setAiMetadata(null);
    setReviewNotes('');
    setStep('review');
  };

  // Build the unified payload for save / approval
  const buildCurrentPayload = (isPublishing: boolean, newStatus: string) => {
    return {
      title: title.trim(),
      organization: organization.trim(),
      advertisement_number: advertisementNumber.trim(),
      recruitment_year: Number(recruitmentYear) || new Date().getFullYear(),
      category,
      source_name: sourceName.trim() || 'Official Portal',
      original_url: originalUrl.trim(),
      description: description.trim(),
      selection_process: selectionProcess.trim(),
      application_start_date: startDate || null,
      application_deadline: deadline || null,
      age_cutoff_date: cutoffDate || deadline || null,
      min_age: Number(minAge) || 18,
      max_age: Number(maxAge) || 30,
      total_vacancies: totalVacancies === '' ? null : Number(totalVacancies),
      application_fee_details: {
        'General/OBC': genFee,
        'SC/ST': scFee,
      },
      status: newStatus,
      is_published: isPublishing,
      review_notes: reviewNotes.trim(),
      min_qualification_level: minQual,
      allowed_status: allowedStatus,
      domicile_requirement: domicile.trim() || 'All India',
      age_relaxations: {
        OBC: Number(obcRelax) || 0,
        SC: Number(scRelax) || 0,
        ST: Number(stRelax) || 0,
        EWS: Number(ewsRelax) || 0,
        GEN: 0,
      },
      conditions_summary: conditionsSummary.trim(),
      additional_certification_requirement: additionalCert.trim(),
    };
  };

  // Action: Save as Draft
  const handleSaveDraft = async () => {
    if (!title.trim() || !organization.trim()) {
      setReviewError('Title and Recruiting Organization are mandatory.');
      return;
    }
    setSavingAction('save');
    setReviewError('');

    try {
      const payload = buildCurrentPayload(false, status === 'approved' ? 'approved' : 'pending_review');
      if (draftJobId) {
        await api.updateAdminJob(draftJobId, payload);
      } else {
        await api.createAdminJob(payload);
      }
      onSaved(`Draft "${title}" saved successfully in ${status === 'approved' ? 'published' : 'pending review'} status.`);
      onClose();
    } catch (err: any) {
      setReviewError(err.message || 'Failed to save draft.');
    } finally {
      setSavingAction(null);
    }
  };

  // Action: Approve & Publish
  const handleApproveAndPublish = async () => {
    if (!title.trim() || !organization.trim()) {
      setReviewError('Title and Recruiting Organization are mandatory for publishing.');
      return;
    }
    if (!deadline) {
      setReviewError('Application deadline is required before approving.');
      return;
    }
    if (minAge > maxAge) {
      setReviewError(`Minimum age (${minAge}) cannot exceed maximum age (${maxAge}).`);
      return;
    }

    setSavingAction('approve');
    setReviewError('');

    try {
      const payload = buildCurrentPayload(true, 'approved');
      let targetId = draftJobId;

      if (!targetId) {
        const createRes = await api.createAdminJob(payload);
        targetId = createRes.job.id;
      } else {
        await api.updateAdminJob(targetId, payload);
      }

      // Explicitly trigger the approval workflow
      const approveRes = await api.approveAdminJob(targetId, reviewNotes);
      onSaved(approveRes.message || `Recruitment "${title}" published and alerts dispatched!`);
      onClose();
    } catch (err: any) {
      setReviewError(err.message || 'Failed to approve and publish recruitment.');
    } finally {
      setSavingAction(null);
    }
  };

  // Action: Reject Draft
  const handleReject = async () => {
    if (!draftJobId) {
      onClose();
      return;
    }
    setSavingAction('reject');
    setReviewError('');

    try {
      const res = await api.rejectAdminJob(draftJobId, reviewNotes);
      onSaved(res.message || `Job "${title}" marked as rejected.`);
      onClose();
    } catch (err: any) {
      setReviewError(err.message || 'Failed to reject job draft.');
    } finally {
      setSavingAction(null);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-black/60 flex items-center justify-center p-4 backdrop-blur-xs">
      <div className="relative w-full max-w-4xl bg-[#F5F0E8] border-4 border-[#111111] shadow-[8px_8px_0px_#111111] my-8 max-h-[92vh] flex flex-col">
        
        {/* Modal Top Header */}
        <div className="flex items-center justify-between p-5 bg-[#111111] text-white border-b-4 border-[#111111]">
          <div className="flex items-center gap-3">
            <span className="p-2 bg-[#D9FF43] text-[#111111] font-mono text-sm font-black border-2 border-white shadow-[2px_2px_0px_white]">
              AI ASSIST
            </span>
            <div>
              <h2 className="text-xl font-black uppercase tracking-tight flex items-center gap-2">
                {step === 'choose_source' ? 'Add Recruitment Notification' : 'Verify & Approve Recruitment Draft'}
              </h2>
              <p className="text-xs text-gray-300 font-mono mt-0.5">
                {step === 'choose_source'
                  ? 'Select URL, PDF, or Manual Entry to begin structured draft creation'
                  : 'Review all extracted data, verify conflicts, and approve for aspirant publishing'}
              </p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1.5 bg-[#FF6B4A] hover:bg-[#ff5530] text-[#111111] border-2 border-white transition-transform hover:scale-105"
            title="Close"
          >
            <X className="w-6 h-6 stroke-[3]" />
          </button>
        </div>

        {/* Modal Content Body */}
        <div className="p-6 overflow-y-auto flex-1 space-y-6">
          
          {/* STEP 1: CHOOSE EXTRACTION SOURCE */}
          {step === 'choose_source' && (
            <div className="space-y-6">
              
              {/* Method Switcher Tabs */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                <button
                  type="button"
                  onClick={() => setSourceMethod('url')}
                  className={`p-4 border-3 text-left transition-all ${
                    sourceMethod === 'url'
                      ? 'bg-[#D9FF43] border-[#111111] shadow-[4px_4px_0px_#111111]'
                      : 'bg-white border-[#111111]/40 hover:border-[#111111]'
                  }`}
                >
                  <div className="flex items-center gap-2 font-black text-sm uppercase text-[#111111]">
                    <Globe className="w-5 h-5 text-[#111111]" />
                    1. Portal / Sarkari URL
                  </div>
                  <p className="text-xs text-gray-700 mt-1 font-mono">
                    Paste Sarkari Result or notification webpage link.
                  </p>
                </button>

                <button
                  type="button"
                  onClick={() => setSourceMethod('pdf')}
                  className={`p-4 border-3 text-left transition-all ${
                    sourceMethod === 'pdf'
                      ? 'bg-[#D9FF43] border-[#111111] shadow-[4px_4px_0px_#111111]'
                      : 'bg-white border-[#111111]/40 hover:border-[#111111]'
                  }`}
                >
                  <div className="flex items-center gap-2 font-black text-sm uppercase text-[#111111]">
                    <FileText className="w-5 h-5 text-[#111111]" />
                    2. Upload PDF Notification
                  </div>
                  <p className="text-xs text-gray-700 mt-1 font-mono">
                    Upload official gazette / advertisement PDF (up to 15MB).
                  </p>
                </button>

                <button
                  type="button"
                  onClick={() => setSourceMethod('manual')}
                  className={`p-4 border-3 text-left transition-all ${
                    sourceMethod === 'manual'
                      ? 'bg-[#D9FF43] border-[#111111] shadow-[4px_4px_0px_#111111]'
                      : 'bg-white border-[#111111]/40 hover:border-[#111111]'
                  }`}
                >
                  <div className="flex items-center gap-2 font-black text-sm uppercase text-[#111111]">
                    <Edit3 className="w-5 h-5 text-[#111111]" />
                    3. Manual Entry
                  </div>
                  <p className="text-xs text-gray-700 mt-1 font-mono">
                    Enter all vacancy and eligibility rules manually.
                  </p>
                </button>
              </div>

              {/* Extraction Error Banner */}
              {extractError && (
                <div className="p-4 bg-[#FF6B4A]/20 border-3 border-[#FF6B4A] text-[#111111] flex items-start gap-3">
                  <AlertTriangle className="w-5 h-5 text-[#FF6B4A] shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-black text-sm uppercase">Extraction Halted</h4>
                    <p className="text-xs font-mono mt-0.5">{extractError}</p>
                  </div>
                </div>
              )}

              {/* TAB 1: URL EXTRACTION FORM */}
              {sourceMethod === 'url' && (
                <form onSubmit={handleExtractFromUrl} className="bg-white border-3 border-[#111111] p-6 shadow-[4px_4px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-[#111111]" />
                    <h3 className="font-black uppercase text-base text-[#111111]">
                      Paste Government Job Announcement URL
                    </h3>
                  </div>
                  <p className="text-xs text-gray-600 font-mono">
                    CareerSync automatically applies SSRF safeguards, strips advertisements, confirms it is an active recruitment notification (rejecting admit cards / exam results), and normalizes dates and vacancy figures.
                  </p>

                  <div className="space-y-1">
                    <label className="block text-xs font-black uppercase text-[#111111]">
                      Recruitment Page URL <span className="text-[#FF6B4A]">*</span>
                    </label>
                    <input
                      type="url"
                      required
                      placeholder="https://www.sarkariresult.com/2026/upsc-civil-services.php"
                      value={urlInput}
                      onChange={(e) => setUrlInput(e.target.value)}
                      disabled={extracting}
                      className="w-full p-3 bg-[#F5F0E8] border-2 border-[#111111] font-mono text-sm focus:outline-hidden focus:bg-white"
                    />
                  </div>

                  <div className="pt-2 flex justify-between items-center">
                    <span className="text-xs font-mono text-gray-500">
                      Supports: Sarkari Result, UPSC, SSC, IBPS, State PSCs, RRB
                    </span>
                    <button
                      type="submit"
                      disabled={extracting}
                      className="px-6 py-3 bg-[#D9FF43] hover:bg-[#cbf532] text-[#111111] font-black uppercase text-sm border-2 border-[#111111] shadow-[3px_3px_0px_#111111] flex items-center gap-2 transition-transform active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-50"
                    >
                      {extracting ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Extracting & Structuring...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4" />
                          Generate Draft with AI
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}

              {/* TAB 2: PDF UPLOAD FORM */}
              {sourceMethod === 'pdf' && (
                <form onSubmit={handleExtractFromPdf} className="bg-white border-3 border-[#111111] p-6 shadow-[4px_4px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2">
                    <FileText className="w-5 h-5 text-[#111111]" />
                    <h3 className="font-black uppercase text-base text-[#111111]">
                      Upload Official Notification PDF
                    </h3>
                  </div>
                  <p className="text-xs text-gray-600 font-mono">
                    Upload the official recruitment PDF. CareerSync parses digital text, extracts category vacancy tables and age relaxations, and preserves the document securely in media storage.
                  </p>

                  <div className="border-2 border-dashed border-[#111111] p-8 text-center bg-[#F5F0E8]/50 hover:bg-[#F5F0E8] transition-colors cursor-pointer relative">
                    <input
                      type="file"
                      accept=".pdf,application/pdf"
                      required
                      disabled={extracting}
                      onChange={(e) => {
                        if (e.target.files && e.target.files[0]) {
                          setPdfFile(e.target.files[0]);
                        }
                      }}
                      className="absolute inset-0 opacity-0 cursor-pointer"
                    />
                    <FileText className="w-10 h-10 mx-auto text-[#111111]/70 mb-2" />
                    {pdfFile ? (
                      <div className="font-mono text-sm">
                        <span className="font-bold text-[#111111]">{pdfFile.name}</span>
                        <span className="text-xs text-gray-500 ml-2">
                          ({(pdfFile.size / (1024 * 1024)).toFixed(2)} MB)
                        </span>
                      </div>
                    ) : (
                      <div className="space-y-1">
                        <p className="font-black text-sm uppercase text-[#111111]">
                          Click or drag & drop recruitment notification PDF
                        </p>
                        <p className="text-xs text-gray-500 font-mono">Max size: 15 MB (.pdf only)</p>
                      </div>
                    )}
                  </div>

                  <div className="pt-2 flex justify-end">
                    <button
                      type="submit"
                      disabled={extracting || !pdfFile}
                      className="px-6 py-3 bg-[#D9FF43] hover:bg-[#cbf532] text-[#111111] font-black uppercase text-sm border-2 border-[#111111] shadow-[3px_3px_0px_#111111] flex items-center gap-2 transition-transform active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-50"
                    >
                      {extracting ? (
                        <>
                          <Loader2 className="w-4 h-4 animate-spin" />
                          Parsing & Structuring PDF...
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4" />
                          Parse Notification PDF
                        </>
                      )}
                    </button>
                  </div>
                </form>
              )}

              {/* TAB 3: MANUAL ENTRY */}
              {sourceMethod === 'manual' && (
                <div className="bg-white border-3 border-[#111111] p-6 shadow-[4px_4px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2">
                    <Edit3 className="w-5 h-5 text-[#111111]" />
                    <h3 className="font-black uppercase text-base text-[#111111]">
                      Manual Job Notification Creation
                    </h3>
                  </div>
                  <p className="text-xs text-gray-600 font-mono">
                    Skip AI extraction and directly open the structured job editor to manually input dates, age criteria, category relaxations, and educational qualifications.
                  </p>
                  <div className="pt-2">
                    <button
                      type="button"
                      onClick={handleStartManual}
                      className="px-6 py-3 bg-[#D9FF43] hover:bg-[#cbf532] text-[#111111] font-black uppercase text-sm border-2 border-[#111111] shadow-[3px_3px_0px_#111111] flex items-center gap-2 transition-transform active:translate-x-0.5 active:translate-y-0.5"
                    >
                      <Edit3 className="w-4 h-4" />
                      Open Manual Editor
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* STEP 2: VERIFICATION & REVIEW FORM */}
          {step === 'review' && (
            <div className="space-y-6">
              
              {/* Review Header Banner: Status + Confidence + Source */}
              <div className="p-4 bg-white border-3 border-[#111111] shadow-[3px_3px_0px_#111111] flex flex-wrap items-center justify-between gap-3">
                <div className="flex items-center gap-3">
                  <span
                    className={`px-3 py-1 text-xs font-mono font-black uppercase border-2 border-[#111111] ${
                      status === 'approved'
                        ? 'bg-[#D9FF43] text-[#111111]'
                        : status === 'pending_review'
                        ? 'bg-amber-300 text-[#111111]'
                        : status === 'rejected'
                        ? 'bg-[#FF6B4A] text-white'
                        : 'bg-gray-200 text-[#111111]'
                    }`}
                  >
                    STATUS: {status.replace('_', ' ')}
                  </span>

                  {aiMetadata?.confidence_score !== undefined && (
                    <span className="px-2.5 py-1 text-xs font-mono font-bold bg-[#F5F0E8] border border-[#111111]">
                      AI Confidence: {(aiMetadata.confidence_score * 100).toFixed(0)}%
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-2 text-xs font-mono">
                  {originalUrl && (
                    <a
                      href={originalUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 font-bold text-[#111111] underline hover:text-[#FF6B4A]"
                    >
                      <Globe className="w-3.5 h-3.5" /> Source URL
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}

                  {uploadedPdf && (
                    <a
                      href={`/media/${uploadedPdf}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center gap-1 font-bold text-[#111111] underline hover:text-[#FF6B4A] ml-2"
                    >
                      <FileText className="w-3.5 h-3.5" /> Source PDF
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}

                  {!job && (
                    <button
                      type="button"
                      onClick={() => setStep('choose_source')}
                      className="text-xs text-gray-600 underline hover:text-black ml-3"
                    >
                      Change Source
                    </button>
                  )}
                </div>
              </div>

              {/* CONFLICTS ALERT BANNER (CRITICAL) */}
              {aiMetadata?.conflicts && aiMetadata.conflicts.length > 0 && (
                <div className="p-4 bg-[#FF6B4A]/25 border-3 border-[#FF6B4A] text-[#111111]">
                  <div className="flex items-center gap-2 font-black text-sm uppercase text-[#FF6B4A]">
                    <AlertTriangle className="w-5 h-5 stroke-[2.5]" />
                    Attention: AI Detected Conflicting Information in Source
                  </div>
                  <p className="text-xs text-gray-700 mt-1 font-mono">
                    The source notification contains contradictory values. Please resolve the fields below before approving:
                  </p>
                  <ul className="list-disc list-inside mt-2 text-xs font-mono space-y-1 font-bold">
                    {aiMetadata.conflicts.map((conflict: string, idx: number) => (
                      <li key={idx} className="text-[#111111]">{conflict}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Operational / AI Notice Banner */}
              {aiMetadata?.warnings && aiMetadata.warnings.filter((w: string) => w.startsWith('AI notice:')).map((notice: string, idx: number) => (
                <div key={idx} className="p-3 bg-blue-50 border-2 border-blue-400 text-blue-900 text-xs font-mono font-semibold flex items-center gap-2">
                  <Sparkles className="w-4 h-4 text-blue-600 shrink-0" />
                  <span>{notice}</span>
                </div>
              ))}

              {/* WARNINGS & MISSING INFO BANNER */}
              {aiMetadata?.warnings && aiMetadata.warnings.filter((w: string) => !w.startsWith('AI notice:')).length > 0 && (
                <div className="p-4 bg-amber-100 border-2 border-amber-500 text-[#111111]">
                  <div className="flex items-center gap-2 font-black text-xs uppercase text-amber-900">
                    <AlertCircle className="w-4 h-4 text-amber-700" />
                    Notice Fields to Verify or Complete
                  </div>
                  <ul className="list-disc list-inside mt-1.5 text-xs font-mono space-y-0.5 text-amber-950">
                    {aiMetadata.warnings.filter((w: string) => !w.startsWith('AI notice:')).map((warn: string, idx: number) => (
                      <li key={idx}>{warn}</li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Review Error Banner */}
              {reviewError && (
                <div className="p-3 bg-[#FF6B4A]/20 border-2 border-[#FF6B4A] text-[#111111] text-xs font-mono font-bold">
                  {reviewError}
                </div>
              )}

              {/* EDITABLE FORM SECTIONS */}
              <div className="space-y-6">
                
                {/* Section 1: Basic Identification */}
                <div className="bg-white border-3 border-[#111111] p-5 shadow-[3px_3px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2 border-b-2 border-[#111111] pb-2 font-black uppercase text-sm text-[#111111]">
                    <Building2 className="w-4 h-4" />
                    1. Job Identification & Organization
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-1 md:col-span-2">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Job Notification Title <span className="text-[#FF6B4A]">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-bold focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Recruiting Organization / Commission <span className="text-[#FF6B4A]">*</span>
                      </label>
                      <input
                        type="text"
                        required
                        value={organization}
                        onChange={(e) => setOrganization(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Recruitment Category
                      </label>
                      <select
                        value={category}
                        onChange={(e) => setCategory(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      >
                        <option value="Civil Services">Civil Services & Administration</option>
                        <option value="Banking">Banking & Finance</option>
                        <option value="Railways">Railways</option>
                        <option value="Defense">Defense & Paramilitary</option>
                        <option value="Engineering & Tech">Engineering & Technology</option>
                        <option value="Teaching">Teaching & Academia</option>
                        <option value="Police & Security">Police & State Security</option>
                        <option value="General">General Recruitment</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Advertisement Number / Notice ID
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. 05/2026-CSP or Advt 02/2026"
                        value={advertisementNumber}
                        onChange={(e) => setAdvertisementNumber(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Recruitment Year
                      </label>
                      <input
                        type="number"
                        value={recruitmentYear}
                        onChange={(e) => setRecruitmentYear(Number(e.target.value))}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>

                {/* Section 2: Critical Dates */}
                <div className="bg-white border-3 border-[#111111] p-5 shadow-[3px_3px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2 border-b-2 border-[#111111] pb-2 font-black uppercase text-sm text-[#111111]">
                    <Calendar className="w-4 h-4" />
                    2. Application Dates & Cutoff Schedule
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Application Start Date
                      </label>
                      <input
                        type="date"
                        value={startDate}
                        onChange={(e) => setStartDate(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Application Deadline <span className="text-[#FF6B4A]">*</span>
                      </label>
                      <input
                        type="date"
                        required
                        value={deadline}
                        onChange={(e) => setDeadline(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Age Calculation Cutoff Date <span className="text-[#FF6B4A]">*</span>
                      </label>
                      <input
                        type="date"
                        required
                        value={cutoffDate}
                        onChange={(e) => setCutoffDate(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>

                {/* Section 3: Age Limits & Relaxations */}
                <div className="bg-white border-3 border-[#111111] p-5 shadow-[3px_3px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2 border-b-2 border-[#111111] pb-2 font-black uppercase text-sm text-[#111111]">
                    <Users className="w-4 h-4" />
                    3. Age Criteria & Category-Wise Relaxations
                  </div>

                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Minimum Age
                      </label>
                      <input
                        type="number"
                        min={16}
                        max={60}
                        value={minAge}
                        onChange={(e) => setMinAge(Number(e.target.value))}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Maximum Age (General)
                      </label>
                      <input
                        type="number"
                        min={16}
                        max={65}
                        value={maxAge}
                        onChange={(e) => setMaxAge(Number(e.target.value))}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        OBC Relaxation (Years)
                      </label>
                      <input
                        type="number"
                        min={0}
                        max={15}
                        value={obcRelax}
                        onChange={(e) => setObcRelax(Number(e.target.value))}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        SC / ST Relaxation (Years)
                      </label>
                      <input
                        type="number"
                        min={0}
                        max={15}
                        value={scRelax}
                        onChange={(e) => {
                          const val = Number(e.target.value);
                          setScRelax(val);
                          setStRelax(val);
                        }}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>

                {/* Section 4: Eligibility Rules */}
                <div className="bg-white border-3 border-[#111111] p-5 shadow-[3px_3px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2 border-b-2 border-[#111111] pb-2 font-black uppercase text-sm text-[#111111]">
                    <Award className="w-4 h-4" />
                    4. Qualification & Domicile Eligibility
                  </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Min Academic Level
                      </label>
                      <select
                        value={minQual}
                        onChange={(e) => setMinQual(e.target.value as QualificationLevel)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      >
                        <option value="10th">10th Standard / Matriculation</option>
                        <option value="12th">12th Standard / Intermediate</option>
                        <option value="Graduate">Bachelor / Graduate Degree</option>
                        <option value="Post Graduate">Master / Post Graduate Degree</option>
                        <option value="Doctorate">Doctorate / Ph.D.</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Degree Completion Rule
                      </label>
                      <select
                        value={allowedStatus}
                        onChange={(e) => setAllowedStatus(e.target.value as any)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      >
                        <option value="completed_only">Completed Degree Only</option>
                        <option value="appearing_allowed">Final Year Appearing Allowed</option>
                      </select>
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Domicile Restriction
                      </label>
                      <input
                        type="text"
                        value={domicile}
                        onChange={(e) => setDomicile(e.target.value)}
                        placeholder="All India or State name"
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>
                  </div>

                  <div className="space-y-1 pt-2">
                    <label className="block text-xs font-black uppercase text-[#111111] flex items-center justify-between">
                      <span>Additional Certification Requirement</span>
                      <span className="text-[10px] text-[#666666] font-normal normal-case">Optional: Polytechnic, ITI, CCC, B.Ed, typing, etc.</span>
                    </label>
                    <input
                      type="text"
                      value={additionalCert}
                      onChange={(e) => setAdditionalCert(e.target.value)}
                      placeholder="e.g. 3-Year Polytechnic Diploma in Mechanical/Civil, ITI Trade Certificate, CCC Computer Course, B.Ed"
                      className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                    />
                  </div>
                </div>

                {/* Section 5: Vacancies, Fees, and Selection */}
                <div className="bg-white border-3 border-[#111111] p-5 shadow-[3px_3px_0px_#111111] space-y-4">
                  <div className="flex items-center gap-2 border-b-2 border-[#111111] pb-2 font-black uppercase text-sm text-[#111111]">
                    <Users className="w-4 h-4" />
                    5. Vacancy Count, Application Fee & Selection Stages
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Total Vacancies
                      </label>
                      <input
                        type="number"
                        placeholder="e.g. 1056"
                        value={totalVacancies}
                        onChange={(e) => setTotalVacancies(e.target.value === '' ? '' : Number(e.target.value))}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Fee (General / OBC)
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Rs. 500"
                        value={genFee}
                        onChange={(e) => setGenFee(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Fee (SC / ST / Reserved)
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Rs. 0 (Exempted)"
                        value={scFee}
                        onChange={(e) => setScFee(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1 md:col-span-3">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Selection Process & Stages
                      </label>
                      <input
                        type="text"
                        placeholder="e.g. Prelims Exam, Mains Exam, Interview, Medical Examination"
                        value={selectionProcess}
                        onChange={(e) => setSelectionProcess(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1 md:col-span-3">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Official Notification / Application URL
                      </label>
                      <input
                        type="url"
                        placeholder="https://..."
                        value={originalUrl}
                        onChange={(e) => setOriginalUrl(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>

                    <div className="space-y-1 md:col-span-3">
                      <label className="block text-xs font-black uppercase text-[#111111]">
                        Admin Verification & Review Notes
                      </label>
                      <textarea
                        rows={2}
                        placeholder="Internal notes, verified against official gazette, source verified..."
                        value={reviewNotes}
                        onChange={(e) => setReviewNotes(e.target.value)}
                        className="w-full p-2.5 bg-[#F5F0E8] border-2 border-[#111111] text-sm font-mono focus:bg-white focus:outline-hidden"
                      />
                    </div>
                  </div>
                </div>

              </div>
            </div>
          )}

        </div>

        {/* Modal Bottom Actions Footer */}
        {step === 'review' && (
          <div className="p-4 bg-white border-t-4 border-[#111111] flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-2">
              {draftJobId && (
                <button
                  type="button"
                  onClick={handleReject}
                  disabled={savingAction !== null}
                  className="px-4 py-2 bg-gray-200 hover:bg-[#FF6B4A] hover:text-white text-[#111111] font-black uppercase text-xs border-2 border-[#111111] transition-colors disabled:opacity-50 flex items-center gap-1.5"
                >
                  <XCircle className="w-4 h-4" />
                  Reject Draft
                </button>
              )}
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={handleSaveDraft}
                disabled={savingAction !== null}
                className="px-5 py-2.5 bg-white hover:bg-gray-100 text-[#111111] font-black uppercase text-xs border-2 border-[#111111] shadow-[2px_2px_0px_#111111] transition-transform active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-50 flex items-center gap-2"
              >
                {savingAction === 'save' ? <Loader2 className="w-4 h-4 animate-spin" /> : <Save className="w-4 h-4" />}
                Save Draft (Keep Unlisted)
              </button>

              <button
                type="button"
                onClick={handleApproveAndPublish}
                disabled={savingAction !== null}
                className="px-6 py-2.5 bg-[#D9FF43] hover:bg-[#cbf532] text-[#111111] font-black uppercase text-xs border-2 border-[#111111] shadow-[3px_3px_0px_#111111] transition-transform active:translate-x-0.5 active:translate-y-0.5 disabled:opacity-50 flex items-center gap-2"
              >
                {savingAction === 'approve' ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Approving & Dispatching...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-4 h-4 stroke-[2.5]" />
                    Approve & Publish
                  </>
                )}
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
};
