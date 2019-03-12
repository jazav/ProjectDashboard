from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.issue_utils import get_domain


class DomainBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type = True, None, None, None
    all_spent, all_remain = {'flagged': {}, 'not flagged': {}}, {'flagged': {}, 'not flagged': {}}

    def multi_prepare(self, data_spent, data_original):
        all_original, spent, original = {}, {}, {}
        fl_all_original, fl_spent, fl_original = {}, {}, {}
        for i in range(len(data_spent['key'])):
            data_spent['component'][i] = get_domain(data_spent['component'][i])
            if data_spent['created'][i] < datetime.date(2019, 2, 18):
                if data_spent['component'][i] not in spent.keys():
                    spent[data_spent['component'][i]] = 0
                spent[data_spent['component'][i]] += float(data_spent['spent'][i])
                if data_spent['flagged'][i] is not None:
                    if data_spent['component'][i] not in fl_spent.keys():
                        fl_spent[data_spent['component'][i]] = 0
                    fl_spent[data_spent['component'][i]] += float(data_spent['spent'][i])
        for i in range(len(data_original)):
            data_original['component'][i] = get_domain(data_original['component'][i])
            if data_original['status'][i] not in ('Closed', 'Resolved'):
                if data_original['component'][i] not in original.keys():
                    original[data_original['component'][i]] = 0
                original[data_original['component'][i]] += float(data_original['timeoriginalestimate'][i])
                if data_original['flagged'][i] is not None:
                    if data_original['component'][i] not in fl_original.keys():
                        fl_original[data_original['component'][i]] = 0
                    fl_original[data_original['component'][i]] += float(data_original['timeoriginalestimate'][i])

    def export_to_plotly(self):
        pass

    def export_to_plot(self):
        self.export_to_plotly()
