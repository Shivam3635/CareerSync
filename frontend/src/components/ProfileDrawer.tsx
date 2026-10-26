import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import type { Category, QualificationLevel, QualificationStatus } from '../types';
import { X, Check, Save } from 'lucide-react';

interface ProfileDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onProfileUpdated: () => void;
}

export const ProfileDrawer: React.FC<ProfileDrawerProps> = ({
  isOpen,
  onClose,
  onProfileUpdated,
}) => {
  const { user, updateProfile } = useAuth();
  const profile = user?.student_profile;

  const [dob, setDob] = useState(profile?.date_of_birth || '1999-06-15');
  const [category, setCategory] = useState<Category>(profile?.category || 'OBC');
  const [domicile, setDomicile] = useState(profile?.domicile_state || 'Uttar Pradesh');
  const [qualification, setQualification] = useState<QualificationLevel>(
    (profile?.qualifications?.[profile.qualifications.length - 1]?.level as QualificationLevel) || 'Graduate'
  );
  const [qualStatus, setQualStatus] = useState<QualificationStatus>(
    profile?.qualifications?.[profile.qualifications.length - 1]?.status || 'completed'
  );
  const [degree, setDegree] = useState(
    profile?.qualifications?.[profile.qualifications.length - 1]?.degree || 'B.Tech in Computer Science'
  );
  const [additionalCertifications, setAdditionalCertifications] = useState(
    profile?.additional_certifications || ''
  );
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [errorMsg, setErrorMsg] = useState('');

  useEffect(() => {
    if (profile) {
      if (profile.date_of_birth) setDob(profile.date_of_birth);
      if (profile.category) setCategory(profile.category);
      if (profile.domicile_state) setDomicile(profile.domicile_state);
      if (profile.additional_certifications !== undefined) {
        setAdditionalCertifications(profile.additional_certifications || '');
      }
      if (profile.qualifications && profile.qualifications.length > 0) {
        const topQual = profile.qualifications[profile.qualifications.length - 1];
        setQualification(topQual.level);
        setQualStatus(topQual.status);
        if (topQual.degree) setDegree(topQual.degree);
      }
    }
  }, [profile]);

  if (!isOpen) return null;

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setErrorMsg('');
    setSaveSuccess(false);

    try {
      await updateProfile({
        date_of_birth: dob,
        category,
        domicile_state: domicile,
        additional_certifications: additionalCertifications.trim(),
        qualifications: [
          {
            level: qualification,
            degree,
            status: qualStatus,
          },
        ],
      });
      setSaveSuccess(true);
      onProfileUpdated();
      setTimeout(() => {
        setSaveSuccess(false);
        onClose();
      }, 1000);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-[#111111]/70 backdrop-blur-xs">
      <div className="w-full max-w-lg bg-[#F5F0E8] border-3 border-[#111111] brutal-shadow-lg p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between border-b-2 border-[#111111] pb-3 mb-4">
          <div>
            <h3 className="font-heading font-black text-xl text-[#111111]">
              Eligibility Profile
            </h3>
            <p className="text-xs text-[#555555]">
              Adjust your criteria to see real-time eligibility recalculations.
            </p>
          </div>
          <button
            onClick={onClose}
            className="p-1 border-2 border-[#111111] bg-white hover:bg-[#FF6B4A] hover:text-white brutal-shadow-sm transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        {errorMsg && (
          <div className="mb-4 p-2.5 bg-[#FFF0ED] border-2 border-[#111111] text-xs font-bold text-[#D12E00]">
            {errorMsg}
          </div>
        )}

        {saveSuccess && (
          <div className="mb-4 p-2.5 bg-[#D9FF43] border-2 border-[#111111] text-xs font-bold text-[#111111] flex items-center gap-1.5">
            <Check size={16} />
            Profile updated! Re-evaluating opportunities...
          </div>
        )}

        <form onSubmit={handleSave} className="space-y-4 text-xs font-bold text-[#111111]">
          {/* Date of Birth */}
          <div>
            <label className="block uppercase tracking-wider mb-1">
              Date of Birth <span className="text-[#FF6B4A]">*</span>
            </label>
            <input
              type="date"
              value={dob}
              onChange={(e) => setDob(e.target.value)}
              required
              className="w-full p-2 bg-white border-2 border-[#111111] font-mono text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
            />
            <span className="text-[10px] text-[#666666] font-normal block mt-0.5">
              Used strictly against notification age cutoff dates (handles leap years & exact birth dates).
            </span>
          </div>

          {/* Category */}
          <div>
            <label className="block uppercase tracking-wider mb-1">
              Reservation Category <span className="text-[#FF6B4A]">*</span>
            </label>
            <select
              value={category}
              onChange={(e) => setCategory(e.target.value as Category)}
              className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
            >
              <option value="GEN">General (Unreserved - UR)</option>
              <option value="OBC">Other Backward Classes (OBC - Non-Creamy Layer)</option>
              <option value="SC">Scheduled Castes (SC)</option>
              <option value="ST">Scheduled Tribes (ST)</option>
              <option value="EWS">Economically Weaker Section (EWS)</option>
            </select>
          </div>

          {/* Domicile State */}
          <div>
            <label className="block uppercase tracking-wider mb-1">
              State of Domicile <span className="text-[#FF6B4A]">*</span>
            </label>
            <input
              type="text"
              value={domicile}
              onChange={(e) => setDomicile(e.target.value)}
              placeholder="e.g. Uttar Pradesh, Delhi, Bihar, Maharashtra"
              required
              className="w-full p-2 bg-white border-2 border-[#111111] font-semibold text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
            />
          </div>

          {/* Highest Qualification */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block uppercase tracking-wider mb-1">
                Highest Qualification <span className="text-[#FF6B4A]">*</span>
              </label>
              <select
                value={qualification}
                onChange={(e) => setQualification(e.target.value as QualificationLevel)}
                className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
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
                Completion Status <span className="text-[#FF6B4A]">*</span>
              </label>
              <select
                value={qualStatus}
                onChange={(e) => setQualStatus(e.target.value as QualificationStatus)}
                className="w-full p-2 bg-white border-2 border-[#111111] font-bold text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
              >
                <option value="completed">Completed Degree</option>
                <option value="appearing">Final Year / Appearing</option>
              </select>
            </div>
          </div>

          {/* Degree title / specialization */}
          <div>
            <label className="block uppercase tracking-wider mb-1">
              Degree / Specialization
            </label>
            <input
              type="text"
              value={degree}
              onChange={(e) => setDegree(e.target.value)}
              placeholder="e.g. B.Tech Computer Science, B.Sc Mathematics"
              className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
            />
          </div>

          {/* Additional Certifications / Diplomas */}
          <div>
            <label className="block uppercase tracking-wider mb-1">
              Additional Certifications / Diplomas
            </label>
            <input
              type="text"
              value={additionalCertifications}
              onChange={(e) => setAdditionalCertifications(e.target.value)}
              placeholder="e.g. 3-Year Polytechnic Diploma in Mechanical, ITI Fitter, CCC Computer, B.Ed"
              className="w-full p-2 bg-white border-2 border-[#111111] text-sm brutal-shadow-sm focus:outline-none focus:bg-[#FFFDE6]"
            />
            <span className="text-[10px] text-[#666666] font-normal block mt-0.5">
              Specify any technical Polytechnic diplomas, ITI certificates, computer literacy (CCC/O-Level), or teaching credentials.
            </span>
          </div>

          {/* Action buttons */}
          <div className="pt-3 border-t-2 border-[#111111] flex items-center justify-between">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-xs font-bold uppercase bg-white border-2 border-[#111111] hover:bg-[#E8E2D8]"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSaving}
              className="inline-flex items-center gap-1.5 px-5 py-2 text-xs font-black uppercase tracking-wider bg-[#D9FF43] text-[#111111] border-2 border-[#111111] brutal-shadow-sm hover:translate-x-[-1px] hover:translate-y-[-1px] active:translate-x-[1px] active:translate-y-[1px]"
            >
              <Save size={14} />
              <span>{isSaving ? 'Saving...' : 'Save & Recalculate'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
