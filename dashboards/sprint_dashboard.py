from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain_by_project, get_domain
import plotly.plotly
import plotly.graph_objs as go
from datetime import datetime


def color_for_status(status):
    return {
        'Open': 'rgb(217,98,89)',
        'In Fix': 'rgb(254,210,92)',
        'Closed': 'rgb(29,137,49)'
    }[status]


class SprintDashboard(AbstractDashboard):
    auto_open, fixversion, repository, plotly_auth = True, None, None, None
    key_list, project_list, status_list, components_list, timeoriginalestimate_list, timespent_list, issuetype_list = \
        [], [], [], [], [], [], []
    domain_list, bugs_dict, accuracy_dict, all_bugs = [], {}, {}, {}

    def prepare(self, data):
        self.key_list, self.project_list, self.status_list, self.components_list, self.timeoriginalestimate_list,\
         self.timespent_list, self.issuetype_list = data.get_sprint_info(self.fixversion)
        self.all_bugs = {'Open': 0, 'In Fix': 0, 'Closed': 0}
        for i in range(len(self.key_list)):
            if self.issuetype_list[i] == 'Bug':
                self.all_bugs[self.status_list[i]] += 1
                self.components_list[i] = self.components_list[i].split(',')
                if len(self.components_list[i]) != 1:
                    for _ in range(1, len(self.components_list[i])):
                        self.components_list.append([self.components_list[i].pop()])
                        self.key_list.append(self.key_list[i])
                        self.project_list.append(self.project_list[i])
                        self.status_list.append(self.status_list[i])
                        self.timeoriginalestimate_list.append(self.timeoriginalestimate_list[i])
                        self.timespent_list.append(self.timespent_list[i])
                        self.issuetype_list.append(self.issuetype_list[i])
        self.domain_list = [None] * len(self.key_list)
        for i in range(len(self.key_list)):
            if self.issuetype_list[i] != 'Bug':
                self.domain_list[i] = get_domain_by_project(self.project_list[i])
                if self.domain_list[i] not in self.accuracy_dict.keys():
                    self.accuracy_dict[self.domain_list[i]] = {'Plan': 0, 'Fact': 0}
                self.accuracy_dict[self.domain_list[i]]['Plan'] += self.timeoriginalestimate_list[i]
                self.accuracy_dict[self.domain_list[i]]['Fact'] += self.timespent_list[i]
            else:
                if self.components_list[i] != [''] and get_domain(*self.components_list[i]) != 'Common':
                    self.domain_list[i] = get_domain(*self.components_list[i])
                else:
                    self.domain_list[i] = 'Empty'
                    # self.domain_list[i] = get_domain_by_project(self.project_list[i])
                if self.domain_list[i] not in self.bugs_dict.keys():
                    self.bugs_dict[self.domain_list[i]] = {'Open': 0, 'In Fix': 0, 'Closed': 0}
                self.bugs_dict[self.domain_list[i]][self.status_list[i]] += 1

    def export_to_plotly(self):
        if len(self.key_list) == 0:
            raise ValueError('There is no issues to show')

        data, statuses = [], [st for st in self.bugs_dict[self.domain_list[0]].keys()]
        base = [0]*len(self.bugs_dict.keys())
        for status in statuses:
            data.append(go.Bar(
                x=list(self.bugs_dict.keys()),
                y=[counts[status] for counts in list(self.bugs_dict.values())],
                xaxis='x3',
                yaxis='y3',
                name=status,
                showlegend=False,
                text=['{}: {} '.format(status, counts[status]) for counts in list(self.bugs_dict.values())],
                textposition='auto',
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        width=1
                    )
                ),
                base=base,
                width=0.8,
                offset=-0.4
            ))
            base = [bs+cnt for bs, cnt in zip(base, [counts[status] for counts in list(self.bugs_dict.values())])]
        timeoriginalestimate, timespent, annotations = [], [], []
        for domain in self.accuracy_dict.keys():
            timeoriginalestimate.append(self.accuracy_dict[domain]['Plan'])
            timespent.append(self.accuracy_dict[domain]['Fact'])
        data.append(go.Bar(
            orientation='h',
            y=list(self.accuracy_dict.keys()),
            x=timeoriginalestimate,
            xaxis='x1',
            yaxis='y1',
            name='Original Estimate',
            showlegend=True,
            text=list(map(lambda x: round(x, 2), timeoriginalestimate)),
            textposition='auto',
            marker=dict(
                line=dict(
                    width=1
                ),
                color='rgb(31,119,180)'
            )
        ))
        data.append(go.Bar(
            orientation='h',
            y=list(self.accuracy_dict.keys()),
            x=timespent,
            xaxis='x1',
            yaxis='y1',
            name='Spent Time',
            showlegend=True,
            text=list(map(lambda x: round(x, 2), timespent)),
            textposition='auto',
            marker=dict(
                line=dict(
                    width=1
                ),
                color='rgb(23,190,207)'
            )
        ))
        for domain in self.accuracy_dict.keys():
            # est_acc = 100 - math.fabs(
            #     100 - (self.accuracy_dict[domain]['Plan'] / self.accuracy_dict[domain]['Fact'] * 100))
            acc_fac = self.accuracy_dict[domain]['Fact'] / self.accuracy_dict[domain]['Plan']
            annotations.append(dict(
                x=self.accuracy_dict[domain]['Fact'] + max(timespent)/5,
                y=domain,
                xref='x1',
                yref='y1',
                showarrow=False,
                text='Accuracy factor:<br>{0:.2f}'.format(acc_fac),
                align='center',
                bordercolor='black',
                borderwidth=2,
                borderpad=4
            ))
        base = 0
        for status in self.all_bugs.keys():
            data.append(go.Bar(
                orientation='h',
                y=['BSSBox'],
                x=[self.all_bugs[status]],
                xaxis='x2',
                yaxis='y2',
                name=status,
                showlegend=False,
                text='{}<br>{}'.format(status, self.all_bugs[status]),
                textposition='auto',
                base=base,
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        width=1
                    )
                ),
                offset=-0.25,
                width=0.5
            ))
            base += self.all_bugs[status]

        axis = dict()
        layout = dict(
            legend=dict(
                orientation='h',
                x=0.695,
                y=1.05
            ),
            title='<b>{0} as of {1}</b>'.format(self.dashboard_name, datetime.now().strftime("%d.%m.%y %H:%M"))
                  + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
            annotations=annotations,
            xaxis1=dict(axis, **dict(domain=[0.55, 1], anchor='y1')),
            yaxis1=dict(axis, **dict(domain=[0, 1], anchor='x1', ticksuffix='  ')),
            xaxis2=dict(axis, **dict(domain=[0.025, 0.5], anchor='y2')),
            yaxis2=dict(axis, **dict(domain=[0, 0.18], anchor='x2', ticksuffix='  ')),
            xaxis3=dict(axis, **dict(domain=[0, 0.5], anchor='y3')),
            yaxis3=dict(axis, **dict(domain=[0.22, 1], anchor='x3', ticksuffix='  '))
        )

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
