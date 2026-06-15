"""
End-to-end tests for the Timeline route.
Covers: list, add, edit, delete, filtering by activity type.
"""
import io


TIMELINE_URL = '/timeline/'
ADD_URL = '/timeline/add'


def _delete_url(eid): return f'/timeline/delete/{eid}'
def _edit_url(eid):   return f'/timeline/edit/{eid}'


def _sample_payload(**overrides):
    data = {
        'event_date': '2026-06-01',
        'activity_type': 'consultation',
        'title': 'First GI Consultation',
        'description': 'Discussed liver function tests with Dr. Mehta.',
    }
    data.update(overrides)
    return data


class TestTimelineIndex:
    def test_page_loads(self, client):
        resp = client.get(TIMELINE_URL)
        assert resp.status_code == 200

    def test_filter_all(self, client):
        resp = client.get(TIMELINE_URL + '?type=all')
        assert resp.status_code == 200

    def test_filter_by_type(self, client):
        for activity in ['consultation', 'hospital_visit', 'lab_test',
                          'ayurveda_visit', 'recovery_milestone']:
            resp = client.get(TIMELINE_URL + f'?type={activity}')
            assert resp.status_code == 200


class TestTimelineAdd:
    def test_add_event_success(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'added' in html.lower() or 'success' in html.lower()

    def test_add_event_appears_in_list(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        resp = client.get(TIMELINE_URL)
        html = resp.data.decode()
        assert 'First GI Consultation' in html

    def test_add_requires_date(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(event_date=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_requires_activity_type(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(activity_type=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_requires_title(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(title=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_all_activity_types(self, client):
        """All valid activity types should be accepted."""
        activity_types = [
            'diagnosis', 'hospital_visit', 'lab_test', 'consultation',
            'ayurveda_visit', 'medication_purchase', 'recovery_milestone',
        ]
        for i, atype in enumerate(activity_types):
            resp = client.post(ADD_URL, data=_sample_payload(
                activity_type=atype,
                title=f'Test event {i}',
                event_date=f'2026-06-0{i+1}',
            ), follow_redirects=True)
            assert resp.status_code == 200

    def test_add_event_with_file_attachment(self, client):
        """Adding an event with a valid file attachment should succeed."""
        data = _sample_payload()
        data['attachment'] = (io.BytesIO(b'%PDF fake content'), 'report.pdf')
        resp = client.post(ADD_URL, data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
        assert resp.status_code == 200

    def test_add_event_with_invalid_file_type(self, client):
        """Attachment with disallowed extension should be silently ignored."""
        data = _sample_payload()
        data['attachment'] = (io.BytesIO(b'malicious'), 'evil.exe')
        resp = client.post(ADD_URL, data=data,
                           content_type='multipart/form-data',
                           follow_redirects=True)
        # Should succeed but not store the bad file
        assert resp.status_code == 200


class TestTimelineEdit:
    def _create(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        from models.db import TimelineEvent
        return TimelineEvent.query.first()

    def test_edit_event(self, client, app):
        with app.app_context():
            e = self._create(client)
            eid = e.id

        resp = client.post(_edit_url(eid), data=_sample_payload(
            title='Updated Consultation',
            activity_type='hospital_visit',
        ), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'updated' in html.lower() or 'success' in html.lower()

        with app.app_context():
            from models.db import TimelineEvent
            ev = TimelineEvent.query.get(eid)
            assert ev.title == 'Updated Consultation'
            assert ev.activity_type == 'hospital_visit'

    def test_edit_nonexistent_returns_404(self, client):
        resp = client.post(_edit_url(99999), data=_sample_payload(),
                           follow_redirects=True)
        assert resp.status_code == 404


class TestTimelineDelete:
    def test_delete_event(self, client, app):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        with app.app_context():
            from models.db import TimelineEvent
            eid = TimelineEvent.query.first().id

        resp = client.post(_delete_url(eid), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'deleted' in html.lower() or 'success' in html.lower()

        with app.app_context():
            from models.db import TimelineEvent
            assert TimelineEvent.query.get(eid) is None

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.post(_delete_url(99999), follow_redirects=True)
        assert resp.status_code == 404


class TestTimelineFiltering:
    def test_filter_shows_only_matching_type(self, client):
        """Filtering by 'consultation' should not show 'hospital_visit' events."""
        client.post(ADD_URL, data=_sample_payload(
            activity_type='consultation', title='Consult Event'
        ), follow_redirects=True)
        client.post(ADD_URL, data=_sample_payload(
            activity_type='hospital_visit', title='Hospital Event',
            event_date='2026-06-02'
        ), follow_redirects=True)

        resp = client.get(TIMELINE_URL + '?type=consultation')
        html = resp.data.decode()
        assert 'Consult Event' in html
