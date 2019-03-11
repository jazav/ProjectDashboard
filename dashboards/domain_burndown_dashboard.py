from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime


class DomainBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type = True, None, None, None

    def multi_prepare(self, data_spent, data_original):
        pass

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
