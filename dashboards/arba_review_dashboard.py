from dashboards.dashboard import AbstractDashboard
import plotly
from plotly import tools
# import plotly.figure_factory as ff
import plotly.graph_objs as go
from datetime import datetime, timedelta
from dashboards.arba_issues_dashboard import split_on, group_on
import math


def domain_position(row, col):
    x_pos = {1: [0, 0.32],
             2: [0.34, 0.66],
             3: [0.68, 1]}
    y_pos = {1: [0.55, 1],
             2: [0, 0.45]}
    return dict(
        x=x_pos[col],
        y=y_pos[row]
    )

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

        table_dict = {assignee[0]: None for assignee in self.assignee_list}
        # for assignee in table_dict.keys():
        #     assignee_data = [['Open bugs:', ''],
        #                      ['Closed bugs', ''],
        #                      ['Issues without duedate', ''],
        #                      ['Overdue task/s', ''],
        #                      ['Overdue sub-task/s', ''],
        #                      ['Overdue bug/s', ''],
        #                      ['Estimate accuracy', ''],
        #                      ['Focus Factor', '']]
        #     colorscale = [[0, '#ffffff'], [.5, '#ffffff'], [1, '#ffffff']]
        #     font = ['#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000', '#000000']
        #     table_dict[assignee] = ff.create_table(assignee_data, colorscale=colorscale, font_colors=font)
        # cols = math.ceil(len(table_dict.keys())/2)
        # fig = tools.make_subplots(rows=2, cols=cols, subplot_titles=list(table_dict.keys()))
        # for table, i in zip(table_dict.values(), range(len(table_dict.keys()))):
        #     row, col = int(i // cols + 1), int(i % cols + 1)
        #     fig.append_trace(table['data'][0], row, col)
        #     xaxis, yaxis = 'xaxis' + str(i+1), 'yaxis' + str(i+1)
        #     xref, yref = 'x' + str(i+1), 'y' + str(i+1)
        #     fig['layout'][xaxis].update(table['layout']['xaxis'])
        #     fig['layout'][yaxis].update(table['layout']['yaxis'])
        #     for j in range(len(table['layout']['annotations'])):
        #         table['layout']['annotations'][j].update(xref=xref, yref=yref)
        #     fig['layout']['annotations'] += table['layout']['annotations']
        cols = math.ceil(len(table_dict.keys()) / 2)
        for assignee, i in zip(table_dict.keys(), range(len(table_dict.keys()))):
            open_bugs, closed_bugs = '', ''
            not_duedated, overdue_tasks, overdue_subtasks, overdue_bugs = '', '', '', ''
            for j in range(len(self.assignee_list[i])):
                if self.issuetype_list[i][j] == 'Bug' and self.status_list[i][j] in ('Open', 'Reopened', 'Dev'):
                    open_bugs += '{0}, '.format(self.key_list[i][j])
                elif self.issuetype_list[i][j] == 'Bug' and self.status_list[i][j] in ('Closed', 'Resolved'):
                    closed_bugs += '{0}, '.format(self.key_list[i][j])
                elif self.status_list[i][j] not in ('Closed', 'Resolved'):
                    if self.duedate_list[i][j] is None and self.issuetype_list[i][j] != 'Epic':
                        not_duedated += '{0}, '.format(self.key_list[i][j])
                    elif self.duedate_list[i][j] is not None and datetime.strptime(
                            self.duedate_list[i][j][:11].strip(), '%Y-%m-%d').date() < datetime.now().date():
                        if self.issuetype_list[i][j] == 'Task':
                            overdue_tasks += '{0}, '.format(self.key_list[i][j])
                        elif self.issuetype_list[i][j] == 'Sub-task':
                            overdue_subtasks += '{0}, '.format(self.key_list[i][j])
                        elif self.issuetype_list[i][j] == 'Bug':
                            overdue_bugs += '{0}, '.format(self.key_list[i][j])
            row, col = int(i // cols + 1), int(i % cols + 1)
            table_dict[assignee] = go.Table(
                domain=domain_position(row, col),
                columnorder=[1, 2],
                columnwidth=[75, 180],
                header=dict(
                    values=[[assignee],
                            ['']],
                    fill=dict(
                        color=['white']
                    ),
                    line=dict(
                        width=0
                    ),
                    font=dict(
                        size=16
                    ),
                    height=35
                ),
                cells=dict(
                    values=[['<b>Open bugs:</b>', '<b>Closed bugs:</b>', '<b>Issues w/o duedate:</b>',
                             '<b>Overdue tasks:</b>', '<b>Overdue sub-tasks:</b>', '<b>Overdue bugs:</b>',
                             '<b>Estimation accuracy:</b>', '<b>Focus Factor:</b>'],
                            [open_bugs[:-2], closed_bugs[:-2], not_duedated[:-2], overdue_tasks[:-2],
                             overdue_subtasks[:-2], overdue_bugs[:-2], '', '']],
                    align=['right', 'left'],
                    fill=dict(
                        color=[['rgb(255,255,255)', 'rgb(255,255,255)', 'rgb(240,240,240)', 'rgb(240,240,240)',
                               'rgb(240,240,240)', 'rgb(240,240,240)', 'rgb(224,224,224)', 'rgb(224,224,224)']]
                    ),
                    line=dict(
                        color='black'
                    ),
                    height=35
                )
            )

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        fig = go.Figure(data=list(table_dict.values()))
        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
