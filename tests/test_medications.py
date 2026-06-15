"""
End-to-end tests for the Medications route.
Covers: list, add, edit, delete, status-update, filtering, validation.
"""


MED_URL = '/medications/'
ADD_URL = '/medications/add'


def _delete_url(mid): return f'/medications/delete/{mid}'
def _edit_url(mid):   return f'/medications/edit/{mid}'
def _status_url(mid): return f'/medications/update-status/{mid}'


def _sample_payload(**overrides):
    data = {
        'medicine_name': 'Liv 52 DS',
        'start_date': '2026-05-01',
        'end_date': '',
        'dosage': '2 tablets',
        'frequency': 'Twice daily after meals',
        'instructions': 'Take with warm water',
        'status': 'active',
        'prescribed_by': 'Dr. Sharma',
    }
    data.update(overrides)
    return data


class TestMedicationsIndex:
    def test_page_loads(self, client):
        resp = client.get(MED_URL)
        assert resp.status_code == 200

    def test_filter_active(self, client):
        resp = client.get(MED_URL + '?status=active')
        assert resp.status_code == 200

    def test_filter_completed(self, client):
        resp = client.get(MED_URL + '?status=completed')
        assert resp.status_code == 200

    def test_filter_discontinued(self, client):
        resp = client.get(MED_URL + '?status=discontinued')
        assert resp.status_code == 200


class TestMedicationsAdd:
    def test_add_medication_success(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'added' in html.lower() or 'success' in html.lower()

    def test_add_medication_appears_in_list(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        resp = client.get(MED_URL)
        html = resp.data.decode()
        assert 'Liv 52' in html

    def test_add_requires_medicine_name(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(medicine_name=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_requires_start_date(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(start_date=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_requires_dosage(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(dosage=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_with_end_date(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(
            end_date='2026-06-30',
            status='completed',
        ), follow_redirects=True)
        assert resp.status_code == 200

    def test_add_multiple_medications(self, client):
        for name in ['Udiliv 300', 'Syrup Aristozyme', 'Pantoprazole']:
            client.post(ADD_URL, data=_sample_payload(medicine_name=name),
                        follow_redirects=True)
        resp = client.get(MED_URL)
        html = resp.data.decode()
        assert 'Udiliv' in html
        assert 'Aristozyme' in html
        assert 'Pantoprazole' in html


class TestMedicationsEdit:
    def _create(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        from models.db import Medication
        return Medication.query.first()

    def test_edit_medication(self, client, app):
        with app.app_context():
            m = self._create(client)
            mid = m.id

        resp = client.post(_edit_url(mid), data=_sample_payload(
            dosage='3 tablets',
            status='completed',
        ), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'updated' in html.lower() or 'success' in html.lower()

        with app.app_context():
            from models.db import Medication
            updated = Medication.query.get(mid)
            assert updated.dosage == '3 tablets'
            assert updated.status == 'completed'

    def test_edit_nonexistent_returns_404(self, client):
        resp = client.post(_edit_url(99999), data=_sample_payload(),
                           follow_redirects=True)
        assert resp.status_code == 404


class TestMedicationsDelete:
    def test_delete_medication(self, client, app):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        with app.app_context():
            from models.db import Medication
            mid = Medication.query.first().id

        resp = client.post(_delete_url(mid), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'deleted' in html.lower() or 'success' in html.lower()

        with app.app_context():
            from models.db import Medication
            assert Medication.query.get(mid) is None

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.post(_delete_url(99999), follow_redirects=True)
        assert resp.status_code == 404


class TestMedicationsStatusUpdate:
    def _create(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        from models.db import Medication
        return Medication.query.first()

    def test_update_status_to_completed(self, client, app):
        with app.app_context():
            m = self._create(client)
            mid = m.id

        resp = client.post(_status_url(mid), data={'status': 'completed'},
                           follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            from models.db import Medication
            assert Medication.query.get(mid).status == 'completed'

    def test_update_status_to_discontinued(self, client, app):
        with app.app_context():
            m = self._create(client)
            mid = m.id

        resp = client.post(_status_url(mid), data={'status': 'discontinued'},
                           follow_redirects=True)
        assert resp.status_code == 200

        with app.app_context():
            from models.db import Medication
            assert Medication.query.get(mid).status == 'discontinued'

    def test_invalid_status_ignored(self, client, app):
        """An invalid status value should not change the medication status."""
        with app.app_context():
            m = self._create(client)
            mid = m.id

        client.post(_status_url(mid), data={'status': 'bogus_status'},
                    follow_redirects=True)

        with app.app_context():
            from models.db import Medication
            # Status should remain 'active' (unchanged)
            assert Medication.query.get(mid).status == 'active'
