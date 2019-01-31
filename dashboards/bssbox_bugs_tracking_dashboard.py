from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain, get_domain_by_project
import datetime
import numpy


class BssboxBugsTrackingDashboard(AbstractDashboard):
    auto_open, repository = True, None
    prepared_data = {}

    def prepare(self, data):
        self.prepared_data = {key: [] for key in data.keys()}
        for i in range(len(data['jira_key'])):
            data['component'][i] = get_domain(data['component'][i]) if data['component'][i] != ''\
                else get_domain_by_project(data['component'][i])
            data['start'][i] = int(numpy.busday_count(data['start'][i], datetime.datetime.now().date()) + 1)
            if data['component'][i] != 'Others':
                for key in data.keys():
                    self.prepared_data[key].append(data[key][i])
        print(self.prepared_data)

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
