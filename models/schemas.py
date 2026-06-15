"""
Data validation schemas for Jaundice Recovery Tracker
"""

# Activity type choices for timeline events
ACTIVITY_TYPES = [
    ('diagnosis', 'Initial Diagnosis'),
    ('hospital_visit', 'Hospital Visit'),
    ('lab_test', 'Laboratory Test'),
    ('consultation', 'Follow-up Consultation'),
    ('ayurveda_visit', 'Ayurveda Treatment'),
    ('medication_purchase', 'Medication Purchase'),
    ('recovery_milestone', 'Recovery Milestone'),
]

# Report category choices
REPORT_CATEGORIES = [
    ('laboratory_report', 'Laboratory Reports'),
    ('prescription', 'Prescriptions'),
    ('consultation_notes', 'Consultation Notes'),
    ('ayurveda_records', 'Ayurveda Records'),
]

# Medication status choices
MEDICATION_STATUS = [
    ('active', 'Active'),
    ('completed', 'Completed'),
    ('discontinued', 'Discontinued'),
]

# Common lab test names for jaundice tracking
LAB_TEST_NAMES = [
    'Total Bilirubin',
    'Direct Bilirubin',
    'Indirect Bilirubin',
    'SGPT (ALT)',
    'SGOT (AST)',
    'Alkaline Phosphatase (ALP)',
    'GGT',
    'Total Protein',
    'Albumin',
    'Globulin',
    'Prothrombin Time',
    'Complete Blood Count (CBC)',
    'Hepatitis B Surface Antigen',
    'Hepatitis A IgM',
    'Hepatitis C Antibody',
    'Urine Routine',
    'Other',
]

# Lab result status choices
LAB_RESULT_STATUS = [
    ('normal', 'Normal'),
    ('high', 'High'),
    ('low', 'Low'),
    ('critical', 'Critical'),
]

# Activity type icons and colors for UI rendering
ACTIVITY_TYPE_CONFIG = {
    'diagnosis': {'icon': 'fa-stethoscope', 'color': '#E74C3C', 'bg': '#FDEDEC'},
    'hospital_visit': {'icon': 'fa-hospital', 'color': '#3498DB', 'bg': '#EBF5FB'},
    'lab_test': {'icon': 'fa-flask', 'color': '#9B59B6', 'bg': '#F4ECF7'},
    'consultation': {'icon': 'fa-user-md', 'color': '#1ABC9C', 'bg': '#E8F8F5'},
    'ayurveda_visit': {'icon': 'fa-leaf', 'color': '#27AE60', 'bg': '#EAFAF1'},
    'medication_purchase': {'icon': 'fa-pills', 'color': '#F39C12', 'bg': '#FEF9E7'},
    'recovery_milestone': {'icon': 'fa-trophy', 'color': '#E67E22', 'bg': '#FDF2E9'},
}

# Report category icons
REPORT_CATEGORY_CONFIG = {
    'laboratory_report': {'icon': 'fa-file-medical-alt', 'color': '#9B59B6'},
    'prescription': {'icon': 'fa-prescription', 'color': '#3498DB'},
    'consultation_notes': {'icon': 'fa-notes-medical', 'color': '#1ABC9C'},
    'ayurveda_records': {'icon': 'fa-leaf', 'color': '#27AE60'},
}
