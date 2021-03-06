from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain_bssbox, domain_shortener
import json
import plotly
import plotly.graph_objs as go
import datetime
from plotly import subplots
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time
import textwrap
import requests
import re


def load_capacity(dashboard_name):
    scope = re.search(r'Super Sprint \d+|Pilot .+', dashboard_name).group(0)
    url = 'https://stash.billing.ru/projects/DBSS_TRACKING/repos/super-sprint-capacity/raw/{}.json'.format(scope)
    r = requests.get(url=url)
    return r.json()


def color_for_status(status):
    return {'Open': 'rgb(217,98,89)', 'Dev': 'rgb(254,210,92)', 'Done': 'rgb(29,137,49)'}[status]


def color_for_est(est):
    return {'Capacity': 'rgb(158,244,82)', 'Bulk estimate': 'rgb(97,100,223)', 'Original estimate': 'rgb(82,162,218)',
            'Spent time': 'rgb(75,223,156)'}[est]


class SprintInfoDashboard(AbstractDashboard):
    auto_open, repository, citrix_token, local_user = True, None, None, None
    est_dict, st_dict = {}, {}
    prj_est, prj_st = {'Capacity': 0, 'Bulk estimate': 0, 'Original estimate': 0,
                       'Spent time': 0}, {'Open': 0, 'Dev': 0, 'Done': 0}
    readiness = {'Open': {'Spent': 0, 'Original': 0}, 'Dev': {'Spent': 0, 'Original': 0},
                 'Done': {'Spent': 0, 'Original': 0}, 'Total': 0}

    def prepare(self, data):
        spent, original = 0, 0
        capacity_dict = {}
        for dmn, cap in load_capacity(self.dashboard_name).items():
            try:
                domain = domain_shortener[dmn]
                if domain not in capacity_dict.keys():
                    capacity_dict[domain] = cap
                else:
                    capacity_dict[domain] += cap
            except KeyError:
                print(dmn)
        self.prj_est['Capacity'] = sum(capacity_dict.values())
        for i in range(len(data['Key'])):
            if data['Issue type'][i] != 'User Story (L3)':
                k = data['Key'].count(data['Key'][i])
                domain = get_domain_bssbox(data['Component'][i])
                if domain not in self.est_dict.keys():
                    self.est_dict[domain] = {'Capacity': capacity_dict.get(domain, 0), 'Bulk estimate': 0,
                                             'Original estimate': 0, 'Spent time': 0}
                    self.st_dict[domain] = {'Open': 0, 'Dev': 0, 'Done': 0}
                self.est_dict[domain]['Original estimate'] += float(data['Estimate'][i]) / 28800
                self.prj_est['Original estimate'] += float(data['Estimate'][i]) / 28800 / k
                self.est_dict[domain]['Spent time'] += float(data['Spent time'][i]) / 28800
                self.prj_est['Spent time'] += float(data['Spent time'][i]) / 28800 / k
                self.st_dict[domain][data['Status'][i]] += 1
                self.prj_st[data['Status'][i]] += 1 / k
                self.readiness[data['Status'][i]]['Spent'] += float(data['Spent time'][i]) / 28800 / k
                self.readiness[data['Status'][i]]['Original'] += float(data['Estimate'][i]) / 28800 / k
                if domain not in ('QC', 'Doc'):
                    spent += float(data['Spent time'][i]) / 28800 / k
                    original += float(data['Spent time'][i]) / 28800 / k \
                        if float(data['Spent time'][i]) > float(data['Estimate'][i]) or data['Status'][i] == 'Done' \
                        else float(data['Estimate'][i]) / 28800 / k
            else:
                d = json.loads(data['Estimate'][i])
                for cmp in d.keys():
                    domain = get_domain_bssbox(cmp)
                    if domain not in self.est_dict.keys():
                        self.est_dict[domain] = {'Capacity': capacity_dict.get(domain, 0),
                                                 'Bulk estimate': 0, 'Original estimate': 0, 'Spent time': 0}
                        self.st_dict[domain] = {'Open': 0, 'Dev': 0, 'Done': 0}
                    self.est_dict[domain]['Bulk estimate'] += float(d[cmp])
                    self.prj_est['Bulk estimate'] += float(d[cmp])
        self.readiness['Total'] = round(spent / original * 100) if spent <= original else 100
        print(spent, original, self.readiness['Total'])

    def export_to_plotly(self):
        if len(self.est_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        data_est, data_st = [], []
        for est in self.est_dict[list(self.est_dict.keys())[0]].keys():
            data_est.append(go.Bar(
                x=[key for key in self.est_dict.keys() if key != 'Common'],
                y=[e[est] for key, e in self.est_dict.items() if key != 'Common'],
                xaxis='x1',
                yaxis='y1',
                name=est,
                showlegend=True,
                legendgroup='group',
                text=[round(e[est], 1) for key, e in self.est_dict.items() if key != 'Common'],
                textposition='auto',
                marker=dict(
                    color=color_for_est(est),
                    line=dict(
                        width=1,
                        color='black'
                    )
                )
            ))
        base = [0]*len([key for key in self.st_dict.keys() if key != 'Common'])
        for st in self.st_dict[list(self.st_dict.keys())[0]].keys():
            data_st.append(go.Bar(
                x=[key for key in self.st_dict.keys() if key != 'Common'],
                y=[s[st] for key, s in self.st_dict.items() if key != 'Common'],
                xaxis='x2',
                yaxis='y2',
                name=st,
                showlegend=True,
                legendgroup='group1',
                text=[s[st] for key, s in self.st_dict.items() if key != 'Common'],
                textposition='auto',
                base=base,
                offset=-0.4,
                width=0.8,
                marker=dict(
                    color=color_for_status(st),
                    line=dict(
                        width=1,
                        color='black'
                    )
                )
            ))
            base = [bs + cnt for bs, cnt in
                    zip(base, [counts[st] for key, counts in list(self.st_dict.items()) if key != 'Common'])]

        est_title = '<i><b>Ratio of high level estimates, original estimates and spent time<br>Total: </b>{}. <b>Readiness: </b>{}%</i>'.\
            format(', '.join(['{} - {} md'.format(est, round(val)) for est, val in self.prj_est.items()]), self.readiness['Total'])
        st_title = '<i><b>Progress of development work<br>Total: </b>{}</i>'.\
            format(', '.join(['{} - {} ({} out of {} md)'.format(status, round(count), round(self.readiness[status]['Spent'], 1),
                                                                 round(self.readiness[status]['Original'], 1)) for status, count in self.prj_st.items()]))
        fig = subplots.make_subplots(rows=2, cols=1, vertical_spacing=0.12, subplot_titles=(est_title, st_title))
        for trace_est in data_est:
            fig.append_trace(trace_est, 1, 1)
        for trace_st in data_st:
            fig.append_trace(trace_st, 2, 1)

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout'].update(legend=dict(y=0.5), hovermode='closest', plot_bgcolor='white')
        fig['layout']['title'].update(x=0.5, text='<b>{0} as of {1}</b>'
                                      .format(self.dashboard_name, datetime.datetime.now().strftime("%d.%m.%y %H:%M")))
        fig['layout']['xaxis1'].update(anchor='y1', showgrid=True, tickfont=dict(size=9),
                                       linecolor='black', gridcolor='rgb(232,232,232)',
                                       tickvals=[key for key in self.est_dict.keys() if key != 'Common'],
                                       ticktext=[key if len(key) < 8 else '<br>'.join(textwrap.wrap(key, 12))
                                                 for key in self.est_dict.keys() if key != 'Common'])
        fig['layout']['yaxis1'].update(anchor='x1', showline=True, title='Man-days',
                                       linecolor='black', gridcolor='rgb(232,232,232)')
        fig['layout']['xaxis2'].update(anchor='y2', showgrid=True, tickfont=dict(size=9),
                                       linecolor='black', gridcolor='rgb(232,232,232)',
                                       tickvals=[key for key in self.st_dict.keys() if key != 'Common'],
                                       ticktext=[key if len(key) < 8 else '<br>'.join(textwrap.wrap(key, 12))
                                                 for key in self.st_dict.keys() if key != 'Common'])
        fig['layout']['yaxis2'].update(anchor='x2', showline=True, title='Count of tasks and sub-tasks',
                                       linecolor='black', gridcolor='rgb(232,232,232)',)

        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=14)

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
