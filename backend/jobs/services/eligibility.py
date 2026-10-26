"""
CareerSync Eligibility Engine
Deterministic, rule-based matching of candidate profiles against recruitment criteria.
"""

import re
from datetime import date
from typing import Dict, Any, List, Optional
from students.models import StudentProfile, StudentQualification
from jobs.models import Job, JobEligibilityRule


HIERARCHY = {
    '10th': 1,
    '12th': 2,
    'Graduate': 3,
    'Post Graduate': 4,
    'Doctorate': 5,
}


def calculate_age_at_cutoff(born: date, cutoff: date) -> int:
    """
    Accurately calculate age on cutoff date handling leap years and birthday calendar dates.
    """
    if born > cutoff:
        return 0
    return cutoff.year - born.year - ((cutoff.month, cutoff.day) < (born.month, born.day))


def check_certification_match(cert_req: str, candidate_certs: str, candidate_degrees: str) -> tuple[bool, str]:
    """
    Evaluates whether the student's recorded certifications or degree details
    satisfy the job's additional certification / diploma requirement.
    """
    combined_raw = f"{candidate_certs} {candidate_degrees}".strip()
    if not combined_raw:
        return False, "No technical certification or specialized trade/degree recorded in profile."

    def _normalize(t: str) -> str:
        s = t.lower()
        s = re.sub(r'\bb\.?\s*ed\b', 'bed', s)
        s = re.sub(r'\bd\.?\s*el\.?\s*ed\b', 'deled', s)
        s = re.sub(r'\bo\s*-\s*level\b', 'olevel', s)
        return s

    cand_norm = _normalize(combined_raw)

    stop_words = {
        'year', 'years', 'by', 'in', 'of', 'for', 'the', 'and', 'or', 'with', 'to', 'at',
        'any', 'recognized', 'relevant', 'discipline', 'trade', 'course', 'class', 'passed',
        'standard', 'minimum', 'candidate', 'candidates', 'must', 'have', 'certificate',
        'certificates', 'ed', 'level', 'skill', 'state', 'central', 'board', 'university'
    }

    # Split requirement by alternatives (comma, semicolon, or)
    clauses = re.split(r'[,;]|\b(?:or)\b', cert_req, flags=re.IGNORECASE)

    for clause in clauses:
        clause_str = clause.strip()
        if not clause_str:
            continue
        c_norm = _normalize(clause_str)
        if c_norm in cand_norm:
            return True, f"Satisfies requirement track: '{clause_str}'"

        tokens = [w for w in re.findall(r'\b[a-z0-9\+\#]{2,}\b', c_norm) if w not in stop_words]
        for tok in tokens:
            aliases = [tok]
            if tok == 'diploma':
                aliases.append('polytechnic')
            elif tok == 'polytechnic':
                aliases.append('diploma')
            elif tok == 'steno':
                aliases.append('stenography')
            elif tok == 'stenography':
                aliases.append('steno')

            for a in aliases:
                if re.search(rf'\b{re.escape(a)}\b', cand_norm):
                    return True, f"Confirmed credential ({tok.upper()} in {clause_str})"

    return False, f"Missing required credential '{cert_req}'. Profile recorded: '{combined_raw}'"


