from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
import math


class SprintBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    all_spent, all_remain = {}, {}
    fl_all_spent, fl_all_remain = {}, {}

    def multi_prepare(self, data_spent, data_original):
        spent, all_original = 0, {}
        fl_spent, fl_all_original = 0, {}
        original = float(sum([orig for orig, st in zip(data_original['timeoriginalestimate'], data_original['status'])
                              if st not in ('Closed', 'Resolved')]))
        fl_original = float(sum([orig for orig, st, fl in zip(data_original['timeoriginalestimate'],
                                                              data_original['status'], data_original['flagged'])
                                 if st not in ('Closed', 'Resolved') and fl is not None]))
        for i in range(len(data_spent['key'])):
            if data_spent['flagged'][i] is not None:
                fl_spent += float(data_spent['spent'][i])
                self.fl_all_spent[data_spent['created'][i]] = fl_spent
            spent += float(data_spent['spent'][i])
            self.all_spent[data_spent['created'][i]] = spent
        for resdate, origest, flagged in zip(data_original['resolutiondate'], data_original['timeoriginalestimate'],
                                             data_original['flagged']):
            if resdate is not None:
                if flagged is not None:
                    fl_original += float(origest)
                    fl_all_original[resdate] = fl_original
                original += float(origest)
                all_original[resdate] = original
        self.all_remain = {dt: all_original.get(dt, all_original.get(dt - datetime.timedelta(days=1),all_original.get(dt - datetime.timedelta(days=2))))
                           - self.all_spent[dt] + float(sum([sp for sp, rd in zip(data_spent['spent'], data_spent['resolutiondate'])
                                                             if rd is not None and rd < dt])) for dt in self.all_spent.keys()}
        self.fl_all_remain = {dt: fl_all_original.get(dt, fl_all_original.get(dt - datetime.timedelta(days=1), fl_all_original.get(dt - datetime.timedelta(days=2))))
                              - self.fl_all_spent[dt] + float(sum([sp for sp, rd, fl in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['flagged'])
                                                                   if fl is not None and rd is not None and rd < dt])) for dt in self.fl_all_spent.keys()}

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

        start, end = datetime.date(2019, 2, 18), datetime.date(2019, 3, 29)
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
        ), go.Scatter(
            x=list(self.fl_all_spent.keys()),
            y=list(self.fl_all_spent.values()),
            xaxis='x2',
            yaxis='y2',
            name='Spent',
            text=[str(round(sp, 1)) for sp in self.fl_all_spent.values()],
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
            ),
            showlegend=False
        ), go.Scatter(
            x=list(self.fl_all_remain.keys()),
            y=list(self.fl_all_remain.values()),
            xaxis='x2',
            yaxis='y2',
            name='Remain',
            text=[str(round(sp, 1)) for sp in self.fl_all_remain.values()],
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
            ),
            showlegend=False
        ), go.Scatter(
            x=[start, end-datetime.timedelta(days=11)],
            y=[max(self.fl_all_remain.values()), 0],
            xaxis='x2',
            yaxis='y2',
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
                range=[start-datetime.timedelta(days=1), end+datetime.timedelta(days=1)]
            ),
            yaxis1=dict(
                domain=[0.55, 1],
                anchor='x1',
                showline=True,
                title='Man-hour',
                titlefont=dict(
                    size=12
                ),
                tickfont=dict(
                    size=16
                ),
                range=[0, max(self.all_remain.values()) + 100]
            ),
            xaxis2=dict(
                domain=[0, 1],
                anchor='y2',
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
                range=[start - datetime.timedelta(days=1), end - datetime.timedelta(days=10)]
            ),
            yaxis2=dict(
                domain=[0, 0.45],
                anchor='x2',
                showline=True,
                title='Man-days',
                titlefont=dict(
                    size=12
                ),
                tickfont=dict(
                    size=16
                ),
                range=[0, max(self.fl_all_remain.values()) + 100]
            ),
            title=title,
            legend=dict(
                orientation='h',
                x=0.455,
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
