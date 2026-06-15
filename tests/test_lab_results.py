"""
End-to-end tests for the Lab Results route.
Covers: list, add, edit, delete, chart-data API, validation, filtering.
"""
from datetime import date


LAB_URL = '/lab-results/'
ADD_URL = '/lab-results/add'


def _delete_url(rid): return f'/lab-results/delete/{rid}'
def _edit_url(rid):   return f'/lab-results/edit/{rid}'
def _chart_url(test='Total Bilirubin'): return f'/lab-results/api/chart-data?test={test}'


def _sample_payload(**overrides):
    data = {
        'test_name': 'Total Bilirubin',
        'test_date': '2026-06-05',
        'result_value': '3.2',
        'result_unit': 'mg/dL',
        'normal_range': '0.2-1.2',
        'status': 'high',
        'doctor_notes': 'Monitor closely.',
        'followup_recommendations': 'Repeat in 3 days.',
    }
    data.update(overrides)
    return data


class TestLabResultsIndex:
    def test_page_loads(self, client):
        resp = client.get(LAB_URL)
        assert resp.status_code == 200

    def test_filter_all(self, client):
        resp = client.get(LAB_URL + '?test=all')
        assert resp.status_code == 200

    def test_filter_specific_test(self, client):
        """Filter by a specific test name should not crash even if no results."""
        resp = client.get(LAB_URL + '?test=SGPT')
        assert resp.status_code == 200


class TestLabResultsAdd:
    def test_add_result_success(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'added' in html.lower() or 'success' in html.lower()

    def test_add_result_appears_in_list(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        resp = client.get(LAB_URL)
        html = resp.data.decode()
        assert 'Bilirubin' in html

    def test_add_requires_test_name(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(test_name=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_requires_test_date(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(test_date=''),
                           follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'required' in html.lower() or 'error' in html.lower()

    def test_add_multiple_results(self, client):
        for val, d in [('3.2', '2026-06-01'), ('2.1', '2026-06-05'), ('1.5', '2026-06-10')]:
            client.post(ADD_URL,
                        data=_sample_payload(result_value=val, test_date=d),
                        follow_redirects=True)
        resp = client.get(LAB_URL)
        html = resp.data.decode()
        assert 'Bilirubin' in html

    def test_add_sgpt_result(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(
            test_name='SGPT', result_value='120', result_unit='U/L',
            normal_range='7-56', status='high'
        ), follow_redirects=True)
        assert resp.status_code == 200

    def test_add_custom_test_name(self, client):
        resp = client.post(ADD_URL, data=_sample_payload(
            test_name='Other',
            custom_test_name='HbsAg'
        ), follow_redirects=True)
        assert resp.status_code == 200


class TestLabResultsEdit:
    def _create(self, client):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        from models.db import LabResult
        return LabResult.query.first()

    def test_edit_result(self, client, app):
        with app.app_context():
            r = self._create(client)
            rid = r.id

        resp = client.post(_edit_url(rid), data=_sample_payload(
            result_value='1.9', status='normal'
        ), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'updated' in html.lower() or 'success' in html.lower()

        with app.app_context():
            from models.db import LabResult
            updated = LabResult.query.get(rid)
            assert updated.result_value == '1.9'
            assert updated.status == 'normal'

    def test_edit_nonexistent_returns_404(self, client):
        resp = client.post(_edit_url(99999), data=_sample_payload(),
                           follow_redirects=True)
        assert resp.status_code == 404


class TestLabResultsDelete:
    def test_delete_result(self, client, app):
        client.post(ADD_URL, data=_sample_payload(), follow_redirects=True)
        with app.app_context():
            from models.db import LabResult
            rid = LabResult.query.first().id

        resp = client.post(_delete_url(rid), follow_redirects=True)
        assert resp.status_code == 200
        html = resp.data.decode()
        assert 'deleted' in html.lower() or 'success' in html.lower()

        with app.app_context():
            from models.db import LabResult
            assert LabResult.query.get(rid) is None

    def test_delete_nonexistent_returns_404(self, client):
        resp = client.post(_delete_url(99999), follow_redirects=True)
        assert resp.status_code == 404


class TestLabResultsChartAPI:
    def test_chart_data_empty(self, client):
        resp = client.get(_chart_url())
        assert resp.status_code == 200
        data = resp.get_json()
        assert 'labels' in data
        assert 'values' in data
        assert data['labels'] == []
        assert data['values'] == []

    def test_chart_data_with_results(self, client):
        for val, d in [('5.0', '2026-06-01'), ('3.5', '2026-06-07'), ('2.0', '2026-06-14')]:
            client.post(ADD_URL,
                        data=_sample_payload(result_value=val, test_date=d),
                        follow_redirects=True)
        resp = client.get(_chart_url('Total Bilirubin'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['values']) == 3
        assert data['values'] == [5.0, 3.5, 2.0]

    def test_chart_data_custom_test(self, client):
        client.post(ADD_URL, data=_sample_payload(
            test_name='SGPT', result_value='88', test_date='2026-06-10'
        ), follow_redirects=True)
        resp = client.get(_chart_url('SGPT'))
        assert resp.status_code == 200
        data = resp.get_json()
        assert len(data['values']) == 1
        assert data['values'][0] == 88.0
