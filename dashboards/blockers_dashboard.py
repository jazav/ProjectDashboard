from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta
from adapters.issue_utils import get_domain, get_domain_by_project


class BlockersDashboard(AbstractDashboard):
    key_list, created_list, status_list, components_list = [], [], [], []
    auto_open, priority, fixversion, projects, statuses = True, None, None, None, None

    def prepare(self, data):
        self.key_list, self.created_list, self.status_list, self.components_list =\
            data.get_bugs(self.projects, self.priority, self.fixversion, self.statuses)
        print(self.key_list)
