from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dashboards.arba_issues_dashboard import split_on, group_on


class ArbaReviewDashboard(AbstractDashboard):
    key_list, assignee_list, issuetype_list, status_list, duedate_list = [], [], [], [], []
    auto_open, assignees = True, None

    def prepare(self, data):
        self.key_list, self.assignee_list, self.issuetype_list, self.status_list, self.duedate_list =\
            data.get_arba_review(self.assignees)
        self.assignee_list = split_on(self.assignee_list)
        self.key_list = group_on(self.key_list, self.assignee_list)
        self.issuetype_list = group_on(self.issuetype_list, self.assignee_list)
        self.status_list = group_on(self.status_list, self.assignee_list)
        self.duedate_list = group_on(self.duedate_list, self.assignee_list)

    def export_to_plotly(self):
        if len(self.key_list) == 0:
            raise ValueError('There is no issues to show')

    def export_to_plot(self):
        self.export_to_plotly()
