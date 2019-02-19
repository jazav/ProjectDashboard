from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain


class SprintInfoDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] != 'User Story (L3)':
                print('{}: {}'.format(data['Component'][i], get_domain(data['Component'][i])))

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
