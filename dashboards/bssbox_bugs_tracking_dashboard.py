from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain
import datetime
import numpy
import plotly
import plotly.graph_objs as go
import math


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


def domain_position(row, col, rows):
    delta = 0.02
    length = ((0.99-(rows-1)*delta)/rows)
    start, end, y_pos = 0.99-length, 0.99, {}
    for i in range(1, rows+1):
        y_pos[i] = [start, end]
        end = start - delta
        start = end - length
    x_pos = {
        1: [0.76, 0.87],
        2: [0.88, 0.99]
    }
    return dict(
        x=x_pos[col],
        y=y_pos[row]
    )


class BssboxBugsTrackingDashboard(AbstractDashboard):
    auto_open, repository = True, None
    tracking_data, pivot_data, all_bugs = {}, {}, {}

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
            data['Days on fix'][i] = int(numpy.busday_count(data['Days on fix'][i], datetime.datetime.now().date())+1)\
                if data['Status'][i] not in ('Closed', 'Resolved')\
                else int(numpy.busday_count(data['Days on fix'][i], data['Resolved'][i])+1)
            if data['Status'][i] not in ('Closed', 'Resolved'):
                for key in self.tracking_data.keys():
                    self.tracking_data[key].append(data[key][i])
            else:
                if data['Domain'][i] not in self.pivot_data.keys():
                    self.pivot_data[data['Domain'][i]] = {'On time': 0, 'Overdue': 0}
                if data['Priority'][i] == 'Blocker':
                    if data['Days on fix'][i] > 1:
                        self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                        self.all_bugs['BSSBox']['Overdue'] += 1
                    else:
                        self.pivot_data[data['Domain'][i]]['On time'] += 1
                        self.all_bugs['BSSBox']['On time'] += 1
                elif data['Priority'][i] == 'Critical':
                    if data['Days on fix'][i] > 2:
                        self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                        self.all_bugs['BSSBox']['Overdue'] += 1
                    else:
                        self.pivot_data[data['Domain'][i]]['On time'] += 1
                        self.all_bugs['BSSBox']['On time'] += 1

    def export_to_plotly(self):
        if len(self.tracking_data['Key']) == 0:
            raise ValueError('There is no issues to show')

        header_values = [['<b>{}</b>'.format(head)] for head in self.tracking_data.keys()]
        cells_values = [value if key != 'Key'
                        else list(map(lambda el: '<a href="https://jira.billing.ru/browse/{0}">{0}</a>'.format(el),
                                      value)) for key, value in self.tracking_data.items()]
        data = [go.Table(
            domain=dict(
                x=[0, 0.72],
                y=[0, 1]
            ),
            columnorder=[1, 2, 3, 4, 5, 6, 7],
            columnwidth=[3, 12, 3, 2, 2, 2, 2],
            header=dict(
                values=header_values,
                fill=dict(color=['grey']),
                font=dict(color='white'),
                line=dict(width=2)
            ),
            cells=dict(
                values=cells_values,
                align=['center', 'left', 'center', 'center', 'center', 'center', 'center'],
                fill=dict(color=alert_action(days=self.tracking_data['Days on fix'],
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
            textposition='auto',
            marker=dict(
                color='rgb(232,232,232)'
            )
        ), go.Bar(
            orientation='h',
            y=list(self.pivot_data.keys()),
            x=[value['Overdue'] for value in self.pivot_data.values()],
            xaxis='x1',
            yaxis='y1',
            name='Overdue',
            showlegend=False,
            text=list(map(lambda el: '<a href = "https://jira.billing.ru/">Overdue: <b>{}</b> </a>'.format(el),
                          [value['Overdue'] for value in self.pivot_data.values()])),
            textposition='auto',
            marker=dict(
                color='rgb(255,204,204)'
            )
        )]
        # rows = math.ceil(len(self.pivot_data.keys()) / 2)
        # for domain, i in zip(self.pivot_data.keys(), range(len(self.pivot_data.keys()))):
        #     row, col = int((i % rows) + 1), int((i // rows) + 1)
        #     data.append(go.Pie(
        #         labels=list(self.pivot_data[domain].keys()),
        #         values=list(self.pivot_data[domain].values()),
        #         hoverinfo='label+percent',
        #         textinfo='label+value',
        #         textposition='inside',
        #         hole=0.4,
        #         domain=domain_position(row, col, rows),
        #         marker=dict(
        #             colors=['rgb(232,232,232)', 'rgb(255,204,204)'],
        #             line=dict(width=1)
        #         ),
        #         showlegend=False,
        #         title=domain,
        #         titleposition='middle center'
        #     ))

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        axis = dict()
        layout = go.Layout(
            title='<b>{} ({})</b><br><i>SLA: Blockers - 2 days, Criticals - 1 day</i>'
            .format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M")),
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
                y1=0.16,
                line=dict(
                    color='rgb(0,0,0)',
                    width=1
                )
            )],
            xaxis1=dict(axis, **dict(domain=[0.77, 0.99], anchor='y1')),
            yaxis1=dict(axis, **dict(domain=[0.2, 0.99], anchor='x1', ticksuffix='  ')),
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
