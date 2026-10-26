# CareerSync — Government Jobs. Matched to You.

CareerSync is a minimalist, personalized government recruitment eligibility discovery platform for Indian government exam aspirants.

It acts as an eligibility filter that evaluates an aspirant's profile (date of birth, category, qualification level, completion status, domicile) against recruitment criteria and redirects them to the official notification URL.

---

## 🎨 Visual Identity: Neo-Brutalism
- **Palette**: `#F5F0E8` (Canvas), `#111111` (Ink), `#D9FF43` (Electric Lime Accent), `#FF6B4A` (Coral Accent)
- **Typography**: Space Grotesk & Plus Jakarta Sans
- **Elements**: Bold 2px/3px black borders, solid drop shadows (`4px 4px 0px #111111`), tactile hover/active transitions

---

## 🤖 AI-Assisted Job Creation Feature (New)

The admin panel now includes an **"Add Job (URL / PDF / Manual)"** workflow designed to eliminate manual data entry while enforcing strict human-in-the-loop validation:

### 1. Three Input Pathways
1. 🌐 **Portal / Sarkari URL**:
   - Fetches and sanitizes HTML content.
   - **SSRF Defense Guard**: Blocks localhost, loopback, RFC 1918 private subnets, cloud metadata (`169.254.169.254`), and non-HTTP schemes. Validates DNS and redirects on every hop.
   - **Content-Type Filter**: Automatically classifies page types and rejects Admit Cards, Exam Dates, Answer Keys, and Exam Results.
2. 📄 **Official Notification PDF**:
   - Validates file type and magic bytes (`%PDF-`), enforces a 15 MB size limit.
   - Extracts page-by-page text via `pypdf` with OCR fallback for scanned gazettes.
   - Securely stores the source PDF in `/media/notifications_pdfs/` linked to the draft.
3. ✏️ **Manual Entry**:
   - Directly opens the pre-structured recruitment form.

### 2. AI Structuring & Conflict Detection
- **Gemini 2.5 Flash API** or intelligent deterministic regex fallback engine.
- Normalizes all dates to `YYYY-MM-DD` and ages/vacancies to integers.
- **Conflict Highlighting**: Detects contradictions in the source (e.g. min age > max age, conflicting last dates) and displays alert banners.
- **Missing Field Indicators**: Flags missing critical fields (such as application deadline or cutoff date).

### 3. Human-In-The-Loop Approval Workflow
- Every AI-generated draft starts in **`pending_review`** with **`is_published=False`**.
- **Aspirant Visibility Isolation**: Unapproved drafts are strictly hidden from candidate searches, discovery feeds, and public endpoints.
- **Admin Review Modal**: Pre-filled review screen showing confidence score, source URL / PDF link, conflicts, warnings, and editable fields.
- **Actions**:
  - `Save Draft`: Keeps the draft unlisted for further editing.
  - `Reject`: Marks draft as rejected.
  - `Approve & Publish`: Explicitly publishes the opportunity and dispatches notifications to eligible candidates.

---

## ⚡ Quick Start

### 1. Backend Setup (Django + DRF)

```bash
cd backend

# 1. Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Apply database migrations
python manage.py migrate

# 4. Seed demo accounts & sample jobs
python manage.py seed_data

# 5. Run the backend server
python manage.py runserver 127.0.0.1:8000
```

### 2. Frontend Setup (React + Vite + Tailwind CSS)

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Start Vite development server
npm run dev
```

Visit **`http://127.0.0.1:5173/`** in your browser.

---

## 🔑 Demo Accounts (Seeded)

| Account | Email | Password | Role | Profile Summary |
|---|---|---|---|---|
| **Student Demo** | `student@careersync.demo` | `password123` | Student | Born: 15-Jun-1999, Category: OBC, Domicile: UP, Qualification: Graduate (B.Tech CS) |
| **Admin Demo** | `admin@careersync.demo` | `admin123` | Admin / Staff | Full access to the Custom Admin Portal (`/admin`) to extract, review, approve, and manage notifications |

*Note: On the `/auth` page, 1-click demo buttons allow instant login.*

---

## ⚙️ Environment Variables (`.env`)

```ini
# Django Backend Configuration
DJANGO_SECRET_KEY=careersync-production-secret-key-change-this
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# AI-Assisted Job Posting (Optional)
# Set your Gemini API key to use Gemini 2.5 Flash for PDF & URL extraction.
# If omitted, CareerSync automatically uses its robust deterministic rules engine.
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## 🧠 Eligibility Engine Logic

The engine (`backend/jobs/services/eligibility.py`) evaluates candidates with transparent explainability:

1. **Age at Cutoff**: Calculated on the official `age_cutoff_date` (never today's date), handling leap years and birthdays correctly.
2. **Category Relaxation**: Automatically looks up relaxation from the job's rules (e.g. OBC: +3 years, SC/ST: +5 years).
3. **Education Matching**: Compares qualification rank against requirement (`10th` < `12th` < `Diploma` < `Graduate` < `Post Graduate` < `Doctorate`).
4. **Appearing Status**: Verifies whether final year candidates are allowed.
5. **State Domicile**: Checks state restriction requirements.
6. **Statuses**:
   - `eligible` (all mandatory criteria satisfied)
   - `review_required` (missing profile information)
   - `not_eligible` (age or qualification mismatch)

---

## 🧪 Running Automated Tests

```bash
cd backend
python manage.py test accounts jobs
```

All 30 unit tests pass, covering:
- SSRF prevention (localhost, private subnets, cloud metadata, unsupported schemes)
- URL extraction & non-recruitment page rejection (admit cards, results)
- PDF file validation & text parsing
- AI normalization, conflict detection, and missing field warnings
- Admin authorization enforcement
- Aspirant isolation (unapproved jobs strictly hidden)
- Admin review, approval, rejection, and alert notification dispatching
- Deterministic eligibility math (leap years, category relaxations, education hierarchy)
