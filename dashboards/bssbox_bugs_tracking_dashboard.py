from dashboards.dashboard import AbstractDashboard


class BssboxBugsTrackingDashboard(AbstractDashboard):
    auto_open, repository = True, None

    def prepare(self, data):
        pass
