from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
import json
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


class YotaBurndownDashboard(AbstractDashboard):
    auto_open, repository, dashboard_type, citrix_token, local_user = True, None, None, None, None
    all_spent, all_remain = {}, {}
    pp_all_spent, pp_all_remain = {}, {}
    start_date, end_date, pp_end_date = datetime.date(2019, 2, 18), datetime.date(2020, 3, 1), datetime.date(2019, 11, 1)
    readiness, pp_readiness = {'spent': 0, 'bulk estimate': 0, 'features': 0},\
                              {'spent': 0, 'bulk estimate': 0, 'features': 0}

    def multi_prepare(self, data_spent, data_original):
        all_original, spent, original = {}, 0, 0
        pp_all_original, pp_spent, pp_original = {}, 0, 0
        kk, estimates = [], []

        for i in range(len(data_spent['key'])):
            k = set()
            for j in range(len(data_spent['key'])):
                if data_spent['key'][j] == data_spent['key'][i]:
                    k.add(data_spent['component'][j])
            k = len(k)
            kk.append(k)
            if data_spent['created'][i] < self.start_date:
                spent += float(data_spent['spent'][i]) / k
                self.all_spent[self.start_date] = spent
                if data_spent['PilotPriority'][i]:
                    pp_spent += float(data_spent['spent'][i]) / k
                    self.pp_all_spent[self.start_date] = pp_spent
            else:
                spent += float(data_spent['spent'][i]) / k
                self.all_spent[data_spent['created'][i]] = spent
                if data_spent['PilotPriority'][i]:
                    pp_spent += float(data_spent['spent'][i]) / k
                    self.pp_all_spent[data_spent['created'][i]] = pp_spent
            self.readiness['spent'] += float(data_spent['spent'][i]) / k
            if data_spent['PilotPriority'][i]:
                self.pp_readiness['spent'] += float(data_spent['spent'][i]) / k

        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] == 'User Story (L3)':
                d = json.loads(data_original['estimate'][i])
                d = {key: float(val) for key, val in d.items()}
                d['Total'] = sum(list(d.values()))
                estimates.append(d)
                original += float(d['Total']) if d.keys() else 0
                all_original[self.start_date], self.readiness['bulk estimate'] = original, original
                self.readiness['features'] += 1
                if data_original['PilotPriority'][i]:
                    pp_original += float(d['Total']) if d.keys() else 0
                    pp_all_original[self.start_date], self.pp_readiness['bulk estimate'] = pp_original, pp_original
                    self.pp_readiness['features'] += 1
            else:
                if data_original['status'][i] == 'Closed' \
                        and data_original['resolution date'][i] \
                        and data_original['component'][i]:
                    try:
                        cmp_est = [est[data_original['component'][i]] for est, key
                                   in zip(estimates, data_original['key']) if key == data_original['L3'][i]][0]
                        original -= cmp_est
                        all_original[data_original['resolution date'][i]] = original
                        if data_original['PilotPriority'][i]:
                            pp_original -= cmp_est
                            pp_all_original[data_original['resolution date'][i]] = pp_original
                    except KeyError:
                        pass

        for dt in self.all_spent.keys():
            if dt not in all_original.keys():
                all_original[dt] = all_original[max([date for date in all_original.keys() if date < dt])]
        for dt in self.pp_all_spent.keys():
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

        xaxis = [self.start_date]
        while xaxis[-1] != self.end_date:
            xaxis.append(xaxis[-1] + datetime.timedelta(days=1))
        data = [go.Scatter(
            x=list(self.all_spent.keys()),
            y=list(self.all_spent.values()),
            xaxis='x1',
            yaxis='y1',
            name='Spent',
            text=[str(round(sp, 1)) if not i % 10 else '' for i, sp in enumerate(self.all_spent.values())],
            textposition='top left',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(31,119,180)',
                dash='dash'
            ),
            marker=dict(
                size=1,
                color='rgb(31,119,180)',
            )
        ), go.Scatter(
            x=list(self.all_remain.keys()),
            y=list(self.all_remain.values()),
            xaxis='x1',
            yaxis='y1',
            name='Remain',
            text=[str(round(sp, 1)) if not i % 10 else '' for i, sp in enumerate(self.all_remain.values())],
            textposition='top right',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(31,119,180)',
            ),
            marker=dict(
                size=1,
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
                width=2,
                dash='dot'),
            showlegend=False
        ), go.Scatter(
            x=list(self.pp_all_spent.keys()),
            y=list(self.pp_all_spent.values()),
            xaxis='x1',
            yaxis='y1',
            name='Spent (PilotPriority)',
            text=[str(round(sp, 1)) if not i % 10 else '' for i, sp in enumerate(self.pp_all_spent.values())],
            textposition='top left',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(255,127,14)',
                dash='dash'
            ),
            marker=dict(
                size=1,
                color='rgb(255,127,14)',
            )
        ), go.Scatter(
            x=list(self.pp_all_remain.keys()),
            y=list(self.pp_all_remain.values()),
            xaxis='x1',
            yaxis='y1',
            name='Remain (PilotPriority)',
            text=[str(round(sp, 1)) if not i % 10 else '' for i, sp in enumerate(self.pp_all_remain.values())],
            textposition='top right',
            textfont=dict(size=8),
            mode='lines+markers+text',
            line=dict(
                width=2,
                color='rgb(255,127,14)',
            ),
            marker=dict(
                size=1,
                color='rgb(255,127,14)',
            )
        ), go.Scatter(
            x=[self.start_date, self.pp_end_date],
            y=[max(self.pp_all_remain.values()), 0],
            xaxis='x1',
            yaxis='y1',
            name='',
            mode='lines',
            line=dict(
                color='rgba(255,127,14,0.4)',
                width=2,
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
                range=[self.start_date - datetime.timedelta(days=1), self.end_date + datetime.timedelta(days=1)],
                tickvals=xaxis,
                ticktext=[xaxis[i].strftime('%d.%m.%y') if not i % 5 else '' for i in range(len(xaxis))],
                automargin=True,
                linecolor='black',
                gridcolor='rgb(232,232,232)'
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
                range=[0, max(self.all_remain.values()) + 1000],
                automargin=True,
                linecolor='black',
                gridcolor='rgb(232,232,232)'
            ),
            title=dict(
                text=title
                + '<br><b>Total ({} features):</b> spent - {} md, bulk estimate - {} md. <b>Readiness:</b> {}%'
                .format(*map(round, [self.readiness['features'], self.readiness['spent'],
                                     self.readiness['bulk estimate'], self.readiness['spent']
                                     / self.readiness['bulk estimate'] * 100
                                     if self.readiness['spent'] <= self.readiness['bulk estimate'] else 100]))
                + '<br><b>Pilot priority ({} features):</b> spent - {} md, bulk estimate - {} md. <b>Readiness:</b> {}%'
                .format(*map(round, [self.pp_readiness['features'], self.pp_readiness['spent'],
                                     self.pp_readiness['bulk estimate'], self.pp_readiness['spent']
                                     / self.pp_readiness['bulk estimate'] * 100
                                     if self.pp_readiness['spent'] <= self.pp_readiness['bulk estimate'] else 100])),
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
