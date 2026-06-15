"""
End-to-end tests for the Database models (unit-level).
Verifies that each model can be created, persisted, and serialised.
"""
import pytest
from datetime import date, datetime
from models.db import db, TimelineEvent, LabResult, Medication, JournalEntry, Report


class TestTimelineEventModel:
    def test_create_and_persist(self, app):
        with app.app_context():
            ev = TimelineEvent(
                event_date=date(2026, 6, 1),
                activity_type='consultation',
                title='Test Event',
                description='Some description',
            )
            db.session.add(ev)
            db.session.commit()

            found = TimelineEvent.query.get(ev.id)
            assert found is not None
            assert found.title == 'Test Event'
            assert found.activity_type == 'consultation'

    def test_to_dict(self, app):
        with app.app_context():
            ev = TimelineEvent(
                event_date=date(2026, 6, 1),
                activity_type='lab_test',
                title='Lab Dict Test',
            )
            db.session.add(ev)
            db.session.commit()

            d = ev.to_dict()
            assert d['title'] == 'Lab Dict Test'
            assert d['event_date'] == '2026-06-01'
            assert 'id' in d

    def test_optional_fields_nullable(self, app):
        with app.app_context():
            ev = TimelineEvent(
                event_date=date(2026, 6, 2),
                activity_type='diagnosis',
                title='Minimal Event',
            )
            db.session.add(ev)
            db.session.commit()
            assert ev.description is None
            assert ev.attachment_path is None


class TestLabResultModel:
    def test_create_and_persist(self, app):
        with app.app_context():
            lr = LabResult(
                test_name='Total Bilirubin',
                test_date=date(2026, 6, 5),
                result_value='4.5',
                result_unit='mg/dL',
                normal_range='0.2-1.2',
                status='high',
            )
            db.session.add(lr)
            db.session.commit()
            found = LabResult.query.get(lr.id)
            assert found.test_name == 'Total Bilirubin'
            assert found.result_value == '4.5'

    def test_to_dict_keys(self, app):
        with app.app_context():
            lr = LabResult(
                test_name='SGPT',
                test_date=date(2026, 6, 1),
            )
            db.session.add(lr)
            db.session.commit()
            d = lr.to_dict()
            expected_keys = ['id', 'test_name', 'test_date', 'result_value',
                             'result_unit', 'normal_range', 'status',
                             'doctor_notes', 'followup_recommendations', 'created_at']
            for key in expected_keys:
                assert key in d


class TestMedicationModel:
    def test_default_status_active(self, app):
        with app.app_context():
            med = Medication(
                medicine_name='Liv 52',
                start_date=date(2026, 5, 1),
                dosage='2 tablets',
                frequency='Twice daily',
            )
            db.session.add(med)
            db.session.commit()
            assert med.status == 'active'

    def test_to_dict_end_date_none(self, app):
        with app.app_context():
            med = Medication(
                medicine_name='Test Med',
                start_date=date(2026, 5, 1),
                dosage='1 tablet',
                frequency='Once daily',
            )
            db.session.add(med)
            db.session.commit()
            d = med.to_dict()
            assert d['end_date'] is None

    def test_to_dict_with_end_date(self, app):
        with app.app_context():
            med = Medication(
                medicine_name='Test Med 2',
                start_date=date(2026, 5, 1),
                end_date=date(2026, 6, 30),
                dosage='1 tablet',
                frequency='Once daily',
                status='completed',
            )
            db.session.add(med)
            db.session.commit()
            d = med.to_dict()
            assert d['end_date'] == '2026-06-30'
            assert d['status'] == 'completed'


class TestJournalEntryModel:
    def test_unique_date_constraint(self, app):
        """Two entries on the same date should raise an IntegrityError."""
        from sqlalchemy.exc import IntegrityError
        with app.app_context():
            e1 = JournalEntry(entry_date=date(2026, 6, 10), energy_level=5)
            db.session.add(e1)
            db.session.commit()

            e2 = JournalEntry(entry_date=date(2026, 6, 10), energy_level=8)
            db.session.add(e2)
            with pytest.raises(IntegrityError):
                db.session.commit()
            db.session.rollback()

    def test_to_dict_all_vitals(self, app):
        with app.app_context():
            entry = JournalEntry(
                entry_date=date(2026, 6, 1),
                symptoms='Fatigue',
                energy_level=5,
                appetite=6,
                sleep_quality=7,
                mood=6,
                observations='Improving',
                recovery_notes='Rest well',
            )
            db.session.add(entry)
            db.session.commit()
            d = entry.to_dict()
            assert d['energy_level'] == 5
            assert d['appetite'] == 6
            assert d['sleep_quality'] == 7
            assert d['mood'] == 6
            assert d['symptoms'] == 'Fatigue'
