from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain
import datetime
import numpy
import plotly
import plotly.graph_objs as go


def alert_action(days, priorities):
    color = [[]]
    for day, priority in zip(days, priorities):
        if priority == 'Blocker':
            if day > 1:
                color[0].append('rgb(255,204,204)')
            else:
                color[0].append('rgb(255,255,255)')
        elif priority == 'Critical':
            if day > 2:
                color[0].append('rgb(255,204,204)')
            else:
                color[0].append('rgb(255,255,255)')
    return color


class BssboxBugsTrackingDashboard(AbstractDashboard):
    auto_open, repository = True, None
    tracking_data, pivot_data, all_bugs, overdue_data = {}, {}, {}, {}
    jql_all = 'https://jira.billing.ru/issues/?jql=key in ('

    def prepare(self, data):
        self.tracking_data = {key: [] for key in list(data.keys()) if key != 'Resolved'}
        self.all_bugs['BSSBox'] = {'On time': 0, 'Overdue': 0}
        preparing_data = {key: [] for key in data.keys()}
        for i in range(len(data['Key'])):
            if get_domain(data['Domain'][i]) != 'Others':
                for key in data.keys():
                    preparing_data[key].append(data[key][i])
        data = preparing_data
        for i in range(len(data['Key'])):
            data['Domain'][i] = get_domain(data['Domain'][i]) if data['Domain'][i] is not None else 'W/o components'
            data['Days in progress'][i] =\
                int(numpy.busday_count(data['Days in progress'][i], datetime.datetime.now().date())+1)\
                if data['Status'][i] not in ('Closed', 'Resolved')\
                else int(numpy.busday_count(data['Days in progress'][i], data['Resolved'][i])+1)
            if data['Status'][i] not in ('Closed', 'Resolved'):
                for key in self.tracking_data.keys():
                    self.tracking_data[key].append(data[key][i])
            else:
                if data['Domain'][i] not in self.pivot_data.keys():
                    self.pivot_data[data['Domain'][i]] = {'On time': 0, 'Overdue': 0}
                    self.overdue_data[data['Domain'][i]] = 'https://jira.billing.ru/issues/?jql=key in ('
                if data['Priority'][i] == 'Blocker':
                    if data['Days in progress'][i] > 1:
                        self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                        self.all_bugs['BSSBox']['Overdue'] += 1
                        self.overdue_data[data['Domain'][i]] += '{}, '.format(data['Key'][i])
                        self.jql_all += '{}, '.format(data['Key'][i])
                    else:
                        self.pivot_data[data['Domain'][i]]['On time'] += 1
                        self.all_bugs['BSSBox']['On time'] += 1
                elif data['Priority'][i] == 'Critical':
                    if data['Days in progress'][i] > 2:
                        self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                        self.all_bugs['BSSBox']['Overdue'] += 1
                        self.overdue_data[data['Domain'][i]] += '{}, '.format(data['Key'][i])
                        self.jql_all += '{}, '.format(data['Key'][i])
                    else:
                        self.pivot_data[data['Domain'][i]]['On time'] += 1
                        self.all_bugs['BSSBox']['On time'] += 1
        self.overdue_data = {domain: '{})'.format(jql[:-2]) for domain, jql in self.overdue_data.items()}
        self.jql_all = '{})'.format(self.jql_all[:-2])

    def export_to_plotly(self):
        if len(self.tracking_data['Key']) == 0:
            raise ValueError('There is no issues to show')

        header_values = [['<b>{}</b>'.format(head)] for head in self.tracking_data.keys()] + [['<b>Deadline</b>']]
        cells_values = [value if key != 'Key' else list(
            map(lambda el: '<a href="https://jira.billing.ru/browse/{0}">{0}</a>'.format(el), value)) for key, value in
                        self.tracking_data.items()] + [[datetime.datetime.now().date() - datetime.timedelta(
                            days=days-3) if pr == 'Critical' else datetime.datetime.now().date()
                            - datetime.timedelta(days=days-2) for days, pr
                            in zip(self.tracking_data['Days in progress'], self.tracking_data['Priority'])]]
        data = [go.Table(
            domain=dict(
                x=[0, 0.72],
                y=[0, 1]
            ),
            columnorder=[1, 2, 3, 4, 5, 6, 7, 8],
            columnwidth=[3, 11, 3, 2, 2, 2, 2, 2],
            header=dict(
                values=header_values,
                fill=dict(color=['grey']),
                font=dict(color='white'),
                line=dict(width=2),
                align='center'
            ),
            cells=dict(
                values=cells_values,
                align=['center', 'left', 'center', 'center', 'center', 'center', 'center'],
                fill=dict(color=alert_action(days=self.tracking_data['Days in progress'],
                                             priorities=self.tracking_data['Priority'])),
                height=25,
                line=dict(width=2)
            )
        ), go.Bar(
            orientation='h',
            y=list(self.pivot_data.keys()),
            x=[value['On time'] for value in self.pivot_data.values()],
            xaxis='x1',
            yaxis='y1',
            name='On time',
            showlegend=False,
            text=list(map(lambda el: 'On time: <b>{}</b> '.format(el),
                          [value['On time'] for value in self.pivot_data.values()])),
            textposition='inside',
            marker=dict(
                color='rgb(232,232,232)',
            )
        ), go.Bar(
            orientation='h',
            y=list(self.pivot_data.keys()),
            x=[value['Overdue'] for value in self.pivot_data.values()],
            xaxis='x1',
            yaxis='y1',
            name='Overdue',
            showlegend=False,
            text=list(map(lambda el, link: '<a href = "{}">Overdue: <b>{}</b> </a>'.format(link, el),
                          [value['Overdue'] for value in self.pivot_data.values()], self.overdue_data.values())),
            textposition='inside',
            marker=dict(
                color='rgb(255,204,204)'
            )
        ), go.Bar(
            orientation='h',
            y=list(self.all_bugs.keys()),
            x=[value['On time'] for value in self.all_bugs.values()],
            xaxis='x2',
            yaxis='y2',
            name='On time',
            showlegend=False,
            text=list(map(lambda el: 'On time: <b>{}</b> '.format(el),
                          [value['On time'] for value in self.all_bugs.values()])),
            textposition='inside',
            marker=dict(
                color='rgb(232,232,232)',
            )
        ), go.Bar(
            orientation='h',
            y=list(self.all_bugs.keys()),
            x=[value['Overdue'] for value in self.all_bugs.values()],
            xaxis='x2',
            yaxis='y2',
            name='Overdue',
            showlegend=False,
            text=list(map(lambda el: '<a href = "{}">Overdue: <b>{}</b> </a>'.format(self.jql_all, el),
                          [value['Overdue'] for value in self.all_bugs.values()])),
            textposition='inside',
            marker=dict(
                color='rgb(255,204,204)'
            )
        )]

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        axis = dict()
        layout = go.Layout(
            title='<b>{} ({})</b>'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                  + ('<sup> in cloud</sup>' if self.repository == 'online' else '')
                  + '<br><i>SLA: Blockers - 1 day, Criticals - 2 days</i>',
            font=dict(family='Oswald, sans-serif', size=12),
            shapes=[dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0.73,
                y0=0.17,
                x1=1,
                y1=1,
                line=dict(
                    color='rgb(0,0,0)',
                    width=1
                )
            ), dict(
                type='rect',
                xref='paper',
                yref='paper',
                x0=0.73,
                y0=0,
                x1=1,
                y1=0.15,
                line=dict(
                    color='rgb(0,0,0)',
                    width=1
                )
            )],
            xaxis1=dict(axis, **dict(domain=[0.77, 0.99], anchor='y1')),
            yaxis1=dict(axis, **dict(domain=[0.2, 0.99], anchor='x1', ticksuffix='  ')),
            xaxis2=dict(axis, **dict(domain=[0.77, 0.99], anchor='y2')),
            yaxis2=dict(axis, **dict(domain=[0.03, 0.14], anchor='x2', ticksuffix='  ')),
            barmode='stack'
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username='Rnd-Rnd', api_key='GFSxsbDP8rOiakf0rs8U')
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
