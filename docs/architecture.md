# CareerSync — Architecture & System Design

## 1. System Overview

CareerSync is a minimalist, personalized government recruitment eligibility discovery platform built for Indian government exam aspirants. It solves a core problem: helping candidates immediately identify exams they qualify for without manually parsing lengthy official PDF advertisements.

```
                          ┌────────────────────────┐
                          │   React + TypeScript   │
                          │   Vite + Tailwind CSS  │
                          │  Neo-Brutalist Design  │
                          └───────────┬────────────┘
                                      │ HTTP / JSON
                                      ▼
                          ┌────────────────────────┐
                          │  Django REST Framework │
                          │     Session Auth       │
                          └─────┬────────────┬─────┘
                                │            │
            ┌───────────────────▼──┐      ┌──▼──────────────────┐
            │  Eligibility Engine  │      │ Notification Engine │
            │  (Deterministic Math)│      │ (Email Dispatch)    │
            └───────────┬──────────┘      └──┬──────────────────┘
                        │                    │
                        └─────────┬──────────┘
                                  ▼
                         ┌─────────────────┐
                         │   PostgreSQL /  │
                         │     SQLite3     │
                         └─────────────────┘
```

---

## 2. Core Modules

### 2.1 Eligibility Engine (`jobs/services/eligibility.py`)
- **Deterministic Evaluation**: Implements transparent, explainable logic without black-box heuristics or arbitrary AI guesses.
- **Accurate Age Calculation**: Uses calendar subtraction on official recruitment `age_cutoff_date` rather than today's date, correctly accounting for leap years and exact birth dates.
- **Reservation & Relaxation**: Applies structured category relaxation rules (e.g., OBC: +3 years, SC/ST: +5 years, EWS: 0).
- **Educational Hierarchy**: Compares applicant qualifications against minimum required ranks (`10th` < `12th` < `Diploma` < `Graduate` < `Post Graduate` < `Doctorate`).
- **Appearing Status**: Validates whether candidates in final year/appearing status are eligible.
- **State Domicile Filtering**: Supports 'All India' or state-specific domicile requirements (e.g., UPPSC vs HSSC).

### 2.2 Notification Engine (`jobs/services/notification_service.py`)
- When administrators publish or update a recruitment notification, the engine automatically matches active student profiles.
- Deduplication: Unique database constraints (`student`, `job`, `notification_type`) prevent duplicate email alerts.

### 2.3 Neo-Brutalist Visual Design System
- High-contrast color palette:
  - Background: `#F5F0E8`
  - Text & Border: `#111111`
  - Primary Accent: `#D9FF43` (Electric Lime)
  - Secondary Accent: `#FF6B4A` (Coral)
  - Muted Surface: `#E8E2D8`
- Distinctive physical styling:
  - Solid borders: `2px solid #111111`
  - Hard drop shadows: `4px 4px 0px #111111`
  - Micro-animations: active press translate with reduced shadow.

---

## 3. Database Schema

1. **User (`accounts_user`)**:
   - `id`, `email`, `full_name`, `role` (`student` | `admin`), `is_staff`, `created_at`
2. **StudentProfile (`students_studentprofile`)**:
   - `user_id`, `date_of_birth`, `gender`, `category`, `domicile_state`
3. **StudentQualification (`students_studentqualification`)**:
   - `student_id`, `level`, `degree`, `status`, `passing_year`, `percentage`
4. **Job (`jobs_job`)**:
   - `title`, `organization`, `category`, `application_start_date`, `application_deadline`, `age_cutoff_date`, `min_age`, `max_age`, `original_url`, `source_name`, `description`, `is_published`
5. **JobEligibilityRule (`jobs_jobeligibilityrule`)**:
   - `job_id`, `min_qualification_level`, `allowed_status`, `age_relaxations`, `domicile_requirement`, `min_percentage`
6. **Notification (`notifications_notification`)**:
   - `student_id`, `job_id`, `notification_type`, `is_sent`, `is_read`, `sent_at`
