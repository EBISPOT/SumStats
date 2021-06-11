from sumstats.server.app import app


class TestAPI(object):

    def test_api_root(self):
        test_app = app.test_client()
        test_app.testing = True

        result = test_app.get("/gwas/summary-statistics/api")
        assert result.status_code == 200

    def test_something_associations_endpoint(self):
        test_app = app.test_client()
        test_app.testing = True
        result = test_app.get("/gwas/summary-statistics/api/associations")
        assert result.status_code == 200
