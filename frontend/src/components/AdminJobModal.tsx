import React, { useState, useEffect } from 'react';
import type { Job, QualificationLevel } from '../types';
import { api } from '../services/api';
import { X, Save, AlertCircle } from 'lucide-react';

interface AdminJobModalProps {
  job: Job | null; // null for Create, Job object for Edit
  isOpen: boolean;
  onClose: () => void;
  onSaved: (message: string) => void;
}

export const AdminJobModal: React.FC<AdminJobModalProps> = ({
  job,
  isOpen,
  onClose,
  onSaved,
}) => {
  const isEditing = !!job;

  const [title, setTitle] = useState('');
  const [organization, setOrganization] = useState('');
  const [category, setCategory] = useState('Civil Services');
  const [sourceName, setSourceName] = useState('Official Portal');
  const [originalUrl, setOriginalUrl] = useState('');
  const [description, setDescription] = useState('');

  const [startDate, setStartDate] = useState('');
  const [deadline, setDeadline] = useState('');
  const [cutoffDate, setCutoffDate] = useState('');

  const [minAge, setMinAge] = useState(18);
  const [maxAge, setMaxAge] = useState(30);

  const [obcRelax, setObcRelax] = useState(3);
  const [scRelax, setScRelax] = useState(5);
  const [stRelax, setStRelax] = useState(5);
  const [ewsRelax, setEwsRelax] = useState(0);

  const [minQual, setMinQual] = useState<QualificationLevel>('Graduate');
  const [allowedStatus, setAllowedStatus] = useState<'completed_only' | 'appearing_allowed'>('completed_only');
  const [domicile, setDomicile] = useState('All India');
  const [conditionsSummary, setConditionsSummary] = useState('');
  const [additionalCert, setAdditionalCert] = useState('');
  const [isPublished, setIsPublished] = useState(true);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (job) {
      setTitle(job.title || '');
      setOrganization(job.organization || '');
      setCategory(job.category || 'Civil Services');
      setSourceName(job.source_name || 'Official Portal');
      setOriginalUrl(job.original_url || '');
      setDescription(job.description || '');

      setStartDate(job.application_start_date || '');
      setDeadline(job.application_deadline || '');
      setCutoffDate(job.age_cutoff_date || '');

      setMinAge(job.min_age || 18);
      setMaxAge(job.max_age || 30);
      setIsPublished(job.is_published ?? true);

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
    } else {
      // Default dates for new job
      const now = new Date();
      const todayStr = now.toISOString().split('T')[0];
      const nextMonth = new Date(now.getTime() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0];
      const cutoff = `${now.getFullYear()}-08-01`;

      setTitle('');
      setOrganization('');
      setCategory('Civil Services');
      setSourceName('Official Portal');
      setOriginalUrl('');
      setDescription('');
      setStartDate(todayStr);
      setDeadline(nextMonth);
      setCutoffDate(cutoff);
      setMinAge(18);
      setMaxAge(30);
      setObcRelax(3);
      setScRelax(5);
      setStRelax(5);
      setEwsRelax(0);
      setMinQual('Graduate');
      setAllowedStatus('completed_only');
      setDomicile('All India');
      setConditionsSummary('');
      setAdditionalCert('');
      setIsPublished(true);
    }
    setError('');
  }, [job, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setError('');

    const payload = {
      title,
      organization,
      category,
      source_name: sourceName,
      original_url: originalUrl,
      description,
      application_start_date: startDate,
      application_deadline: deadline,
      age_cutoff_date: cutoffDate,
      min_age: Number(minAge),
      max_age: Number(maxAge),
      is_published: isPublished,
      min_qualification_level: minQual,
      allowed_status: allowedStatus,
      domicile_requirement: domicile,
      conditions_summary: conditionsSummary,
      additional_certification_requirement: additionalCert.trim(),
      age_relaxations: {
        OBC: Number(obcRelax),
        SC: Number(scRelax),
        ST: Number(stRelax),
        EWS: Number(ewsRelax),
        GEN: 0,
      },
    };

    try {
      if (isEditing && job) {
        const res = await api.updateAdminJob(job.id, payload);
        onSaved(res.message || 'Job updated successfully.');
      } else {
        const res = await api.createAdminJob(payload);
        onSaved(res.message || 'Job created successfully.');
      }
      onClose();
    } catch (err: any) {
      setError(err.message || 'Failed to save recruitment notification.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#111111]/70 backdrop-blur-xs">
      <div className="w-full max-w-2xl bg-[#F5F0E8] border-3 border-[#111111] brutal-shadow-lg p-6 max-h-[92vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between border-b-2 border-[#111111] pb-3 mb-4">
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-[#D9FF43] border border-[#111111] inline-block"></span>
            <h3 className="font-heading font-black text-xl text-[#111111]">
              {isEditing ? 'Edit Recruitment Opportunity' : 'Create Recruitment Opportunity'}
            </h3>
          </div>
          <button
            onClick={onClose}
            className="p-1 border-2 border-[#111111] bg-white hover:bg-[#FF6B4A] hover:text-white brutal-shadow-sm transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-[#FFF0ED] border-2 border-[#111111] text-xs font-bold text-[#D12E00] flex items-center gap-2">
            <AlertCircle size={16} />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 text-xs font-bold text-[#111111]">
          {/* Section 1: Basic Information */}
          <div className="bg-white border-2 border-[#111111] p-3.5 space-y-3 brutal-shadow-sm">
            <span className="font-mono text-[10px] font-black uppercase tracking-wider bg-[#111111] text-[#D9FF43] px-2 py-0.5">
              1. Basic Information
            </span>

            <div>
              <label className="block uppercase tracking-wider mb-1">
                Recruitment Title <span className="text-[#FF6B4A]">*</span>
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Combined Graduate Level Examination (SSC CGL) 2026"
                className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Issuing Organization <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={organization}
                  onChange={(e) => setOrganization(e.target.value)}
                  placeholder="e.g. Staff Selection Commission (SSC)"
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
                />
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Recruitment Category <span className="text-[#FF6B4A]">*</span>
                </label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-bold focus:outline-none focus:bg-white"
                >
                  <option value="Civil Services">Civil Services</option>
                  <option value="Banking">Banking & Finance</option>
                  <option value="Railways">Railways</option>
                  <option value="Defense">Defense</option>
                  <option value="Engineering & Tech">Engineering & Tech</option>
                  <option value="Teaching">Teaching</option>
                  <option value="Police & Security">Police & Security</option>
                  <option value="General">General Recruitment</option>
                </select>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Official Notification URL <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="url"
                  required
                  value={originalUrl}
                  onChange={(e) => setOriginalUrl(e.target.value)}
                  placeholder="https://ssc.gov.in/portal/cgl-notice.pdf"
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
                />
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Source / Portal Name
                </label>
                <input
                  type="text"
                  value={sourceName}
                  onChange={(e) => setSourceName(e.target.value)}
                  placeholder="e.g. Official SSC Portal"
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
                />
              </div>
            </div>

            <div>
              <label className="block uppercase tracking-wider mb-1">
                Description
              </label>
              <textarea
                rows={2}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Brief summary of vacancies and posts..."
                className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
              />
            </div>
          </div>

          {/* Section 2: Dates & Age Rules */}
          <div className="bg-white border-2 border-[#111111] p-3.5 space-y-3 brutal-shadow-sm">
            <span className="font-mono text-[10px] font-black uppercase tracking-wider bg-[#111111] text-[#D9FF43] px-2 py-0.5">
              2. Dates & Age Criteria
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Start Date <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={startDate}
                  onChange={(e) => setStartDate(e.target.value)}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] font-mono text-xs focus:outline-none focus:bg-white"
                />
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Deadline <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={deadline}
                  onChange={(e) => setDeadline(e.target.value)}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] font-mono text-xs focus:outline-none focus:bg-white"
                />
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Age Cutoff Date <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="date"
                  required
                  value={cutoffDate}
                  onChange={(e) => setCutoffDate(e.target.value)}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] font-mono text-xs focus:outline-none focus:bg-white"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Min Age (Years) <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="number"
                  min={14}
                  max={60}
                  required
                  value={minAge}
                  onChange={(e) => setMinAge(Number(e.target.value))}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] font-mono text-xs focus:outline-none focus:bg-white"
                />
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Max Age (UR / General) <span className="text-[#FF6B4A]">*</span>
                </label>
                <input
                  type="number"
                  min={18}
                  max={65}
                  required
                  value={maxAge}
                  onChange={(e) => setMaxAge(Number(e.target.value))}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] font-mono text-xs focus:outline-none focus:bg-white"
                />
              </div>
            </div>

            {/* Category Relaxations */}
            <div>
              <span className="block uppercase tracking-wider text-[11px] mb-1.5 text-[#555555]">
                Category-based Age Relaxation (Years):
              </span>
              <div className="grid grid-cols-4 gap-2 text-center">
                <div>
                  <span className="text-[10px] uppercase font-mono block mb-1">OBC</span>
                  <input
                    type="number"
                    min={0}
                    max={15}
                    value={obcRelax}
                    onChange={(e) => setObcRelax(Number(e.target.value))}
                    className="w-full p-1.5 text-center bg-[#F5F0E8] border border-[#111111] font-mono text-xs"
                  />
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono block mb-1">SC</span>
                  <input
                    type="number"
                    min={0}
                    max={15}
                    value={scRelax}
                    onChange={(e) => setScRelax(Number(e.target.value))}
                    className="w-full p-1.5 text-center bg-[#F5F0E8] border border-[#111111] font-mono text-xs"
                  />
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono block mb-1">ST</span>
                  <input
                    type="number"
                    min={0}
                    max={15}
                    value={stRelax}
                    onChange={(e) => setStRelax(Number(e.target.value))}
                    className="w-full p-1.5 text-center bg-[#F5F0E8] border border-[#111111] font-mono text-xs"
                  />
                </div>
                <div>
                  <span className="text-[10px] uppercase font-mono block mb-1">EWS</span>
                  <input
                    type="number"
                    min={0}
                    max={15}
                    value={ewsRelax}
                    onChange={(e) => setEwsRelax(Number(e.target.value))}
                    className="w-full p-1.5 text-center bg-[#F5F0E8] border border-[#111111] font-mono text-xs"
                  />
                </div>
              </div>
            </div>
          </div>

          {/* Section 3: Educational Qualifications & Domicile */}
          <div className="bg-white border-2 border-[#111111] p-3.5 space-y-3 brutal-shadow-sm">
            <span className="font-mono text-[10px] font-black uppercase tracking-wider bg-[#111111] text-[#D9FF43] px-2 py-0.5">
              3. Qualification & Domicile Rules
            </span>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Min Academic Level <span className="text-[#FF6B4A]">*</span>
                </label>
                <select
                  value={minQual}
                  onChange={(e) => setMinQual(e.target.value as QualificationLevel)}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-bold focus:outline-none focus:bg-white"
                >
                  <option value="10th">10th Standard / Matric</option>
                  <option value="12th">12th Standard / Inter</option>
                  <option value="Graduate">Bachelor / Graduate Degree</option>
                  <option value="Post Graduate">Master / Post Graduate</option>
                  <option value="Doctorate">Doctorate / Ph.D.</option>
                </select>
              </div>

              <div>
                <label className="block uppercase tracking-wider mb-1">
                  Allowed Completion Status <span className="text-[#FF6B4A]">*</span>
                </label>
                <select
                  value={allowedStatus}
                  onChange={(e) => setAllowedStatus(e.target.value as any)}
                  className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-bold focus:outline-none focus:bg-white"
                >
                  <option value="completed_only">Completed Degree Only</option>
                  <option value="appearing_allowed">Final Year / Appearing Candidates Allowed</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block uppercase tracking-wider mb-1">
                Additional Certification Requirement (Optional)
              </label>
              <input
                type="text"
                value={additionalCert}
                onChange={(e) => setAdditionalCert(e.target.value)}
                placeholder="e.g. 3-Year Polytechnic Diploma in Mechanical/Civil, ITI Motor Mechanic, CCC, B.Ed"
                className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
              />
            </div>

            <div>
              <label className="block uppercase tracking-wider mb-1">
                State Domicile Requirement
              </label>
              <input
                type="text"
                value={domicile}
                onChange={(e) => setDomicile(e.target.value)}
                placeholder="'All India' or specific state (e.g. Uttar Pradesh, Haryana)"
                className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
              />
            </div>

            <div>
              <label className="block uppercase tracking-wider mb-1">
                Notification Conditions Summary
              </label>
              <input
                type="text"
                value={conditionsSummary}
                onChange={(e) => setConditionsSummary(e.target.value)}
                placeholder="e.g. Bachelor Degree from any recognized university or equivalent."
                className="w-full p-2 bg-[#F5F0E8] border border-[#111111] text-xs font-semibold focus:outline-none focus:bg-white"
              />
            </div>
          </div>

          {/* Publication checkbox */}
          <div className="bg-[#D9FF43] border-2 border-[#111111] p-3 flex items-center justify-between brutal-shadow-sm">
            <div>
              <span className="block font-black text-xs uppercase tracking-wider">
                Publication Status
              </span>
              <span className="text-[11px] font-semibold text-[#333333]">
                {isPublished 
                  ? 'Published: Will be visible on student dashboards and trigger email alerts.'
                  : 'Draft / Unpublished: Invisible to candidates.'}
              </span>
            </div>
            <label className="flex items-center gap-2 cursor-pointer font-black text-xs uppercase">
              <input
                type="checkbox"
                checked={isPublished}
                onChange={(e) => setIsPublished(e.target.checked)}
                className="w-4 h-4 accent-[#111111]"
              />
              <span>Published</span>
            </label>
          </div>

          {/* Action buttons */}
          <div className="pt-2 flex items-center justify-between">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-bold uppercase bg-white border-2 border-[#111111] hover:bg-[#E8E2D8]"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={saving}
              className="inline-flex items-center gap-2 px-6 py-2.5 bg-[#111111] text-[#D9FF43] font-black text-xs uppercase tracking-wider border-2 border-[#111111] brutal-shadow hover:bg-[#222222] active:translate-x-[1px] active:translate-y-[1px] transition-transform"
            >
              <Save size={15} />
              <span>{saving ? 'Saving...' : isEditing ? 'Update Opportunity' : 'Publish Opportunity'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
