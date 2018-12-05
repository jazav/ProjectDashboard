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
    team_list = [],

    def prepare(self, data):
        self.name_list, self.assignee_list, self.created_list, self.duedate_list = data.get_arba_issues(self.assignees)
        # self.assignee_list = split_on(self.assignee_list)
        # self.duedate_list = group_on(self.duedate_list, self.assignee_list)
        # self.name_list = group_on(self.name_list, self.assignee_list)
        # for i in range(len(self.name_list)):
        #     if self.assignee_list[i] not in self.team_dict:
        #         self.team_dict[self.assignee_list[i]] = [[], []]
        #     self.team_dict[self.assignee_list[i]][0].append(self.name_list[i])
        #     self.team_dict[self.assignee_list[i]][1].append(self.duedate_list[i][:11].strip())
        # print(self.team_dict)
        max_tasks = 0
        for i in range(len(self.assignee_list)):
            if self.assignee_list.count(self.assignee_list[i]) > max_tasks:
                max_tasks = self.assignee_list.count(self.assignee_list[i])
        self.team_list = [[[], [], []] for _ in range(max_tasks)]
        for i in range(len(self.assignee_list)):
            self.team_list[self.assignee_list[:i].count(self.assignee_list[i])][0].append(self.assignee_list[i])
            self.team_list[self.assignee_list[:i].count(self.assignee_list[i])][1].append(self.duedate_list[i])
            self.team_list[self.assignee_list[:i].count(self.assignee_list[i])][2].append(self.name_list[i])

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')

        data, annotations = [], []
        for i in range(len(self.team_list)):
            data.append(go.Bar(
                x=self.team_list[i][1],
                y=self.team_list[i][0],
                width=0.05,
                orientation='h'
            ))
        # for i in range(len(self.assignee_list)):
        #     for j in range(len(self.assignee_list[i])):
        #         annotations.append(dict(
        #             x=self.duedate_list[i][j],
        #             y=self.assignee_list[i][j],
        #             xref='x',
        #             yref='y',
        #             text=self.name_list[i][j][:11] + '...',
        #             showarrow=True,
        #             arrowwidth=0.5,
        #             arrowcolor='#636363',
        #             arrowhead=0,
        #             ax=-80,
        #             ay=-40 - 20 * (self.duedate_list[i][:j].count(self.duedate_list[i][j]))
        #         ))

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        layout = go.Layout(
            barmode='group',
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
