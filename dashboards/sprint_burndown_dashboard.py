from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


class SprintBurndownDashboard(AbstractDashboard):
    auto_open, repository, dashboard_type, citrix_token, local_user, start_date, end_date \
        = True, None, None, None, None, None, None
    all_spent, all_remain = {}, {}
    pp_all_spent, pp_all_remain = {}, {}
    readiness, pp_readiness = {'spent': 0, 'original estimate': 0, 'features': 0},\
                              {'spent': 0, 'original estimate': 0, 'features': 0}

    def multi_prepare(self, data_spent, data_original):
        all_original, spent = {}, 0
        pp_all_original, pp_spent = {}, 0
        kk = []

        for i in range(len(data_spent['key'])):
            k = set()
            for j in range(len(data_spent['key'])):
                if data_spent['key'][j] == data_spent['key'][i]:
                    k.add(data_spent['component'][j])
            k = len(k)
            kk.append(k)
            if data_spent['created'][i] < self.start_date:
                spent += float(data_spent['spent'][i]) / k
                if data_spent['PilotPriority'][i]:
                    pp_spent += float(data_spent['spent'][i]) / k
            else:
                spent += float(data_spent['spent'][i]) / k
                self.all_spent[data_spent['created'][i]] = spent
                if data_spent['PilotPriority'][i]:
                    pp_spent += float(data_spent['spent'][i]) / k
                    self.pp_all_spent[data_spent['created'][i]] = pp_spent
            self.readiness['spent'] += float(data_spent['spent'][i]) / k
            if data_spent['PilotPriority'][i]:
                self.pp_readiness['spent'] += float(data_spent['spent'][i]) / k

        original, pp_original = 0, 0
        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] != 'User Story (L3)':
                k = data_original['key'].count(data_original['key'][i])
                original += float(data_original['timeoriginalestimate'][i]) / k
                all_original[self.start_date] = original
                oe = float(data_original['timespent'][i]) / k \
                    if data_original['timespent'][i] > data_original['timeoriginalestimate'][i] \
                    or data_original['status'][i] in ('Closed', 'Resolved', 'Done') \
                    else float(data_original['timeoriginalestimate'][i]) / k
                self.readiness['original estimate'] += oe
                if data_original['PilotPriority'][i]:
                    pp_original += float(data_original['timeoriginalestimate'][i]) / k
                    pp_all_original[self.start_date] = pp_original
                    self.pp_readiness['original estimate'] += oe
        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] != 'User Story (L3)':
                k = data_original['key'].count(data_original['key'][i])
                if data_original['status'][i] in ('Closed', 'Resolved', 'Done') and data_original['resolutiondate'][i]:
                    original -= float(data_original['timeoriginalestimate'][i]) / k
                    all_original[data_original['resolutiondate'][i]] = original
                    if data_original['PilotPriority'][i]:
                        pp_original -= float(data_original['timeoriginalestimate'][i]) / k
                        pp_all_original[data_original['resolutiondate'][i]] = pp_original
            else:
                self.readiness['features'] += 1
                if data_original['PilotPriority'][i]:
                    self.pp_readiness['features'] += 1

        for dt in self.all_spent:
            if dt not in all_original.keys():
                all_original[dt] = all_original[max([date for date in all_original.keys() if date < dt])]
        for dt in self.pp_all_spent:
            if dt not in pp_all_original.keys():
                pp_all_original[dt] = pp_all_original[max([date for date in pp_all_original.keys() if date < dt])]

        for dt in self.all_spent.keys():
            sp = 0
            for i, k in zip(range(len(data_spent['key'])), kk):
                if data_spent['status'][i] in ('Closed', 'Resolved', 'Done') \
                        and data_spent['resolutiondate'][i] and data_spent['resolutiondate'][i] <= dt:
                    sp += float(data_spent['spent'][i]) / k
            self.all_remain[dt] = all_original[dt] - (self.all_spent[dt] - sp)
        for dt in self.pp_all_spent.keys():
            sp = 0
            for i, k in zip(range(len(data_spent['key'])), kk):
                if data_spent['PilotPriority'][i] and data_spent['status'][i] in ('Closed', 'Resolved', 'Done') \
                        and data_spent['resolutiondate'][i] and data_spent['resolutiondate'][i] <= dt:
                    sp += float(data_spent['spent'][i]) / k
            self.pp_all_remain[dt] = pp_all_original[dt] - (self.pp_all_spent[dt] - sp)

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

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
                dash='dash'
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
                color='rgb(31,119,180)',
            ),
            marker=dict(
                size=5,
                color='rgb(31,119,180)',
            )
        ), go.Scatter(
            x=[self.start_date, self.end_date],
            y=[max(self.all_remain.values()), 0],
            xaxis='x1',
            yaxis='y1',
            name='',
            mode='lines',
            line=dict(
                color='rgba(31,119,180,0.4)',
                width=1,
                dash='dot'),
            showlegend=False
        ), go.Scatter(
            x=list(self.pp_all_spent.keys()),
            y=list(self.pp_all_spent.values()),
            xaxis='x1',
            yaxis='y1',
            name='Spent (PilotPriority)',
            text=[str(round(sp, 1)) for sp in self.pp_all_spent.values()],
            textposition='top left',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(255,127,14)',
                dash='dash'
            ),
            marker=dict(
                size=5,
                color='rgb(255,127,14)',
            )
        ), go.Scatter(
            x=list(self.pp_all_remain.keys()),
            y=list(self.pp_all_remain.values()),
            xaxis='x1',
            yaxis='y1',
            name='Remain (PilotPriority)',
            text=[str(round(sp, 1)) for sp in self.pp_all_remain.values()],
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
            x=[self.start_date, self.end_date],
            y=[max(self.pp_all_remain.values()), 0],
            xaxis='x1',
            yaxis='y1',
            name='',
            mode='lines',
            line=dict(
                color='rgba(255,127,14,0.4)',
                width=1,
                dash='dot'),
            showlegend=False
        )]

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            hovermode='closest',
            plot_bgcolor='white',
            xaxis1=dict(
                linecolor='black',
                gridcolor='rgb(232,232,232)',
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
                range=[self.start_date - datetime.timedelta(days=1), self.end_date + datetime.timedelta(days=1)]
            ),
            yaxis1=dict(
                linecolor='black',
                gridcolor='rgb(232,232,232)',
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
            title=dict(
                text=title
                + '<br><b>Total ({} features):</b> spent - {} md, original estimate - {} md. <b>Readiness:</b> {}%'
                .format(*map(round, [self.readiness['features'], self.readiness['spent'],
                                     self.readiness['original estimate'], self.readiness['spent']
                                     / self.readiness['original estimate'] * 100
                                     if self.readiness['spent'] <= self.readiness['original estimate'] else 100]))
                + '<br><b>Pilot priority ({} features):</b> spent - {} md, original estimate - {} md. <b>Readiness:</b> {}%'
                .format(*map(round, [self.pp_readiness['features'], self.pp_readiness['spent'],
                                     self.pp_readiness['original estimate'], self.pp_readiness['spent']
                                     / self.pp_readiness['original estimate'] * 100
                                     if self.pp_readiness['spent'] <= self.pp_readiness['original estimate'] else 100])),
                x=0.5
            ),
            legend=dict(
                orientation='h'
            )
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
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
