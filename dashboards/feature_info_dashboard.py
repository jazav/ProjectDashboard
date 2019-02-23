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
    feature_dict, est_dict = {}, {}

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] == 'User Story (L3)':
                if data['Key'][i] not in self.feature_dict.keys():
                    self.feature_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                         if domain != 'Others'}
                    self.est_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                     if domain != 'Others'}
                d = json.loads(data['Estimate'][i]) if data['Estimate'][i] is not None else {}
                for domain in [key for key in d.keys() if not key.isdigit() and key != 'Total']:
                    if bulk_convert[domain] != 'Others':
                        self.feature_dict[data['Key'][i]][bulk_convert[domain]] += float(d[domain]['v'])
            else:
                if get_domain(data['Component'][i]) not in ('Empty', 'Others'):
                    self.est_dict[data['Feature'][i]][get_domain(data['Component'][i])] += float(data['Spent time'][i]) / 28800
        fd, pt, ed = {}, 1, {}
        print(self.feature_dict.keys())
        for ft, est in self.feature_dict.items():
            if 'part{}'.format(pt) not in fd.keys():
                fd['part{}'.format(pt)] = {}
                ed['part{}'.format(pt)] = {}
            fd['part{}'.format(pt)][ft] = est
            if len(fd['part{}'.format(pt)].keys()) > 15:
                pt += 1
        self.feature_dict = fd
        print(self.est_dict.keys())

    def export_to_plotly(self):
        if len(self.feature_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        for pt, estimates in self.feature_dict.items():
            data, base = [], [0]*len(estimates.keys())
            for dmn in estimates[list(estimates.keys())[0]].keys():
                data.append(go.Bar(
                    orientation='h',
                    y=[key for key in estimates.keys()],
                    x=[est[dmn] for est in estimates.values()],
                    name=dmn,
                    showlegend=False,
                    text=[dmn]*len(estimates.keys()),
                    textposition='inside',
                    marker=dict(
                        color='rgb(255,255,255)',
                        line=dict(
                            width=2
                        )
                    )
                ))

            title = '{} Features ({})'.format(self.dashboard_name, pt)
            # html_file = self.png_dir + "{0}.html".format(title)
            html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

            layout = dict(
                barmode='stack',
                title='<b>{0} as of {1}</b>'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M"))
                      + (' <sup>in cloud</sup>' if self.repository == 'online' else ''))
            fig = go.Figure(data=data, layout=layout)
            if self.repository == 'offline':
                plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
            elif self.repository == 'online':
                plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
                plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
