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
            grouped[-1].append(lst[j])
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
        print(self.duedate_list)

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')

        data, annotations = [], []
        for i in range(len(self.assignee_list)):
            data.append(go.Scatter(
                x=self.duedate_list[i],
                y=self.assignee_list[i],
                mode='markers',
                name=self.assignee_list[i][0]
            ))
        for i in range(len(self.assignee_list)):
            for j in range(len(self.assignee_list[i])):
                annotations.append(dict(
                    x=self.duedate_list[i][j],
                    y=self.assignee_list[i][j],
                    xref='x',
                    yref='y',
                    text=self.name_list[i][j][:11] + '...',
                    showarrow=True,
                    arrowwidth=0.5,
                    arrowcolor='#636363',
                    arrowhead=0,
                    ax=-80,
                    ay=-40 - 20 * (self.duedate_list[i][:j].count(self.duedate_list[i][j]))
                ))

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        layout = go.Layout(
            annotations=annotations,
            showlegend=False,
            title=title,
            autosize=True,
            xaxis=dict(
                range=['2018-11-25', '2019-01-01']
            )
        )

        fig = dict(data=data, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
