from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime


def split_on(lst):
    splitted = [[lst[0]]]
    for i in range(1, len(lst)):
        if lst[i] == lst[i - 1]:
            splitted[-1].append(lst[i])
        else:
            splitted.append([])
            splitted[-1].append(lst[i])
    return splitted


def group_on(lst, splitted):
    grouped, start, end = [], 0, 0
    for i in range(len(splitted)):
        grouped.append([])
        end += len(splitted[i])
        for j in range(start, end):
            grouped[-1].append(lst[j][:11].strip())
        start = end
    return grouped


class ArbaIssuesDashboard(AbstractDashboard):
    name_list, assignee_list, created_list, duedate_list = [], [], [], []
    auto_open, assignees = True, None
    team_dict = {}

    def prepare(self, data):
        self.name_list, self.assignee_list, self.created_list, self.duedate_list = data.get_arba_issues(self.assignees)
        self.assignee_list = split_on(self.assignee_list)
        self.duedate_list = group_on(self.duedate_list, self.assignee_list)
        self.name_list = group_on(self.name_list, self.assignee_list)

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')

        data = []
        for i in range(len(self.assignee_list)):
            data.append(go.Scatter(
                x=self.duedate_list[i],
                y=self.assignee_list[i],
                name=self.assignee_list[i][0]
            ))

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        layout = dict(
            title=title,
            xaxis=dict(
                range=['2018-11-01', '2019-02-01'])
        )

        fig = dict(data=data, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
