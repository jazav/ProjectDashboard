from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime


class YotaBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type = True, None, None, None
    all_spent, all_remain = {}, {}

    def multi_prepare(self, data_spent, data_original):
        all_original, fl_all_original = {}, {}
        spent, original = 0, 0
        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] < datetime.date(2019, 2, 18):
                spent += float(data_spent['spent'][i])
        for i in range(len(data_original['key'])):
            if data_original['status'][i] not in ('Closed', 'Resolved'):
                original += float(data_original['timeoriginalestimate'][i])
        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] > datetime.date(2019, 2, 17):
                spent += float(data_spent['spent'][i])
                self.all_spent[data_spent['created'][i]] = spent
        for i in range(len(data_original['key'])):
            if data_original['resolutiondate'][i] is not None:
                original += float(data_original['timeoriginalestimate'][i])
                all_original[data_original['resolutiondate'][i]] = original
        for dt in self.all_spent:
            if dt not in all_original.keys():
                try:
                    all_original[dt] = all_original[max([date for date in all_original.keys() if date < dt])]
                except ValueError:
                    all_original[dt] = all_original[list(all_original.keys())[-1]]
        self.all_remain = {dt: all_original[dt] - self.all_spent[dt] + float(sum(
            [sp for sp, rd in zip(data_spent['spent'], data_spent['resolutiondate']) if rd is not None and rd < dt]))
                           for dt in self.all_spent.keys()}

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

        start, end = datetime.date(2019, 2, 18), datetime.date(2019, 7, 18)
        data = [go.Scatter(
            x=list(self.all_spent.keys()),
            y=list(self.all_spent.values()),
            xaxis='x1',
            yaxis='y1',
            name='Spent',
            text=[str(round(sp, 1)) for sp in self.all_spent.values()],
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
            text=[str(round(sp, 1)) for sp in self.all_remain.values()],
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
            x=[start, end],
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
                range=[start - datetime.timedelta(days=1), end + datetime.timedelta(days=1)],
                showticklabels=False
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
                range=[0, max(self.all_remain.values()) + 100]
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
