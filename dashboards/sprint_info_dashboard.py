from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain
import json
import plotly
import plotly.graph_objs as go
import datetime
from plotly import tools


def bulk_convert(domain):
    return {
        'Common': 'Others', 'Infra': 'Infra', 'Billing': 'Billing', 'Business Analysis': 'BA',
        'CRM (Customer Relationship Management)': 'CRM', 'Charge Events Storage': 'Billing',
        'Order Management': 'Ordering', 'Design': 'Design', 'DevOps': 'DevOps', 'DFE (Digital Frontend)': 'DFE',
        'Digital API': 'DFE', 'Documentation': 'Doc', 'Dunning and Collection': 'Billing',
        'Logical Resource Inventory': 'PSC', 'Network Monetization': 'NWM', 'Partner Management': 'PRM',
        'Payment Management': 'Billing', 'Performance Testing': 'Others', 'Product Management': 'PSC', 'QC': 'Others',
        'System Architecture': 'Arch'
    }[domain]


def color_for_status(status):
    return {'Open': 'rgb(217,98,89)', 'Dev': 'rgb(254,210,92)', 'Done': 'rgb(29,137,49)'}[status]


def color_for_est(est):
    return {'Bulk Estimate': 'rgb(97,100,223)', 'Original Estimate': 'rgb(82,162,218)', 'Spent Time': 'rgb(75,223,156)'}[est]


class SprintInfoDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    est_dict, st_dict = {}, {}

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] != 'User Story (L3)':
                data['Component'][i] = get_domain(data['Component'][i])
                if data['Component'][i] not in self.est_dict.keys():
                    self.est_dict[data['Component'][i]] = {'Bulk Estimate': 0, 'Original Estimate': 0, 'Spent Time': 0}
                    self.st_dict[data['Component'][i]] = {'Open': 0, 'Dev': 0, 'Done': 0}
                self.est_dict[data['Component'][i]]['Original Estimate'] += int(data['Estimate'][i]) / 28800
                self.est_dict[data['Component'][i]]['Spent Time'] += int(data['Spent time'][i]) / 28800
                self.st_dict[data['Component'][i]][data['Status'][i]] += 1
            else:
                d = json.loads(data['Estimate'][i]) if data['Estimate'][i] is not None else {}
                for domain in [key for key in d.keys() if not key.isdigit() and key != 'Total']:
                    if bulk_convert(domain) not in self.est_dict.keys():
                        self.est_dict[bulk_convert(domain)] = {'Bulk Estimate': 0, 'Original Estimate': 0, 'Spent Time': 0}
                        self.st_dict[bulk_convert(domain)] = {'Open': 0, 'Dev': 0, 'Done': 0}
                    self.est_dict[bulk_convert(domain)]['Bulk Estimate'] += float(d[domain]['v'])

    def export_to_plotly(self):
        if len(self.est_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        data_est, data_st = [], []
        for est in self.est_dict[list(self.est_dict.keys())[0]].keys():
            data_est.append(go.Bar(
                x=[key for key in self.est_dict.keys() if key != 'Others'],
                y=[e[est] for key, e in self.est_dict.items() if key != 'Others'],
                xaxis='x1',
                yaxis='y1',
                name=est,
                showlegend=True,
                text=[round(e[est], 1) for key, e in self.est_dict.items() if key != 'Others'],
                textposition='auto',
                marker=dict(
                    color=color_for_est(est),
                    line=dict(
                        width=1
                    )
                )
            ))
        base = [0]*len([key for key in self.st_dict.keys() if key != 'Others'])
        for st in self.st_dict[list(self.st_dict.keys())[0]].keys():
            data_st.append(go.Bar(
                x=[key for key in self.st_dict.keys() if key != 'Others'],
                y=[s[st] for key, s in self.st_dict.items() if key != 'Others'],
                xaxis='x2',
                yaxis='y2',
                name=st,
                showlegend=True,
                text=[s[st] for key, s in self.st_dict.items() if key != 'Others'],
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
                    zip(base, [counts[st] for key, counts in list(self.st_dict.items()) if key != 'Others'])]

        fig = tools.make_subplots(rows=2, cols=1, vertical_spacing=0.07,
                                  subplot_titles=('<b><i>Ratio of high level estimates, original estimates and spent time</i></b>',
                                                  '<b><i>Progress of development work</i></b>'))
        for trace_est, trace_st in zip(data_est, data_st):
            fig.append_trace(trace_est, 1, 1)
            fig.append_trace(trace_st, 2, 1)

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout'].update(title='<b>{0} as of {1}</b>'.format(self.dashboard_name, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                                   + (' <sup>in cloud</sup>' if self.repository == 'online' else ''), legend=dict(y=0.5))
        fig['layout']['xaxis1'].update(anchor='y1', showgrid=True)
        fig['layout']['yaxis1'].update(anchor='x1', showline=True, title='Man-days')
        fig['layout']['xaxis2'].update(anchor='y2', showgrid=True)
        fig['layout']['yaxis2'].update(anchor='x2', showline=True, title='Count of tasks and sub-tasks')

        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
