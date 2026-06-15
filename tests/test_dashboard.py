"""
End-to-end tests for the Dashboard route.
"""


class TestDashboard:
    """Tests for GET /"""

    def test_dashboard_loads_200(self, client):
        """Dashboard returns HTTP 200."""
        resp = client.get('/')
        assert resp.status_code == 200

    def test_dashboard_contains_key_elements(self, client):
        """Dashboard HTML contains expected headings / sections."""
        resp = client.get('/')
        html = resp.data.decode()
        # Page should mention the tracker title or key sections
        assert 'Jaundice' in html or 'Recovery' in html or 'Dashboard' in html

    def test_dashboard_empty_state(self, client):
        """Dashboard works correctly when there is no data in the DB."""
        resp = client.get('/')
        # Must not 500 even with zero records
        assert resp.status_code == 200
