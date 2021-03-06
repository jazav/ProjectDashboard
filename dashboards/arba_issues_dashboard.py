from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime, timedelta
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


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


def issue_color(issuetype, part):
    if part == 'background':
        return {
            'Task': 'rgb(75,173,232)',
            'Sub-task': 'white',
            'Bug': 'rgb(249,88,58)'
        }[issuetype]
    elif part == 'border':
        return {
            'Task': 'white',
            'Sub-task': 'rgb(75,173,232)',
            'Bug': 'white'
        }[issuetype]
    elif part == 'font':
        return {
            'Task': 'white',
            'Sub-task': 'rgb(75,173,232)',
            'Bug': 'white'
        }[issuetype]


class ArbaIssuesDashboard(AbstractDashboard):
    name_list, assignee_list, created_list, duedate_list, key_list, issuetype_list = [], [], [], [], [], []
    auto_open, assignees, repository, citrix_token, local_user = True, None, None, None, None
    team_list = []

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
                    text=self.key_list[i][j][8:] + ': ' + self.name_list[i][j][:30] + '...',
                    showarrow=True,
                    arrowwidth=0.5,
                    arrowcolor='rgb(115,115,115)',
                    arrowhead=0,
                    ax=-80,
                    # ay=-40 - 20 * (self.duedate_list[i][:j].count(self.duedate_list[i][j]))
                    ay=-25 - 18.5 * j,
                    font=dict(
                        size=12,
                        color=issue_color(self.issuetype_list[i][j], 'font')
                    ),
                    bordercolor=issue_color(self.issuetype_list[i][j], 'border'),
                    borderwidth=1,
                    borderpad=1,
                    bgcolor=issue_color(self.issuetype_list[i][j], 'background'),
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
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

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
                tickfont=dict(
                    size=14
                )
                # rangeslider=dict(
                #     visible=True
                # )
            ),
            yaxis=dict(
                automargin=True,
                tickfont=dict(
                    size=14
                )
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
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'citrix':
            plotly.offline.plot(fig, image_filename=title, image='png', image_height=1080, image_width=1920)
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
            time.sleep(5)
            shutil.move('C:/Users/{}/Downloads/{}.png'.format(self.local_user, title), './files/{}.png'.format(title))
            citrix = CitrixShareFile(hostname=self.citrix_token['hostname'], client_id=self.citrix_token['client_id'],
                                     client_secret=self.citrix_token['client_secret'],
                                     username=self.citrix_token['username'], password=self.citrix_token['password'])
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path='./files/{}.png'.format(title))
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path=html_file)

    def export_to_plot(self):
        self.export_to_plotly()
