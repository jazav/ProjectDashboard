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
import json


class YotaDomainBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, dashboard_type, citrix_token, local_user = True, None, None, None, None, None
    all_spent, all_remain = {}, {}
    start_date, end_date = datetime.date(2019, 2, 18), datetime.date(2020, 3, 1)
    estimates = []

    def multi_prepare(self, data_spent, data_original):
        # dmns = ['BA', 'System Architecture', 'Arch & SA', 'Billing', 'CES', 'Pays', 'CRM1', 'CRM2',
        #         'Ordering & PRM', 'PSC', 'Performance Testing', 'DevOps']
        # self.all_spent = {dmn: {} for dmn in dmns}
        all_original, spent, original = {}, {}, {}
        for i in range(len(data_spent['key'])):
            data_spent['component'][i] = get_domain_bssbox(data_spent['component'][i])
            if data_spent['created'][i] < self.start_date:
                if data_spent['component'][i] not in spent.keys():
                    spent[data_spent['component'][i]] = 0
                    self.all_spent[data_spent['component'][i]] = {}
                spent[data_spent['component'][i]] += float(data_spent['spent'][i])
                self.all_spent[data_spent['component'][i]][self.start_date] = spent[data_spent['component'][i]]
            else:
                if data_spent['component'][i] not in spent.keys():
                    spent[data_spent['component'][i]] = 0
                    self.all_spent[data_spent['component'][i]] = {}
                spent[data_spent['component'][i]] += float(data_spent['spent'][i])
                self.all_spent[data_spent['component'][i]][data_spent['created'][i]] = spent[data_spent['component'][i]]
        for i in range(len(data_original['key'])):
            if data_original['issue type'][i] == 'User Story (L3)':
                d = json.loads(data_original['estimate'][i])
                d = {key: float(val) for key, val in d.items()}
                self.estimates.append(d)
                for cmp, est in d.items():
                    domain = get_domain_bssbox(cmp)
                    if domain not in original.keys():
                        original[domain] = 0
                        all_original[domain] = {}
                    original[domain] += est
                    all_original[domain][self.start_date] = original[domain]
            else:
                if data_original['resolution date'][i] and data_original['component'][i]:
                    try:
                        original[data_original['component'][i]] -= [est[data_original['component'][i]] for est, key in
                                                                    zip(self.estimates, data_original['key'])
                                                                    if key == data_original['L3'][i]][0]
                        all_original[data_original['component'][i]][data_original['resolution date'][i]] \
                            = original[data_original['component'][i]]
                    except KeyError:
                        pass
        for dmn, spents in self.all_spent.items():
            if dmn not in all_original.keys():
                all_original[dmn] = {dt: 0 for dt in spents.keys()}
            for dt in spents.keys():
                if dt not in all_original[dmn].keys():
                    try:
                        all_original[dmn][dt] = all_original[dmn][max([date for date in all_original[dmn].keys() if date < dt])]
                    except ValueError:
                        all_original[dmn][dt] = all_original[dmn][list(all_original[dmn].keys())[-1]]
        for dmn in all_original:
            all_original[dmn] = {dt: all_original[dmn][dt] for dt in sorted(all_original[dmn].keys())}
        for dmn, origs in all_original.items():
            if dmn not in self.all_spent:
                self.all_spent[dmn] = {dt: 0 for dt in origs.keys()}
            for dt in origs.keys():
                if dt not in self.all_spent[dmn].keys():
                    try:
                        self.all_spent[dmn][dt] = self.all_spent[dmn][max([date for date in self.all_spent[dmn].keys() if date < dt])]
                    except ValueError:
                        self.all_spent[dmn][dt] = self.all_spent[dmn][list(self.all_spent[dmn].keys())[0]]
        for dmn in self.all_spent:
            self.all_spent[dmn] = {dt: self.all_spent[dmn][dt] for dt in sorted(self.all_spent[dmn].keys())}
        for dmn in self.all_spent.keys():
            self.all_remain[dmn] = {dt: all_original[dmn][dt] - self.all_spent[dmn][dt]
                                    + float(sum([sp for sp, rd, domain in zip(data_spent['spent'], data_spent['resolutiondate'], data_spent['component'])
                                            if domain == dmn and rd is not None and rd <= dt])) for dt in self.all_spent[dmn].keys()}

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
                    size=1,
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
                    size=1,
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
        for traces, i, dmn in zip(trace_dict.values(), range(len(trace_dict.keys())), trace_dict.keys()):
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
                showline=True
            )

        title = '{} by domains'.format(self.dashboard_name)
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout']['title'].update(text='{0} as of {1}'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M")), x=0.5)
        fig["layout"].update(hovermode='closest', legend=dict(orientation='h'), plot_bgcolor='white')
        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=14)

        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        # elif self.repository == 'online':
        #     plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
        #     plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)
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
