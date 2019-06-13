from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


class SprintBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type, citrix_token, local_user = True, None, None, None, None, None
    all_spent, all_remain = {}, {}
    fl_all_spent, fl_all_remain = {}, {}

    def multi_prepare(self, data_spent, data_original):
        all_original, fl_all_original = {}, {}
        spent, fl_spent = 0, 0
        original, fl_original = 0, 0
        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] < datetime.date(2019, 5, 21):
                k = set()
                for j in range(len(data_spent['key'])):
                    if data_spent['key'][j] == data_spent['key'][i]:
                        k.add(data_spent['component'][j])
                if data_spent['flagged'][i] is not None:
                    fl_spent += float(data_spent['spent'][i]) / len(k)
                spent += float(data_spent['spent'][i]) / len(k)
        for i in range(len(data_original['key'])):
            if data_original['status'][i] not in ('Closed', 'Resolved'):
                k = set()
                for j in range(len(data_original['key'])):
                    if data_original['key'][j] == data_original['key'][i]:
                        k.add(data_original['component'][j])
                if data_original['flagged'][i] is not None:
                    fl_original += float(data_original['timeoriginalestimate'][i]) / len(k)
                original += float(data_original['timeoriginalestimate'][i]) / len(k)
        for i in range(len(data_spent['key'])):
            if data_spent['created'][i] > datetime.date(2019, 5, 20):
                k = set()
                for j in range(len(data_spent['key'])):
                    if data_spent['key'][j] == data_spent['key'][i]:
                        k.add(data_spent['component'][j])
                if data_spent['flagged'][i] is not None:
                    fl_spent += float(data_spent['spent'][i]) / len(k)
                    self.fl_all_spent[data_spent['created'][i]] = fl_spent
                spent += float(data_spent['spent'][i]) / len(k)
                self.all_spent[data_spent['created'][i]] = spent
        for i in range(len(data_original['key'])):
            if data_original['resolutiondate'][i] is not None:
                k = set()
                for j in range(len(data_original['key'])):
                    if data_original['key'][j] == data_original['key'][i]:
                        k.add(data_original['component'][j])
                if data_original['flagged'][i] is not None:
                    fl_original += float(data_original['timeoriginalestimate'][i]) / len(k)
                    fl_all_original[data_original['resolutiondate'][i]] = fl_original
                original += float(data_original['timeoriginalestimate'][i]) / len(k)
                all_original[data_original['resolutiondate'][i]] = original
        for dt in self.all_spent:
            if dt not in all_original.keys():
                all_original[dt] = all_original[max([date for date in all_original.keys() if date < dt])]
        for dt in self.fl_all_spent:
            if dt not in fl_all_original.keys():
                try:
                    fl_all_original[dt] = fl_all_original[max([date for date in fl_all_original.keys() if date < dt])]
                except ValueError:
                    fl_all_original[dt] = fl_all_original[list(fl_all_original.keys())[-1]]
        self.all_remain = {dt: all_original[dt] - self.all_spent[dt] + float(sum(
            [sp for sp, rd in zip(data_spent['spent'], data_spent['resolutiondate']) if rd is not None and rd < dt]))
                           for dt in self.all_spent.keys()}
        self.fl_all_remain = {dt: fl_all_original[dt] - self.fl_all_spent[dt] + float(sum(
            [sp for sp, rd, fl in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['flagged']) if
             fl is not None and rd is not None and rd < dt])) for dt in self.fl_all_spent.keys()}

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

        start, end1, end2 = datetime.date(2019, 5, 20), datetime.date(2019, 7, 2), datetime.date(2019, 7, 2)
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
        )]

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        annotations = [dict(
            x=0.98,
            y=0.8,
            xref='paper',
            yref='paper',
            text='<b><i>Chart for committed features<br>Deadline 02.07.19</b></i>',
            showarrow=False,
            bordercolor='black',
            borderwidth=1,
            borderpad=3,
            align='center'
        ), dict(
            x=0.98,
            y=0.2,
            xref='paper',
            yref='paper',
            text='<b><i>Chart for all features<br>Deadline 02.07.19</b></i>',
            showarrow=False,
            bordercolor='black',
            borderwidth=1,
            borderpad=3,
            align='center'
        )]

        layout = go.Layout(
            hovermode='closest',
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
                range=[start - datetime.timedelta(days=1), end2 + datetime.timedelta(days=1)]
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
                range=[start - datetime.timedelta(days=1), end1 + datetime.timedelta(days=1)]
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
