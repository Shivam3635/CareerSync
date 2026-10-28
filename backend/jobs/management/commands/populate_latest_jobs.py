from datetime import date
from django.core.management.base import BaseCommand
from jobs.models import Job, JobEligibilityRule

LATEST_JOBS_DATA = [
    {
        "title": "SSC CGL Recruitment 2026 (Combined Graduate Level)",
        "organization": "Staff Selection Commission (SSC)",
        "advertisement_number": "HQ-PPII03(1)/2/2026-PP_II",
        "recruitment_year": 2026,
        "category": "General",
        "application_start_date": date(2026, 9, 15),
        "application_deadline": date(2026, 11, 28),
        "age_cutoff_date": date(2026, 8, 1),
        "min_age": 18,
        "max_age": 30,
        "total_vacancies": 17727,
        "application_fee_details": {"General/OBC/EWS": 100, "SC/ST/Female/ESM": 0},
        "vacancy_details": [
            {"post_name": "Assistant Section Officer (ASO - CSS / MEA / IB)", "vacancies": 2450, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Inspector (Central Excise & GST / Preventive Officer)", "vacancies": 3200, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Sub-Inspector (CBI / NIA)", "vacancies": 450, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Auditor & Accountant (CAG / CGA)", "vacancies": 4127, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Tax Assistant (CBDT / CBIC)", "vacancies": 7500, "qualification": "Bachelor's Degree + Typing proficiency"}
        ],
        "selection_process": "Tier-I (Computer Based Test), Tier-II (Computer Based Exam + Data Entry Speed Test), Document Verification",
        "original_url": "https://ssc.gov.in",
        "source_name": "Official SSC Portal",
        "source_type": "manual",
        "description": "Staff Selection Commission (SSC) prestigious Combined Graduate Level Examination (CGL 2026) for filling Group B and Group C Gazetted and Non-Gazetted vacancies across Central Ministries and Departments.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Bachelor's Degree in any discipline from a recognized University. Age cutoff date is 01-08-2026 with standard government category age relaxations."
        }
    },
    {
        "title": "SBI PO Recruitment 2026 (Probationary Officers)",
        "organization": "State Bank of India (SBI)",
        "advertisement_number": "CRPD/PO/2026-27/04",
        "recruitment_year": 2026,
        "category": "Banking",
        "application_start_date": date(2026, 9, 20),
        "application_deadline": date(2026, 11, 20),
        "age_cutoff_date": date(2026, 4, 1),
        "min_age": 21,
        "max_age": 30,
        "total_vacancies": 2000,
        "application_fee_details": {"General/EWS/OBC": 750, "SC/ST/PwBD": 0},
        "vacancy_details": [
            {"post_name": "Probationary Officer (General)", "vacancies": 810, "qualification": "Graduation in any discipline"},
            {"post_name": "Probationary Officer (OBC)", "vacancies": 540, "qualification": "Graduation in any discipline"},
            {"post_name": "Probationary Officer (SC)", "vacancies": 300, "qualification": "Graduation in any discipline"},
            {"post_name": "Probationary Officer (ST)", "vacancies": 150, "qualification": "Graduation in any discipline"},
            {"post_name": "Probationary Officer (EWS)", "vacancies": 200, "qualification": "Graduation in any discipline"}
        ],
        "selection_process": "Phase-I Preliminary Exam (Objective), Phase-II Main Exam (Objective + Descriptive), Phase-III Psychometric Test, Group Exercise & Interview",
        "original_url": "https://sbi.co.in/careers",
        "source_name": "SBI Careers Portal",
        "source_type": "manual",
        "description": "State Bank of India recruitment for Probationary Officers (PO) across branches in India. Candidates in their final year of graduation are also eligible to apply provisionally.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "appearing_allowed",
            "additional_certification_requirement": "",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Graduation in any discipline. Final year / semester appearing candidates are permitted to apply subject to producing proof of graduation at interview."
        }
    },
    {
        "title": "UPSC Civil Services Examination (IAS/IPS/IFS) 2026",
        "organization": "Union Public Service Commission (UPSC)",
        "advertisement_number": "05/2026-CSP",
        "recruitment_year": 2026,
        "category": "Civil Services",
        "application_start_date": date(2026, 9, 1),
        "application_deadline": date(2026, 12, 5),
        "age_cutoff_date": date(2026, 8, 1),
        "min_age": 21,
        "max_age": 32,
        "total_vacancies": 1056,
        "application_fee_details": {"General/OBC/EWS Male": 100, "Female/SC/ST/PwBD": 0},
        "vacancy_details": [
            {"post_name": "Indian Administrative Service (IAS)", "vacancies": 180, "qualification": "Any Graduate Degree"},
            {"post_name": "Indian Police Service (IPS)", "vacancies": 200, "qualification": "Any Graduate Degree"},
            {"post_name": "Indian Foreign Service (IFS)", "vacancies": 55, "qualification": "Any Graduate Degree"},
            {"post_name": "Central Services Group A (IRS, IA&AS, etc.)", "vacancies": 621, "qualification": "Any Graduate Degree"}
        ],
        "selection_process": "Civil Services Preliminary Examination (CSAT + GS), Civil Services Main Examination (Written 9 Papers), Personality Test / Interview",
        "original_url": "https://upsc.gov.in",
        "source_name": "Official UPSC Portal",
        "source_type": "manual",
        "description": "Union Public Service Commission (UPSC) premier Civil Services Examination 2026 for recruitment to the Indian Administrative Service, Indian Police Service, Indian Foreign Service, and Group A/B Central Services.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "appearing_allowed",
            "additional_certification_requirement": "",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Bachelor's degree from recognized university. Age limit 21 to 32 years as of 1st August 2026. General: 6 attempts, OBC: 9 attempts, SC/ST: unlimited attempts."
        }
    },
    {
        "title": "SSC GD Constable Recruitment 2026 (CAPFs & SSF)",
        "organization": "Staff Selection Commission / Ministry of Home Affairs",
        "advertisement_number": "F.No. 3/1/2026-P&P-I",
        "recruitment_year": 2026,
        "category": "Defense",
        "application_start_date": date(2026, 9, 5),
        "application_deadline": date(2026, 11, 30),
        "age_cutoff_date": date(2026, 1, 1),
        "min_age": 18,
        "max_age": 23,
        "total_vacancies": 39481,
        "application_fee_details": {"General/OBC/EWS Male": 100, "Women/SC/ST/Ex-Servicemen": 0},
        "vacancy_details": [
            {"post_name": "Constable GD in BSF", "vacancies": 15654, "qualification": "10th Class (Matriculation)"},
            {"post_name": "Constable GD in CISF", "vacancies": 7145, "qualification": "10th Class (Matriculation)"},
            {"post_name": "Constable GD in CRPF", "vacancies": 11541, "qualification": "10th Class (Matriculation)"},
            {"post_name": "Constable GD in SSB & ITBP", "vacancies": 4141, "qualification": "10th Class (Matriculation)"},
            {"post_name": "Rifleman GD in Assam Rifles & SSF", "vacancies": 1000, "qualification": "10th Class (Matriculation)"}
        ],
        "selection_process": "Computer Based Examination (CBE in 13 regional languages), Physical Standard Test (PST), Physical Efficiency Test (PET), Medical Examination & Document Verification",
        "original_url": "https://ssc.gov.in",
        "source_name": "SSC Official Website",
        "source_type": "manual",
        "description": "Recruitment of Constables (General Duty) in Central Armed Police Forces (CAPFs), SSF, and Rifleman (GD) in Assam Rifles Examination 2026. Huge opportunity for 10th pass youth.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "10th",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Candidate must have passed Matriculation or 10th Class Examination from a recognized Board/University. Must fulfill physical measurement standards."
        }
    },
    {
        "title": "SSC CHSL (10+2) Recruitment 2026 (LDC / JSA / DEO)",
        "organization": "Staff Selection Commission (SSC)",
        "advertisement_number": "F.No. 3/2/2026-P&P-II",
        "recruitment_year": 2026,
        "category": "General",
        "application_start_date": date(2026, 9, 25),
        "application_deadline": date(2026, 12, 15),
        "age_cutoff_date": date(2026, 8, 1),
        "min_age": 18,
        "max_age": 27,
        "total_vacancies": 3712,
        "application_fee_details": {"General/OBC": 100, "SC/ST/Women": 0},
        "vacancy_details": [
            {"post_name": "Lower Division Clerk (LDC) / Junior Secretariat Assistant (JSA)", "vacancies": 2980, "qualification": "12th Standard or equivalent"},
            {"post_name": "Data Entry Operator (DEO / DEO Grade A)", "vacancies": 732, "qualification": "12th Standard pass in Science stream with Mathematics"}
        ],
        "selection_process": "Tier-I (Computer Based Objective Test), Tier-II (Objective Exam + Typing Test / Skill Test)",
        "original_url": "https://ssc.gov.in",
        "source_name": "SSC Examination Portal",
        "source_type": "manual",
        "description": "Staff Selection Commission Combined Higher Secondary (10+2) Level Examination 2026 for recruitment to Lower Division Clerk, Junior Secretariat Assistant, and Data Entry Operator positions in various Central Ministries.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "12th",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "Computer typing proficiency (English: 35 wpm / Hindi: 30 wpm)",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Candidates must have passed 12th Standard or equivalent exam from a recognized Board or University. Data Entry Operator posts require Science stream with Mathematics."
        }
    },
    {
        "title": "UPPSC Combined State / Upper Subordinate Services (PCS) 2026",
        "organization": "Uttar Pradesh Public Service Commission (UPPSC)",
        "advertisement_number": "A-1/E-1/2026",
        "recruitment_year": 2026,
        "category": "Civil Services",
        "application_start_date": date(2026, 9, 10),
        "application_deadline": date(2026, 11, 25),
        "age_cutoff_date": date(2026, 7, 1),
        "min_age": 21,
        "max_age": 40,
        "total_vacancies": 220,
        "application_fee_details": {"UR/EWS/OBC": 125, "SC/ST": 65, "PwBD": 25},
        "vacancy_details": [
            {"post_name": "Deputy Collector (SDM)", "vacancies": 42, "qualification": "Graduate Degree in any discipline"},
            {"post_name": "Deputy Superintendent of Police (DSP)", "vacancies": 38, "qualification": "Graduate Degree in any discipline + Physical standard"},
            {"post_name": "Block Development Officer (BDO)", "vacancies": 50, "qualification": "Graduate Degree in any discipline"},
            {"post_name": "Assistant Regional Transport Officer (ARTO)", "vacancies": 20, "qualification": "Graduate Degree in any discipline"},
            {"post_name": "District Treasury Officer & Commercial Tax Officer", "vacancies": 70, "qualification": "Graduate in Commerce / Economics / Any stream"}
        ],
        "selection_process": "Preliminary Examination (General Studies I & II / CSAT), Main Written Examination (8 Descriptive Papers including UP Special GS), Interview / Viva-Voce",
        "original_url": "https://uppsc.up.nic.in",
        "source_name": "UPPSC Official Portal",
        "source_type": "manual",
        "description": "Uttar Pradesh Public Service Commission Combined State / Upper Subordinate Services Examination (PCS 2026) for state civil and executive posts in UP.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "",
            "age_relaxations": {"OBC": 5, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Bachelor's Degree in any discipline from a recognized University. Age between 21 and 40 years as of 01-07-2026. Age relaxation of 5 years applicable to SC, ST, and OBC of UP domicile."
        }
    },
    {
        "title": "IBPS Clerk XIV Recruitment 2026 (Customer Service Associate)",
        "organization": "Institute of Banking Personnel Selection (IBPS)",
        "advertisement_number": "CRP-CLERKS-XIV/2026-27",
        "recruitment_year": 2026,
        "category": "Banking",
        "application_start_date": date(2026, 9, 12),
        "application_deadline": date(2026, 11, 18),
        "age_cutoff_date": date(2026, 7, 1),
        "min_age": 20,
        "max_age": 28,
        "total_vacancies": 6128,
        "application_fee_details": {"General/EWS/OBC": 850, "SC/ST/PwBD/ESM": 175},
        "vacancy_details": [
            {"post_name": "Customer Service Associate / Clerk in Punjab National Bank", "vacancies": 1800, "qualification": "Graduation degree"},
            {"post_name": "Customer Service Associate / Clerk in Bank of Baroda", "vacancies": 1200, "qualification": "Graduation degree"},
            {"post_name": "Customer Service Associate / Clerk in Canara Bank", "vacancies": 1400, "qualification": "Graduation degree"},
            {"post_name": "Customer Service Associate / Clerk in Union Bank of India", "vacancies": 1728, "qualification": "Graduation degree"}
        ],
        "selection_process": "Online Preliminary Examination (English, Numerical Ability, Reasoning), Online Main Examination (General/Financial Awareness, English, Quantitative Aptitude, Reasoning & Computer Aptitude)",
        "original_url": "https://ibps.in",
        "source_name": "IBPS Official Recruitment",
        "source_type": "manual",
        "description": "Common Recruitment Process for Selection of Clerical Cadre Personnel in 11 Participating Public Sector Banks across India.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "Certificate / Diploma / Degree in Computer Operations or studied Computer / IT in High School",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "A Degree (Graduation) in any discipline from a University recognized by the Govt. Of India. Operating and working knowledge in computer systems is mandatory."
        }
    },
    {
        "title": "RRB Assistant Loco Pilot (ALP) Recruitment 2026",
        "organization": "Railway Recruitment Board (RRB)",
        "advertisement_number": "CEN 01/2026",
        "recruitment_year": 2026,
        "category": "Railways",
        "application_start_date": date(2026, 9, 1),
        "application_deadline": date(2026, 12, 10),
        "age_cutoff_date": date(2026, 7, 1),
        "min_age": 18,
        "max_age": 33,
        "total_vacancies": 18799,
        "application_fee_details": {"General/OBC": 500, "SC/ST/Female/Ex-Servicemen": 250},
        "vacancy_details": [
            {"post_name": "Assistant Loco Pilot (Northern Railway)", "vacancies": 3200, "qualification": "Matriculation + ITI / Diploma"},
            {"post_name": "Assistant Loco Pilot (Western Railway)", "vacancies": 2850, "qualification": "Matriculation + ITI / Diploma"},
            {"post_name": "Assistant Loco Pilot (Central Railway)", "vacancies": 3100, "qualification": "Matriculation + ITI / Diploma"},
            {"post_name": "Assistant Loco Pilot (Eastern & South Eastern Railway)", "vacancies": 5600, "qualification": "Matriculation + ITI / Diploma"},
            {"post_name": "Assistant Loco Pilot (Southern Railway & SCR)", "vacancies": 4049, "qualification": "Matriculation + ITI / Diploma"}
        ],
        "selection_process": "First Stage CBT (CBT-1), Second Stage CBT (CBT-2 Part A & Part B), Computer Based Aptitude Test (CBAT), Document Verification & Medical Examination (A-1 Standard)",
        "original_url": "https://indianrailways.gov.in",
        "source_name": "Ministry of Railways",
        "source_type": "manual",
        "description": "Railway Recruitment Board (RRB) Centralized Employment Notice for recruitment of Assistant Loco Pilot (ALP) across all Zonal Railways.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "10th",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "ITI Trade Certificate (NCVT/SCVT) or 3-Year Polytechnic Diploma in Mechanical/Electrical/Electronics/Automobile Engineering",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Matriculation / 10th Standard plus ITI in recognized trades OR 3 Years Diploma in Engineering or B.E./B.Tech degree in engineering disciplines."
        }
    },
    {
        "title": "ISRO Scientist / Engineer 'SC' Recruitment 2026",
        "organization": "Indian Space Research Organisation (ISRO)",
        "advertisement_number": "ISRO:ICRB:02(EMC):2026",
        "recruitment_year": 2026,
        "category": "Engineering & Tech",
        "application_start_date": date(2026, 9, 20),
        "application_deadline": date(2026, 12, 1),
        "age_cutoff_date": date(2026, 5, 25),
        "min_age": 18,
        "max_age": 28,
        "total_vacancies": 303,
        "application_fee_details": {"General/OBC/EWS Male": 250, "All Women/SC/ST/PwBD/Ex-Servicemen": 0},
        "vacancy_details": [
            {"post_name": "Scientist/Engineer 'SC' (Computer Science)", "vacancies": 85, "qualification": "B.E/B.Tech in CS with minimum 65% marks or 6.84 CGPA"},
            {"post_name": "Scientist/Engineer 'SC' (Electronics & Communication)", "vacancies": 120, "qualification": "B.E/B.Tech in ECE with minimum 65% marks or 6.84 CGPA"},
            {"post_name": "Scientist/Engineer 'SC' (Mechanical)", "vacancies": 98, "qualification": "B.E/B.Tech in Mechanical with minimum 65% marks or 6.84 CGPA"}
        ],
        "selection_process": "Written Test (Discipline Specific + Aptitude), Comprehensive Technical Interview at ISRO Headquarters Bangalore",
        "original_url": "https://isro.gov.in/careers",
        "source_name": "ISRO Centralised Recruitment Board (ICRB)",
        "source_type": "manual",
        "description": "Indian Space Research Organisation (ISRO) Centralised Recruitment Board invites applications for the prestigious post of Scientist/Engineer 'SC' in Level 10 of Pay Matrix.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "B.E / B.Tech or equivalent degree in First Class with aggregate minimum 65% marks or 6.84 CGPA",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": 65.00,
            "conditions_summary": "First class B.E/B.Tech with minimum 65% marks (average of all semesters) or 6.84/10 CGPA. Maximum age 28 years with OBC/SC/ST relaxation."
        }
    },
    {
        "title": "Delhi Police & CAPFs Sub-Inspector (SI) via SSC CPO 2026",
        "organization": "Staff Selection Commission (SSC) / Delhi Police",
        "advertisement_number": "F.No. 3/1/2026-CPO-SI",
        "recruitment_year": 2026,
        "category": "Police & Security",
        "application_start_date": date(2026, 9, 8),
        "application_deadline": date(2026, 11, 22),
        "age_cutoff_date": date(2026, 8, 1),
        "min_age": 20,
        "max_age": 25,
        "total_vacancies": 4187,
        "application_fee_details": {"General/OBC/EWS Male": 100, "Women/SC/ST/Ex-Servicemen": 0},
        "vacancy_details": [
            {"post_name": "Sub-Inspector (Executive) in Delhi Police - Male", "vacancies": 125, "qualification": "Bachelor's Degree + Driving License (LMV)"},
            {"post_name": "Sub-Inspector (Executive) in Delhi Police - Female", "vacancies": 61, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Sub-Inspector (GD) in CISF", "vacancies": 1597, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Sub-Inspector (GD) in BSF", "vacancies": 892, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Sub-Inspector (GD) in CRPF", "vacancies": 1172, "qualification": "Bachelor's Degree in any discipline"},
            {"post_name": "Sub-Inspector (GD) in ITBP & SSB", "vacancies": 340, "qualification": "Bachelor's Degree in any discipline"}
        ],
        "selection_process": "Paper-I (General Intelligence, Reasoning, GK, Quant, English), Physical Standard Test (PST) & Physical Endurance Test (PET), Paper-II (English Language & Comprehension), Detailed Medical Exam (DME)",
        "original_url": "https://ssc.gov.in",
        "source_name": "SSC Official Website",
        "source_type": "manual",
        "description": "Recruitment of Sub-Inspectors in Delhi Police and Central Armed Police Forces (CAPFs - BSF, CISF, CRPF, ITBP, SSB) Examination 2026.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "completed_only",
            "additional_certification_requirement": "Valid Driving License for LMV (Motorcycle and Car) for Male candidates applying for Delhi Police SI",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": None,
            "conditions_summary": "Bachelor's degree from a recognized university or equivalent. Male candidates for Delhi Police SI must possess a valid driving license for LMV."
        }
    },
    {
        "title": "UGC NET December 2026 (Assistant Professor & JRF)",
        "organization": "National Testing Agency (NTA) / UGC",
        "advertisement_number": "NTA/UGC-NET/DEC-2026",
        "recruitment_year": 2026,
        "category": "Teaching",
        "application_start_date": date(2026, 9, 28),
        "application_deadline": date(2026, 11, 30),
        "age_cutoff_date": date(2026, 12, 1),
        "min_age": 21,
        "max_age": 30,
        "total_vacancies": 5000,
        "application_fee_details": {"General/Unreserved": 1150, "Gen-EWS/OBC-NCL": 600, "SC/ST/PwD/Third Gender": 325},
        "vacancy_details": [
            {"post_name": "Junior Research Fellowship (JRF) & Assistant Professor", "vacancies": 1200, "qualification": "Master's Degree with minimum 55% marks"},
            {"post_name": "Eligibility for Assistant Professor (All Subjects)", "vacancies": 3800, "qualification": "Master's Degree with minimum 55% marks"}
        ],
        "selection_process": "Computer Based Test (CBT) consisting of two papers: Paper-I (Teaching & Research Aptitude) and Paper-II (Subject specific)",
        "original_url": "https://ugcnet.nta.ac.in",
        "source_name": "National Testing Agency",
        "source_type": "manual",
        "description": "University Grants Commission National Eligibility Test (UGC-NET) December 2026 cycle for determining the eligibility of Indian nationals for 'Assistant Professor' as well as 'Junior Research Fellowship and Assistant Professor' in Indian universities and colleges.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Post Graduate",
            "allowed_status": "appearing_allowed",
            "additional_certification_requirement": "",
            "age_relaxations": {"OBC": 3, "SC": 5, "ST": 5, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": 55.00,
            "conditions_summary": "Master's Degree or equivalent with at least 55% marks (50% for OBC-NCL/SC/ST/PwD). Candidates awaiting final year Master's results are eligible to apply."
        }
    },
    {
        "title": "Indian Air Force AFCAT 01/2026 (Flying & Ground Duty)",
        "organization": "Indian Air Force (IAF)",
        "advertisement_number": "AFCAT 01/2026/NCC",
        "recruitment_year": 2026,
        "category": "Defense",
        "application_start_date": date(2026, 9, 30),
        "application_deadline": date(2026, 12, 30),
        "age_cutoff_date": date(2027, 1, 1),
        "min_age": 20,
        "max_age": 26,
        "total_vacancies": 317,
        "application_fee_details": {"All Candidates": 550, "NCC Special Entry": 0},
        "vacancy_details": [
            {"post_name": "Flying Branch (Men & Women)", "vacancies": 38, "qualification": "Graduate with min 60% in Maths & Physics at 10+2 level or B.E./B.Tech (Age 20-24)"},
            {"post_name": "Ground Duty (Technical - Aeronautical Engineering)", "vacancies": 165, "qualification": "B.E/B.Tech with minimum 60% marks in relevant branches"},
            {"post_name": "Ground Duty (Non-Technical - Administration & Logistics)", "vacancies": 114, "qualification": "Graduate Degree in any discipline with minimum 60% marks"}
        ],
        "selection_process": "AFCAT Online Written Examination, Air Force Selection Board (AFSB) 5-Day Interview & Testing, Medical Examination",
        "original_url": "https://afcat.cdac.in",
        "source_name": "Indian Air Force CDAC",
        "source_type": "manual",
        "description": "Air Force Common Admission Test (AFCAT 01/2026) for grant of Short Service Commission (SSC) in Flying Branch and Ground Duty (Technical and Non-Technical) Branches.",
        "status": "approved",
        "is_published": True,
        "rule": {
            "min_qualification_level": "Graduate",
            "allowed_status": "appearing_allowed",
            "additional_certification_requirement": "Minimum 50% in Maths and Physics at 10+2 level and minimum 60% aggregate in Graduation or B.Tech",
            "age_relaxations": {"OBC": 0, "SC": 0, "ST": 0, "EWS": 0, "GEN": 0},
            "domicile_requirement": "All India",
            "min_percentage": 60.00,
            "conditions_summary": "Flying branch: 20 to 24 years. Ground Duty: 20 to 26 years. Minimum 60% marks in graduation required. Candidates in final year with no backlogs allowed."
        }
    }
]


class Command(BaseCommand):
    help = "Populates latest verified 2026 Government recruitment job listings with deterministic eligibility rules."

    def handle(self, *args, **options):
        self.stdout.write("Populating latest 2026 Government recruitment opportunities...")
        created_count = 0
        updated_count = 0

        for item in LATEST_JOBS_DATA:
            rule_data = item.pop("rule")
            advt_no = item.get("advertisement_number", "")
            title = item.get("title")
            org = item.get("organization")

            job, created = Job.objects.update_or_create(
                title=title,
                organization=org,
                defaults=item
            )

            JobEligibilityRule.objects.update_or_create(
                job=job,
                defaults=rule_data
            )

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"+ Created: {title} ({org})"))
            else:
                updated_count += 1
                self.stdout.write(self.style.WARNING(f"= Updated: {title} ({org})"))

        self.stdout.write(self.style.SUCCESS(
            f"Successfully populated latest jobs! Created: {created_count}, Updated: {updated_count}. Total jobs in DB: {Job.objects.count()}"
        ))