class EligibilityEvaluator:
    """
    Evaluates a StudentProfile against a specific Job and its JobEligibilityRule.
    Produces deterministic results with transparent reasoning and explainability.
    """

    def __init__(self, student: Optional[StudentProfile], job: Job):
        self.student = student
        self.job = job
        self.rule: Optional[JobEligibilityRule] = getattr(job, 'rule', None)

    def evaluate(self) -> Dict[str, Any]:
        reasons: List[str] = []
        warnings: List[str] = []
        failed_criteria: List[str] = []
        missing_info: List[str] = []
        
        # If no student profile is supplied (e.g., guest user viewing public list)
        if not self.student:
            return {
                'status': 'review_required',
                'reasons': ['Profile required to determine exact eligibility.'],
                'warnings': ['Sign in or register to calculate personal eligibility.'],
                'failed_criteria': [],
                'missing_info': ['Student profile not provided'],
                'details': {
                    'calculated_age': None,
                    'age_relaxation_applied': 0,
                    'effective_max_age': self.job.max_age,
                    'is_expired': self.job.is_expired,
                }
            }

        # 1. Check Application Expiry
        if self.job.is_expired:
            return {
                'status': 'not_eligible',
                'reasons': [f"Recruitment closed on {self.job.application_deadline.strftime('%d %b %Y')}."],
                'warnings': [],
                'failed_criteria': ['Application window has closed'],
                'missing_info': [],
                'details': {
                    'calculated_age': None,
                    'age_relaxation_applied': 0,
                    'effective_max_age': self.job.max_age,
                    'is_expired': True,
                }
            }

        # 2. Check Date of Birth & Age
        dob = self.student.date_of_birth
        cutoff_date = self.job.age_cutoff_date
        calculated_age = None
        relaxation = 0
        effective_max_age = self.job.max_age

        if not dob:
            missing_info.append('Date of Birth is missing from your profile.')
        else:
            calculated_age = calculate_age_at_cutoff(dob, cutoff_date)
            category = self.student.category

            # Age relaxation lookup from rule
            if self.rule and self.rule.age_relaxations:
                relaxation = self.rule.age_relaxations.get(category, 0)

            effective_max_age = self.job.max_age + relaxation

            if calculated_age < self.job.min_age:
                failed_criteria.append(
                    f"Age requirement not met: You will be {calculated_age} years old on {cutoff_date.strftime('%d-%m-%Y')} "
                    f"(Minimum required: {self.job.min_age} years)."
                )
            elif calculated_age > effective_max_age:
                failed_msg = (
                    f"Above age limit: You will be {calculated_age} years old on {cutoff_date.strftime('%d-%m-%Y')} "
                    f"(Maximum permitted for category {category}: {effective_max_age} years"
                )
                if relaxation > 0:
                    failed_msg += f", including {relaxation} years relaxation)."
                else:
                    failed_msg += ")."
                failed_criteria.append(failed_msg)
            else:
                success_msg = (
                    f"Age eligible: {calculated_age} years old as on cutoff ({cutoff_date.strftime('%d-%m-%Y')}). "
                    f"Permitted range: {self.job.min_age} - {effective_max_age} years"
                )
                if relaxation > 0:
                    success_msg += f" (includes +{relaxation} years {category} relaxation)."
                else:
                    success_msg += "."
                reasons.append(success_msg)

        # 3. Check Educational Qualification
        min_level_req = self.rule.min_qualification_level if self.rule else 'Graduate'
        allowed_status_req = self.rule.allowed_status if self.rule else 'completed_only'
        min_required_rank = HIERARCHY.get(min_level_req, 4)

        # Fetch candidate qualifications
        qualifications = list(self.student.qualifications.all())
        if not qualifications:
            missing_info.append('Educational qualifications are missing from your profile.')
        else:
            # Check highest matching qualification
            matching_quals = [
                q for q in qualifications
                if HIERARCHY.get(q.level, 0) >= min_required_rank
            ]

            if not matching_quals:
                failed_criteria.append(
                    f"Qualification mismatch: Requires minimum '{min_level_req}', but your highest recorded is "
                    f"'{self.student.highest_qualification.level if self.student.highest_qualification else 'None'}'."
                )
            else:
                # Check status requirement (completed vs appearing)
                if allowed_status_req == 'completed_only':
                    completed_quals = [q for q in matching_quals if q.status == 'completed']
                    if completed_quals:
                        best_qual = max(completed_quals, key=lambda q: HIERARCHY.get(q.level, 0))
                        reasons.append(
                            f"Education eligible: You hold '{best_qual.level}' (completed), "
                            f"satisfying the requirement of '{min_level_req}'."
                        )
                    else:
                        top_matching = max(matching_quals, key=lambda q: HIERARCHY.get(q.level, 0))
                        failed_criteria.append(
                            f"Requires completed '{min_level_req}'. Your '{top_matching.level}' is currently marked as 'Appearing/Final Year'."
                        )
                else:
                    # appearing is allowed
                    best_qual = max(matching_quals, key=lambda q: HIERARCHY.get(q.level, 0))
                    status_note = " (Final Year / Appearing permitted)" if best_qual.status == 'appearing' else ""
                    reasons.append(
                        f"Education eligible: You hold '{best_qual.level}' ({best_qual.status}){status_note}, "
                        f"satisfying the minimum requirement of '{min_level_req}'."
                    )

        # 4. Check Additional Certification / Diploma Requirement
        if self.rule and self.rule.additional_certification_requirement:
            cert_req = self.rule.additional_certification_requirement.strip()
            student_certs = (getattr(self.student, 'additional_certifications', '') or '').strip()
            student_degrees = " ".join([q.degree for q in qualifications if q.degree]).strip()

            is_matched, match_detail = check_certification_match(cert_req, student_certs, student_degrees)
            if is_matched:
                reasons.append(f"Additional certification confirmed: {cert_req}")
            else:
                failed_criteria.append(
                    f"Certification requirement not met: Requires '{cert_req}'. "
                    f"Your profile does not satisfy this required technical credential."
                )

        # 5. Check Domicile Requirement (if applicable)
        if self.rule and self.rule.domicile_requirement and self.rule.domicile_requirement != 'All India':
            req_domicile = self.rule.domicile_requirement.strip().lower()
            student_domicile = (self.student.domicile_state or '').strip().lower()
            if student_domicile != req_domicile and student_domicile != 'all india':
                failed_criteria.append(
                    f"State domicile requirement: Open to candidates with domicile of {self.rule.domicile_requirement}. "
                    f"Your domicile is recorded as '{self.student.domicile_state}'."
                )
            else:
                reasons.append(f"Domicile confirmed for {self.rule.domicile_requirement}.")

        # 6. Determine Overall Status
        if failed_criteria:
            status = 'not_eligible'
        elif missing_info:
            status = 'review_required'
            warnings.extend(missing_info)
        else:
            status = 'eligible'

        return {
            'status': status,
            'reasons': reasons,
            'warnings': warnings,
            'failed_criteria': failed_criteria,
            'missing_info': missing_info,
            'details': {
                'calculated_age': calculated_age,
                'age_relaxation_applied': relaxation,
                'effective_max_age': effective_max_age,
                'min_age': self.job.min_age,
                'min_qualification_required': min_level_req,
                'is_expired': False,
            }
        }


def evaluate_student_for_job(student: Optional[StudentProfile], job: Job) -> Dict[str, Any]:
    """Convenience helper to evaluate a student against a job."""
    evaluator = EligibilityEvaluator(student, job)
    return evaluator.evaluate()
