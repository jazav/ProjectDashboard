from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta


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


def issue_color(issuetype):
    return {
        'Task': 'rgb(255,255,255)',
        'Sub-task': 'rgb(255,255,255)',
        'Bug': 'rgb(255,255,255)'
    }[issuetype]


class ArbaIssuesDashboard(AbstractDashboard):
    name_list, assignee_list, created_list, duedate_list, key_list, issuetype_list = [], [], [], [], [], []
    auto_open, assignees = True, None
    team_list = [],

    def prepare(self, data):
        self.name_list, self.assignee_list, self.created_list, self.duedate_list, self.key_list, self.issuetype_list =\
            data.get_arba_issues(self.assignees)
        self.assignee_list = split_on(self.assignee_list)
        self.duedate_list = group_on(self.duedate_list, self.assignee_list)
        self.name_list = group_on(self.name_list, self.assignee_list)
        self.key_list = group_on(self.key_list, self.assignee_list)
        self.issuetype_list = group_on(self.issuetype_list, self.assignee_list)
        # for i in range(len(self.name_list)):
        #     if self.assignee_list[i] not in self.team_dict:
        #         self.team_dict[self.assignee_list[i]] = [[], []]
        #     self.team_dict[self.assignee_list[i]][0].append(self.name_list[i])
        #     self.team_dict[self.assignee_list[i]][1].append(self.duedate_list[i][:11].strip())
        # print(self.team_dict)
        # max_tasks = 0
        # for i in range(len(self.assignee_list)):
        #     if self.assignee_list.count(self.assignee_list[i]) > max_tasks:
        #         max_tasks = self.assignee_list.count(self.assignee_list[i])
        # self.team_list = [[[], [], []] for _ in range(max_tasks)]
        # for i in range(len(self.assignee_list)):
        #     self.team_list[self.assignee_list[:i].count(self.assignee_list[i])][0].append(self.assignee_list[i])
        #     self.team_list[self.assignee_list[:i].count(self.assignee_list[i])][1].append(self.duedate_list[i])
        #     self.team_list[self.assignee_list[:i].count(self.assignee_list[i])][2].append(self.name_list[i])

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            raise ValueError('There is no issues to show')

        data, annotations = [], []
        start_date = str((datetime.now() - timedelta(days=8)).date())
        end_date = str((datetime.now() + timedelta(days=22)).date())
        for i in range(len(self.assignee_list)):
            for j in range(len(self.assignee_list[i])):
                data.append(go.Scatter(
                    x=[self.duedate_list[i][j]],
                    y=[self.assignee_list[i][j]],
                    mode='markers',
                    marker=dict(
                        size=12,
                        color='rgb(255,100,100)'
                        if datetime.strptime(self.duedate_list[i][j][:11].strip(),
                                             '%Y-%m-%d').date() < datetime.now().date() else 'rgb(254,210,92)'
                    )
                ))
            data.append(go.Scatter(
                x=[start_date, end_date],
                y=[self.assignee_list[i][0], self.assignee_list[i][0]],
                mode='lines',
                line=dict(
                    color='rgb(115,115,115)',
                    width=1,
                    dash='dash'),
                opacity=0.4
            ))

        for i in range(len(self.assignee_list)):
            for j in range(len(self.assignee_list[i])):
                annotations.append(dict(
                    x=self.duedate_list[i][j],
                    y=self.assignee_list[i][j],
                    xref='x',
                    yref='y',
                    xanchor='center',
                    text=self.key_list[i][j][8:] + ': ' + self.name_list[i][j][:26] + '...',
                    showarrow=True,
                    arrowwidth=0.5,
                    arrowcolor='rgb(115,115,115)',
                    arrowhead=0,
                    ax=-80,
                    # ay=-40 - 20 * (self.duedate_list[i][:j].count(self.duedate_list[i][j]))
                    ay=-20 - 15 * j,
                    font=dict(
                        size=10
                    ),
                    bordercolor='rgb(115,115,115)',
                    borderwidth=1,
                    borderpad=1,
                    bgcolor=issue_color(self.issuetype_list[i][j]),
                    opacity=0.8
                ))
        annotations.append(dict(
            xref='x',
            yref='paper',
            xanchor='left',
            x=datetime.now().date(),
            y=0,
            # text=datetime.strftime(datetime.now(), '%b %d'),
            text='Today',
            showarrow=False,
            font=dict(
                color='rgb(255,100,100)'
            )
        ))

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        layout = go.Layout(
            barmode='group',
            annotations=annotations,
            showlegend=False,
            title=title,
            autosize=True,
            xaxis=dict(
                type='date',
                range=[start_date, end_date],
                dtick=86400000,
                # rangeslider=dict(
                #     visible=True
                # )
            ),
            yaxis=dict(
                automargin=True
            ),
            shapes=[dict(
                type='line',
                xref='x',
                yref='paper',
                x0=datetime.now().date(),
                y0=0,
                x1=datetime.now().date(),
                y1=1,
                line=dict(
                    color='rgb(255,100,100)',
                    width=1.5
                )
            )]
        )

        fig = dict(data=data, layout=layout)
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
