from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
import json


class YotaBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type = True, None, None, None
    all_spent, all_remain = {}, {}
    start, end = datetime.date(2019, 2, 18), datetime.date(2019, 7, 19)

    def multi_prepare(self, data_spent, data_original):
        all_original, spent, original = {}, 0, 0
        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] < datetime.date(2019, 2, 18):
                spent += float(data_spent['spent'][i])
            else:
                spent += float(data_spent['spent'][i])
                self.all_spent[data_spent['created'][i]] = spent
        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] == 'User Story (L3)':
                d = json.loads(data_original['estimate'][i]) if data_original['estimate'][i] else {}
                data_original['estimate'][i] = {d[cmp]['n']: float(d[cmp]['v']) for cmp in d.keys()
                                                if cmp.isdigit() and d[cmp]['v'] not in ('0', '?')}
                original += float(d['Total']['v']) if d.keys() else 0
                all_original[self.start] = original
            else:
                if data_original['resolution date'][i] and data_original['component'][i]:
                    try:
                        original -= [est[data_original['component'][i]]
                                     for est, key in zip(data_original['estimate'], data_original['key'])
                                     if key == data_original['L3'][i]][0]
                        all_original[data_original['resolution date'][i]] = original
                    except KeyError:
                        pass
        for dt in self.all_spent.keys():
            if dt not in all_original.keys():
                all_original[dt] = all_original[max([date for date in all_original.keys() if date < dt])]
        self.all_remain = {dt: all_original[dt] - self.all_spent[dt] + float(sum(
            [sp for sp, rd in zip(data_spent['spent'], data_spent['resolutiondate']) if rd is not None and rd < dt]))
                           for dt in self.all_spent.keys()}

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

        xaxis = [self.start]
        while xaxis[-1] != self.end:
            xaxis.append(xaxis[-1] + datetime.timedelta(days=1))
        data = [go.Scatter(
            x=list(self.all_spent.keys()),
            y=list(self.all_spent.values()),
            xaxis='x1',
            yaxis='y1',
            name='Spent',
            text=[str(round(sp, 1)) if not i % 4 else '' for i, sp in enumerate(self.all_spent.values())],
            textposition='top left',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(31,119,180)',
            ),
            marker=dict(
                size=5,
                color='rgb(31,119,180)',
            )
        ), go.Scatter(
            x=list(self.all_remain.keys()),
            y=list(self.all_remain.values()),
            xaxis='x1',
            yaxis='y1',
            name='Remain',
            text=[str(round(sp, 1)) if not i % 4 else '' for i, sp in enumerate(self.all_remain.values())],
            textposition='top right',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(255,127,14)',
            ),
            marker=dict(
                size=5,
                color='rgb(255,127,14)',
            )
        ), go.Scatter(
            x=[self.start, self.end],
            y=[max(self.all_remain.values()), 0],
            xaxis='x1',
            yaxis='y1',
            name='',
            mode='lines',
            line=dict(
                color='rgb(200,200,200)',
                width=2,
                dash='dash'),
            showlegend=False
        )]

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            xaxis1=dict(
                domain=[0, 1],
                anchor='y1',
                type='date',
                dtick=86400000,
                title='Date',
                titlefont=dict(
                    size=12
                ),
                tickfont=dict(
                    size=16
                ),
                tickangle=45,
                showline=True,
                range=[self.start - datetime.timedelta(days=1), self.end + datetime.timedelta(days=1)],
                tickvals=xaxis,
                ticktext=[xaxis[i] if not i % 5 else '' for i in range(len(xaxis))],
                automargin=True
            ),
            yaxis1=dict(
                domain=[0, 1],
                anchor='x1',
                showline=True,
                title='Man-days',
                titlefont=dict(
                    size=12
                ),
                tickfont=dict(
                    size=16
                ),
                range=[0, max(self.all_remain.values()) + 100],
                automargin=True
            ),
            title=title + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
            legend=dict(
                orientation='h',
                x=0.453,
                y=1.05
            )
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
