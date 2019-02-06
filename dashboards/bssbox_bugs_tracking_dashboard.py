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
    tracking_data, pivot_data = {}, {}

    def prepare(self, data):
        self.tracking_data = {key: [] for key in list(data.keys()) if key != 'Resolved'}
        for i in range(len(data['Key'])):
            print('{}: {}'.format(data['Domain'][i], get_domain(data['Domain'][i])))
            data['Domain'][i] = get_domain(data['Domain'][i]) if data['Domain'][i] is not None else 'Indefinite'
            data['Days on fix'][i] = int(numpy.busday_count(data['Days on fix'][i], datetime.datetime.now().date())+1)\
                if data['Status'][i] not in ('Closed', 'Resolved')\
                else int(numpy.busday_count(data['Days on fix'][i], data['Resolved'][i])+1)
            if data['Status'][i] not in ('Closed', 'Resolved'):
                for key in self.tracking_data.keys():
                    self.tracking_data[key].append(data[key][i])
            else:
                if data['Domain'][i] not in self.pivot_data.keys():
                    self.pivot_data[data['Domain'][i]] = {'Punctually': 0, 'Overdue': 0}
                if data['Priority'][i] == 'Blocker':
                    if data['Days on fix'][i] > 1:
                        self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                    else:
                        self.pivot_data[data['Domain'][i]]['Punctually'] += 1
                elif data['Priority'][i] == 'Critical':
                    if data['Days on fix'][i] > 2:
                        self.pivot_data[data['Domain'][i]]['Overdue'] += 1
                    else:
                        self.pivot_data[data['Domain'][i]]['Punctually'] += 1
        print(self.pivot_data)

    def export_to_plotly(self):
        if len(self.tracking_data['Key']) == 0:
            raise ValueError('There is no issues to show')

        plotly.tools.set_credentials_file(username='Rnd-Rnd', api_key='GFSxsbDP8rOiakf0rs8U')

        header_values = [['<b>{}</b>'.format(head)] for head in self.tracking_data.keys()]
        cells_values = [value for value in self.tracking_data.values()]
        data = [go.Table(
            domain=dict(
                x=[0, 1],
                y=[0.3, 1]
            ),
            columnorder=[1, 2, 3, 4, 5, 6, 7],
            columnwidth=[2, 14, 2, 2, 2, 2, 2],
            header=dict(
                values=header_values,
                fill=dict(color=['grey']),
                font=dict(color='white')
            ),
            cells=dict(
                values=cells_values,
                align=['center', 'left', 'center', 'center', 'center', 'center', 'center'],
                fill=dict(color=alert_action(days=self.tracking_data['Days on fix'],
                                             priorities=self.tracking_data['Priority'])),
                height=25
            )
        )]

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            title=title,
            font=dict(family='Oswald, sans-serif', size=12)
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
