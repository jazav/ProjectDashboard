from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain_bssbox
import json
import plotly
import plotly.graph_objs as go
import datetime
from plotly import tools
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time


def color_for_status(status):
    return {'Open': 'rgb(217,98,89)', 'Dev': 'rgb(254,210,92)', 'Done': 'rgb(29,137,49)'}[status]


def color_for_est(est):
    return {'Bulk estimate': 'rgb(97,100,223)', 'Original estimate': 'rgb(82,162,218)', 'Spent time': 'rgb(75,223,156)'}[est]


class SprintInfoDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, citrix_token, local_user = True, None, None, None, None
    est_dict, st_dict = {}, {}
    prj_est, prj_st = {'Bulk estimate': 0, 'Original estimate': 0, 'Spent time': 0}, {'Open': 0, 'Dev': 0, 'Done': 0}
    readiness = 0

    def prepare(self, data):
        spent, original = 0, 0
        for i in range(len(data['Key'])):
            if data['Issue type'][i] != 'User Story (L3)':
                data['Component'][i] = get_domain_bssbox(data['Component'][i])
                if data['Component'][i] not in self.est_dict.keys():
                    self.est_dict[data['Component'][i]] = {'Bulk estimate': 0, 'Original estimate': 0, 'Spent time': 0}
                    self.st_dict[data['Component'][i]] = {'Open': 0, 'Dev': 0, 'Done': 0}
                self.est_dict[data['Component'][i]]['Original estimate'] += int(data['Estimate'][i]) / 28800
                self.prj_est['Original estimate'] += int(data['Estimate'][i]) / 28800
                original += int(data['Estimate'][i]) / 28800
                self.est_dict[data['Component'][i]]['Spent time'] += int(data['Spent time'][i]) / 28800
                self.prj_est['Spent time'] += int(data['Spent time'][i]) / 28800
                spent += int(data['Spent time'][i]) / 28800 if data['Status'] != 'Done' else int(data['Estimate'][i]) / 28800
                self.st_dict[data['Component'][i]][data['Status'][i]] += 1
                self.prj_st[data['Status'][i]] += 1
            else:
                d = json.loads(data['Estimate'][i])
                for cmp in d.keys():
                    domain = get_domain_bssbox(cmp)
                    if domain not in self.est_dict.keys():
                        self.est_dict[domain] = {'Bulk estimate': 0, 'Original estimate': 0, 'Spent time': 0}
                        self.st_dict[domain] = {'Open': 0, 'Dev': 0, 'Done': 0}
                    self.est_dict[domain]['Bulk estimate'] += float(d[cmp])
                    self.prj_est['Bulk estimate'] += float(d[cmp])
        self.readiness = round(spent / original * 100)

    def export_to_plotly(self):
        print(self.prj_est)
        print(self.prj_st)
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
                        width=1
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
                        width=1
                    )
                )
            ))
            base = [bs + cnt for bs, cnt in
                    zip(base, [counts[st] for key, counts in list(self.st_dict.items()) if key != 'Common'])]

        est_title = '<i><b>Ratio of high level estimates, original estimates and spent time<br>Total: </b>{}. <b>Readiness: </b>{}%</i>'.\
            format(', '.join(['{} - {}'.format(key, round(val)) for key, val in self.prj_est.items()]), self.readiness)
        st_title = '<i><b>Progress of development work</b>Total: </b>{}</i>'.\
            format(', '.join(['{} - {}'.format(key, val) for key, val in self.prj_st.items()]))
        fig = tools.make_subplots(rows=2, cols=1, vertical_spacing=0.07, subplot_titles=(est_title, st_title))
        for trace_est, trace_st in zip(data_est, data_st):
            fig.append_trace(trace_est, 1, 1)
            fig.append_trace(trace_st, 2, 1)

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout'].update(title='<b>{0} as of {1}</b>'.format(self.dashboard_name, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                                   + (' <sup>in cloud</sup>' if self.repository == 'online' else ''), legend=dict(y=0.5), hovermode='closest')
        fig['layout']['xaxis1'].update(anchor='y1', showgrid=True, tickfont=dict(size=9))
        fig['layout']['yaxis1'].update(anchor='x1', showline=True, title='Man-days')
        fig['layout']['xaxis2'].update(anchor='y2', showgrid=True, tickfont=dict(size=9))
        fig['layout']['yaxis2'].update(anchor='x2', showline=True, title='Count of tasks and sub-tasks')

        for annotation in fig['layout']['annotations']:
            annotation['font'] = dict(size=14)

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
