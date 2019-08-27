from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
from adapters.issue_utils import get_domain_bssbox
import math
from plotly import subplots
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


class DomainBurndownDashboard(AbstractDashboard):
    auto_open, repository, dashboard_type, citrix_token, local_user, end_date = True, None, None, None, None, None
    all_spent, all_remain = {}, {}

    def multi_prepare(self, data_spent, data_original):
        all_original, spent, original, kk = {}, {}, {}, []

        for i in range(len(data_spent['key'])):
            k = set()
            for j in range(len(data_spent['key'])):
                if data_spent['key'][j] == data_spent['key'][i]:
                    k.add(data_spent['component'][j])
            k = len(k)
            kk.append(k)
            domain = get_domain_bssbox(data_spent['component'][i])
            if domain not in spent.keys():
                spent[domain], self.all_spent[domain] = 0, {}
            spent[domain] += float(data_spent['spent'][i]) / k
            self.all_spent[domain][data_spent['created'][i]] = spent[domain]

        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] != 'User Story (L3)':
                domain = get_domain_bssbox(data_original['component'][i])
                k = data_original['key'].count(data_original['key'][i])
                if domain not in original.keys():
                    original[domain] = sum([float(data_original['timeoriginalestimate'][j]) / k
                                            for j in range(len(data_original['key']))
                                            if data_original['issue type'][j] != 'User Story (L3)'
                                            and get_domain_bssbox(data_original['component'][j]) == domain])
                    all_original[domain] = {data_original['created'][i]: original[domain]}
                if data_original['status'][i] in ('Closed', 'Resolved', 'Done') and data_original['resolutiondate'][i]:
                    original[domain] -= float(data_original['timeoriginalestimate'][i]) / k
                    all_original[domain][data_original['resolutiondate'][i]] = original[domain]

        for dmn in all_original:
            all_original[dmn] = {dt: all_original[dmn][dt] for dt in sorted(all_original[dmn].keys())}
        for dmn, spents in self.all_spent.items():
            for date in spents.keys():
                if date not in all_original[dmn].keys():
                    try:
                        all_original[dmn][date] = all_original[dmn][max([
                            dt for dt in all_original[dmn].keys() if dt < date])]
                    except ValueError:
                        all_original[dmn][date] = all_original[dmn][list(all_original[dmn].keys())[0]]

        for domain in self.all_spent.keys():
            self.all_remain[domain] = {}
            for dt in self.all_spent[domain].keys():
                sp = 0
                for i, k in zip(range(len(data_spent['key'])), kk):
                    if domain == get_domain_bssbox(data_spent['component'][i]) \
                            and data_spent['status'][i] in ('Closed', 'Resolved', 'Done') \
                            and data_spent['resolutiondate'][i] \
                            and data_spent['resolutiondate'][i] <= dt:
                        sp += float(data_spent['spent'][i]) / k
                self.all_remain[domain][dt] = all_original[domain][dt] - (self.all_spent[domain][dt] - sp)

    def export_to_plotly(self):
        trace_dict = {dmn: [] for dmn in self.all_spent.keys()}
        for dmn in self.all_spent.keys():
            trace_dict[dmn].append(go.Scatter(
                x=list(self.all_spent[dmn].keys()),
                y=list(self.all_spent[dmn].values()),
                name='Spent',
                mode='lines+markers',
                line=dict(
                    width=2,
                    color='rgb(31,119,180)',
                ),
                marker=dict(
                    size=3,
                    color='rgb(31,119,180)',
                ),
                showlegend=True if dmn == list(self.all_spent.keys())[0] else False
            ))
            trace_dict[dmn].append(go.Scatter(
                x=list(self.all_remain[dmn].keys()),
                y=list(self.all_remain[dmn].values()),
                name='Remain',
                mode='lines+markers',
                line=dict(
                    width=2,
                    color='rgb(255,127,14)',
                ),
                marker=dict(
                    size=3,
                    color='rgb(255,127,14)',
                ),
                showlegend=True if dmn == list(self.all_spent.keys())[0] else False
            ))
            try:
                trace_dict[dmn].append(go.Scatter(
                    x=[min(self.all_remain[dmn].keys()), self.end_date],
                    y=[max([math.fabs(rmn) for rmn in self.all_remain[dmn].values()]), 0],
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
        for traces, i in zip(trace_dict.values(), range(len(trace_dict.keys()))):
            row, col = int(i // cols + 1), int(i % cols + 1)
            for trace in traces:
                fig.append_trace(trace, row, col)
            xaxis, yaxis = 'xaxis{}'.format(i + 1), 'yaxis{}'.format(i + 1)
            fig["layout"][xaxis].update(
                linecolor='black',
                type='date',
                dtick=86400000,
                showline=True,
                showticklabels=False,
                showgrid=False
            )
            fig["layout"][yaxis].update(
                linecolor='black',
                showline=True,
                gridcolor='rgb(232,232,232)'
            )

        title = '{} by domains'.format(self.dashboard_name)
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout']['title'].update(text='{0} as of {1}'
                                      .format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M")), x=0.5)
        fig['layout'].update(hovermode='closest', legend=dict(orientation='h'), plot_bgcolor='white')
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
