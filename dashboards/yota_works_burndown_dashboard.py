from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
import math
from plotly import subplots
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time
import json


class YotaWorksBurndownDashboard(AbstractDashboard):
    auto_open, repository, citrix_token, local_user, labels = True, None, None, None, None
    all_spent, all_remain = {}, {}
    start_date = datetime.date(2019, 2, 18)
    end_date = {'PilotPriority': datetime.date(2019, 11, 1), 'Core': datetime.date(2020, 3, 1),
                'Custom': datetime.date(2020, 3, 1), 'Config': datetime.date(2020, 3, 1)}
    estimates = []

    def multi_prepare(self, data_spent, data_original):
        all_original, spent, original, kk, estimates = {}, {}, {}, [], []

        for label in self.labels:
            self.all_spent[label], all_original[label], spent[label], original[label] = {}, {}, 0, 0
        for i in range(len(data_spent['key'])):
            k = set()
            for j in range(len(data_spent['key'])):
                if data_spent['key'][j] == data_spent['key'][i]:
                    k.add(data_spent['component'][j])
            k = len(k)
            kk.append(k)
            if data_spent['created'][i] < self.start_date:
                for label in self.labels:
                    if data_spent[label][i]:
                        spent[label] += float(data_spent['spent'][i]) / k
                        self.all_spent[label][self.start_date] = spent[label]
            else:
                for label in self.labels:
                    if data_spent[label][i]:
                        spent[label] += float(data_spent['spent'][i]) / k
                        self.all_spent[label][data_spent['created'][i]] = spent[label]

        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] == 'User Story (L3)':
                d = json.loads(data_original['estimate'][i])
                d = {key: float(val) for key, val in d.items()}
                d['Total'] = sum(list(d.values()))
                estimates.append(d)
                for label in self.labels:
                    if data_original[label][i]:
                        original[label] += float(d['Total']) if d.keys() else 0
                        all_original[label][self.start_date] = original[label]
            else:
                for label in self.labels:
                    if data_original[label][i]:
                        if data_original['status'][i] == 'Closed' \
                                and data_original['resolution date'][i] \
                                and data_original['component'][i]:
                            try:
                                cmp_est = [est[data_original['component'][i]] for est, key
                                           in zip(estimates, data_original['key']) if key == data_original['L3'][i]][0]
                                original[label] -= cmp_est
                                all_original[label][data_original['resolution date'][i]] = original[label]
                            except KeyError:
                                pass

        for label, spents in self.all_spent.items():
            if label not in all_original.keys():
                all_original[label] = {dt: 0 for dt in spents.keys()}
            for dt in spents.keys():
                if dt not in all_original[label].keys():
                    all_original[label][dt] = all_original[label][max([date for date in all_original[label].keys() if date < dt])]

        for label in self.all_spent.keys():
            self.all_remain[label] = {}
            for dt in self.all_spent[label].keys():
                sp = 0
                for i, k in zip(range(len(data_spent['key'])), kk):
                    if data_spent[label][i] \
                            and data_spent['status'][i] in ('Closed', 'Resolved', 'Done') \
                            and data_spent['resolutiondate'][i] \
                            and data_spent['resolutiondate'][i] <= dt:
                        sp += float(data_spent['spent'][i]) / k
                self.all_remain[label][dt] = all_original[label][dt] - (self.all_spent[label][dt] - sp)

    def export_to_plotly(self):
        trace_dict, xticks = {label: [] for label in self.all_spent.keys()}, {}
        for label in self.all_spent.keys():
            xticks[label] = [self.start_date]
            while xticks[label][-1] != self.end_date[label]:
                xticks[label].append(xticks[label][-1] + datetime.timedelta(days=1))
            trace_dict[label].append(go.Scatter(
                x=list(self.all_spent[label].keys()),
                y=list(self.all_spent[label].values()),
                name='Spent',
                mode='lines+markers',
                line=dict(
                    width=2,
                    color='rgb(31,119,180)',
                ),
                marker=dict(
                    size=1,
                    color='rgb(31,119,180)',
                ),
                showlegend=True if label == list(self.all_spent.keys())[0] else False
            ))
            trace_dict[label].append(go.Scatter(
                x=list(self.all_remain[label].keys()),
                y=list(self.all_remain[label].values()),
                name='Remain',
                mode='lines+markers',
                line=dict(
                    width=2,
                    color='rgb(255,127,14)',
                ),
                marker=dict(
                    size=1,
                    color='rgb(255,127,14)',
                ),
                showlegend=True if label == list(self.all_spent.keys())[0] else False
            ))
            try:
                trace_dict[label].append(go.Scatter(
                    x=[min(self.all_remain[label].keys()), self.end_date[label]],
                    y=[max([math.fabs(rmn) for rmn in self.all_remain[label].values()]), 0],
                    name='',
                    mode='lines',
                    line=dict(
                        color='rgb(200,200,200)',
                        width=2,
                        dash='dash'),
                    showlegend=False
                ))
            except ValueError:
                pass
        cols = math.ceil(len(self.all_spent.keys()) / 2)
        fig = subplots.make_subplots(rows=2, cols=cols, subplot_titles=list(self.all_spent.keys()))
        for traces, i, label in zip(trace_dict.values(), range(len(trace_dict.keys())), trace_dict.keys()):
            row, col = int(i // cols + 1), int(i % cols + 1)
            for trace in traces:
                fig.append_trace(trace, row, col)
            xaxis, yaxis = 'xaxis{}'.format(i + 1), 'yaxis{}'.format(i + 1)
            fig["layout"][xaxis].update(
                linecolor='black',
                type='date',
                dtick=86400000,
                showline=True,
                showticklabels=True,
                showgrid=False,
                tickvals=xticks[label],
                ticktext=[xticks[label][i].strftime('%d.%m.%y') if not i % 10 else '' for i in range(len(xticks[label]))],
                autorange=True
            )
            fig["layout"][yaxis].update(
                linecolor='black',
                showline=True,
                gridcolor='rgb(232,232,232)',
                autorange=True
            )

        title = '{} specific works'.format(self.dashboard_name)
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout']['title'].update(
            text='{0} as of {1}'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M")), x=0.5)
        fig["layout"].update(hovermode='closest', legend=dict(orientation='h'), plot_bgcolor='white')
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=14)

        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'citrix':
            plotly.offline.plot(fig, image_filename=title, image='png', image_height=1080, image_width=1920)
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
            time.sleep(5)
            shutil.move('C:/Users/{}/Downloads/{}.png'.format(self.local_user, title), './files/{}.png'.format(title))
            citrix = CitrixShareFile(hostname=self.citrix_token['hostname'],
                                     client_id=self.citrix_token['client_id'],
                                     client_secret=self.citrix_token['client_secret'],
                                     username=self.citrix_token['username'], password=self.citrix_token['password'])
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path='./files/{}.png'.format(title))
            citrix.upload_file(folder_id='fofd8511-6564-44f3-94cb-338688544aac',
                               local_path=html_file)

    def export_to_plot(self):
        self.export_to_plotly()
