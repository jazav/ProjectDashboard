from dashboards.dashboard import AbstractDashboard


class AllBugsDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
