from dashboards.dashboard import AbstractDashboard
import json
import plotly
import plotly.graph_objs as go
import datetime
from adapters.issue_utils import get_domain


bulk_convert = {
        'Common': 'Others', 'Infra': 'Infra', 'Billing': 'Billing', 'Business Analysis': 'BA',
        'CRM (Customer Relationship Management)': 'CRM', 'Charge Events Storage': 'Billing',
        'Order Management': 'Ordering', 'Design': 'Design', 'DevOps': 'DevOps', 'DFE (Digital Frontend)': 'DFE',
        'Digital API': 'DFE', 'Documentation': 'Doc', 'Dunning and Collection': 'Billing',
        'Logical Resource Inventory': 'PSC', 'Network Monetization': 'NWM', 'Partner Management': 'PRM',
        'Payment Management': 'Billing', 'Performance Testing': 'Others', 'Product Management': 'PSC', 'QC': 'Others',
        'System Architecture': 'Arch'
    }


class FeatureInfoDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    feature_dict, spent_dict, info, commited = {}, {}, [], []

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] == 'User Story (L3)':
                if data['Flagged'][i]:
                    self.commited.append(data['Key'][i])
                if data['Key'][i] not in self.feature_dict.keys():
                    self.feature_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                         if domain != 'Others'}
                    self.spent_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                       if domain != 'Others'}
                    self.info.append(' ({})<br>{}'.format(data['FL'][i], data['Feature name'][i]))
                d = json.loads(data['Estimate'][i]) if data['Estimate'][i] is not None else {}
                for domain in [key for key in d.keys() if not key.isdigit() and key != 'Total']:
                    if bulk_convert[domain] != 'Others':
                        self.feature_dict[data['Key'][i]][bulk_convert[domain]] += float(d[domain]['v'])
            else:
                if get_domain(data['Component'][i]) not in ('Empty', 'Others'):
                    self.spent_dict[data['Feature'][i]][get_domain(data['Component'][i])] += float(data['Spent time'][i]) / 28800
        fd, pt, sd, info = {}, 1, {}, {}
        for ft, est, spent, inf in zip(self.feature_dict.keys(), self.feature_dict.values(), self.spent_dict.values(), self.info):
            if 'part{}'.format(pt) not in fd.keys():
                fd['part{}'.format(pt)], sd['part{}'.format(pt)], info['part{}'.format(pt)] = {}, {}, []
            fd['part{}'.format(pt)][ft], sd['part{}'.format(pt)][ft] = est, spent
            info['part{}'.format(pt)].append(inf)
            if len(fd['part{}'.format(pt)].keys()) > 14:
                pt += 1
        self.feature_dict, self.spent_dict, self.info = fd, sd, info

    def export_to_plotly(self):
        if len(self.feature_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        for pt, estimates, spents, info in zip(self.feature_dict.keys(), self.feature_dict.values(), self.spent_dict.values(), self.info.values()):
            data, base = [], [0]*len(spents.keys())
            for dmn in estimates[list(estimates.keys())[0]].keys():
                data.append(go.Bar(
                    orientation='h',
                    y=list(estimates.keys()),
                    x=[est[dmn] for est in estimates.values()],
                    name=dmn,
                    showlegend=False,
                    text=[dmn]*len(estimates.keys()),
                    textposition='inside',
                    marker=dict(
                        color=['rgb(255,245,245)' if ft in self.commited else 'rgb(250,250,250)' for ft in list(estimates.keys())],
                        opacity=0.5,
                        line=dict(
                            color=['rgb(102,0,0)' if ft in self.commited else 'rgb(0,0,0)' for ft in list(estimates.keys())],
                            width=2
                        )
                    ),
                    base=base,
                    offset=-0.4,
                    width=0.8
                ))
                data.append(go.Bar(
                    orientation='h',
                    y=list(spents.keys()),
                    x=[spent[dmn] for spent in spents.values()],
                    name=dmn,
                    showlegend=False,
                    text='',
                    textposition='inside',
                    marker=dict(
                        color=['rgb(255,153,153)' if ft in self.commited else 'rgb(180,180,180)' for ft in list(spents.keys())]
                    ),
                    base=base,
                    offset=-0.39,
                    width=0.78
                ))
                base = [bs + cnt for bs, cnt in zip(base, [est[dmn] for est in estimates.values()])]

            title = '{} Features ({})'.format(self.dashboard_name, pt)
            # html_file = self.png_dir + "{0}.html".format(title)
            html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

            for el in ['<a href="https://jira.billing.ru/browse/{0}">{0}</a>{1}'.format(key, inf) for key, inf in zip(list(estimates.keys()), info)]:
                print(el)
            layout = dict(
                title='<b>{0} as of {1}</b>'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                      + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
                yaxis=dict(
                    automargin=True,
                    tickvals=list(estimates.keys()),
                    ticktext=['<a href="https://jira.billing.ru/browse/{0}">{0}</a>{1}'.format(key, inf) for key, inf in zip(list(estimates.keys()), info)],
                    ticks='outside',
                    ticklen=10,
                    tickcolor='rgba(0,0,0,0)'
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
