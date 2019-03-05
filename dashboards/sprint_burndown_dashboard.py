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
        spent, all_original = float(sum([sp for dt, sp in zip(data_spent['created'], data_spent['spent'])
                                         if dt < datetime.date(2019, 2, 18)])), {}
        fl_spent, fl_all_original = float(sum([sp for dt, sp, fl in
                                          zip(data_spent['created'], data_spent['spent'], data_spent['flagged'])
                                               if dt < datetime.date(2019, 2, 18) and fl is not None])), {}
        original = float(sum([orig for orig, st in zip(data_original['timeoriginalestimate'], data_original['status'])
                              if st not in ('Closed', 'Resolved')]))
        fl_original = float(sum([orig for orig, st, fl in zip(data_original['timeoriginalestimate'],
                                                              data_original['status'], data_original['flagged'])
                                 if st not in ('Closed', 'Resolved') and fl is not None]))

        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] > datetime.date(2019, 2, 17):
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
        for dt in self.all_spent:
            if dt not in all_original.keys():
                all_original[dt] = all_original[max([date for date in all_original.keys() if date < dt])]
        for dt in self.fl_all_spent:
            if dt not in fl_all_original.keys():
                fl_all_original[dt] = fl_all_original[max([date for date in fl_all_original.keys() if date < dt])]
        self.all_remain = {dt: all_original[dt] - self.all_spent[dt] + float(sum(
            [sp for sp, rd, cr in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['created'])
             if rd is not None and rd < dt and cr > datetime.date(2019, 2, 17)])) for dt in self.all_spent.keys()}
        self.fl_all_remain = {dt: fl_all_original[dt] - self.fl_all_spent[dt] + float(sum([sp for sp, rd, fl, cr in
             zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['flagged'], data_spent['created']) if
             fl is not None and rd is not None and rd < dt and cr > datetime.date(2019, 2, 17)]))
                              for dt in self.fl_all_spent.keys()}

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

        start, end1, end2 = datetime.date(2019, 2, 18), datetime.date(2019, 3, 18), datetime.date(2019, 3, 29)
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
            x=[start, end2],
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
            x=[end1, end1],
            y=[0, max(self.all_remain.values()) + 100],
            xaxis='x1',
            yaxis='y1',
            mode='lines',
            line=dict(
                color='rgb(255,153,153)',
                width=2,
                dash='dash'
            ),
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
            x=[start, end1],
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
        ), go.Scatter(
            x=[end1, end1],
            y=[0, max(self.fl_all_remain.values()) + 100],
            xaxis='x2',
            yaxis='y2',
            mode='lines',
            line=dict(
                color='rgb(255,153,153)',
                width=2,
                dash='dash'
            ),
            showlegend=False
        )]

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        annotations = [dict(
            x=0.98,
            y=0.97,
            xref='paper',
            yref='paper',
            text='<b><i>Chart for committed features<br>Deadline 18.03.19</b></i>',
            showarrow=False,
            bordercolor='black',
            borderwidth=1,
            borderpad=3,
            align='center'
        ), dict(
            x=0.98,
            y=0.4,
            xref='paper',
            yref='paper',
            text='<b><i>Chart for all features<br>Deadline 29.03.19</b></i>',
            showarrow=False,
            bordercolor='black',
            borderwidth=1,
            borderpad=3,
            align='center'
        )]

        layout = go.Layout(
            annotations=annotations,
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
                range=[start-datetime.timedelta(days=1), end2+datetime.timedelta(days=1)]
            ),
            yaxis2=dict(
                domain=[0.55, 1],
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
                range=[start - datetime.timedelta(days=1), end2 + datetime.timedelta(days=1)]
            ),
            yaxis1=dict(
                domain=[0, 0.45],
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
