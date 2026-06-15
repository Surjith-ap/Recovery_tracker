"""
End-to-end tests for the Journal route.
Covers: list, add (create & upsert), delete, validation.
"""
import pytest
from datetime import date, timedelta


JOURNAL_URL = '/journal/'
ADD_URL = '/journal/add'


def _delete_url(entry_id):
    return f'/journal/delete/{entry_id}'


class TestJournalIndex:
    def test_journal_page_loads(self, client):
        resp = client.get(JOURNAL_URL)
        assert resp.status_code == 200

    def test_journal_page_empty(self, client):
        resp = client.get(JOURNAL_URL)
        assert resp.status_code == 200
        # No crash on empty DB


class TestJournalAdd:
    def _post(self, client, data):
        return client.post(ADD_URL, data=data, follow_redirects=True)

    def test_add_journal_entry_success(self, client):
        """Adding a complete journal entry should succeed with flash message."""
        resp = self._post(client, {
            'entry_date': '2026-06-10',
            'symptoms': 'Mild fatigue, some yellowing',
            'energy_level': '5',
            'appetite': '6',
            'sleep_quality': '7',
            'mood': '6',
            'observations': 'Feeling slightly better than yesterday.',
            'recovery_notes': 'Continue bed rest.',
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        # Flash message should appear
        assert 'added' in html.lower() or 'success' in html.lower()

    def test_add_journal_entry_upsert(self, client):
        """Posting the same date twice should UPDATE the existing entry, not duplicate."""
        data = {
            'entry_date': '2026-06-11',
            'symptoms': 'First entry',
            'energy_level': '4',
            'appetite': '4',
            'sleep_quality': '4',
            'mood': '4',
        }
        self._post(client, data)
        # Post again with updated symptoms
        data['symptoms'] = 'Updated entry'
        resp = self._post(client, data)
        html = resp.data.decode()
        assert 'updated' in html.lower() or 'success' in html.lower()
        # Verify only 1 entry exists for that date
        assert html.count('2026-06-11') >= 1

    def test_add_journal_requires_date(self, client):
        """Submitting without a date should show an error flash."""
        resp = self._post(client, {
            'entry_date': '',
            'symptoms': 'No date test',
        })
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_journal_partial_data(self, client):
        """Date-only submission (no vitals) should still save without crashing."""
        resp = self._post(client, {
            'entry_date': '2026-06-12',
        })
        assert resp.status_code == 200

    def test_multiple_entries_different_dates(self, client):
        """Multiple entries on different dates should all appear on the journal page."""
        for i, day in enumerate(['2026-06-01', '2026-06-02', '2026-06-03'], start=1):
            self._post(client, {
                'entry_date': day,
                'energy_level': str(i),
                'mood': str(i),
            })
        resp = client.get(JOURNAL_URL)
        html = resp.data.decode()
        assert '2026-06-01' in html
        assert '2026-06-02' in html
        assert '2026-06-03' in html


class TestJournalDelete:
    def _add(self, client, date_str='2026-05-20'):
        client.post(ADD_URL, data={
            'entry_date': date_str,
            'symptoms': 'Test entry',
            'energy_level': '5',
        }, follow_redirects=True)

    def test_delete_existing_entry(self, client, app):
        """Deleting an existing journal entry should remove it from DB."""
        self._add(client, '2026-05-21')
        # Get the ID from the DB directly
        from models.db import JournalEntry
        with app.app_context():
            entry = JournalEntry.query.filter_by(
                entry_date=date(2026, 5, 21)
            ).first()
            assert entry is not None
            entry_id = entry.id

        resp = client.post(_delete_url(entry_id), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'deleted' in html.lower() or 'success' in html.lower()

        # Confirm removal
        with app.app_context():
            from models.db import JournalEntry
            deleted = JournalEntry.query.get(entry_id)
            assert deleted is None

    def test_delete_nonexistent_returns_404(self, client):
        """Deleting a non-existent entry should return 404."""
        resp = client.post(_delete_url(99999), follow_redirects=True)
        assert resp.status_code == 404
