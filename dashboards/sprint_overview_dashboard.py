from dashboards.dashboard import AbstractDashboard


class SprintOverviewDashboard(AbstractDashboard):
    auto_open, repository, citrix_token, local_user, user, password = True, None, None, None, None, None

    def prepare_data(self):
        pass

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
