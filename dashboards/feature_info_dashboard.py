from dashboards.dashboard import AbstractDashboard
import json
import plotly
import plotly.graph_objs as go
import math
from plotly import tools


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
    feature_dict = {}

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] == 'User Story (L3)':
                if data['Key'][i] not in self.feature_dict.keys():
                    self.feature_dict[data['Key'][i]] = {domain: 0 for domain in bulk_convert.values()
                                                         if domain != 'Others'}
                d = json.loads(data['Estimate'][i]) if data['Estimate'][i] is not None else {}
                for domain in [key for key in d.keys() if not key.isdigit() and key != 'Total']:
                    if bulk_convert[domain] != 'Others':
                        self.feature_dict[data['Key'][i]][bulk_convert[domain]] += float(d[domain]['v'])
        for k, v in self.feature_dict.items():
            print('{}: {}'.format(k, v))

    def export_to_plotly(self):
        if len(self.feature_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        trace_dict = {ft: [] for ft in self.feature_dict.keys()}
        for ft in trace_dict.keys():
            for dmn in self.feature_dict[ft].keys():
                trace_dict[ft].append(go.Bar(
                    x=[ft],
                    y=[self.feature_dict[ft][dmn]],
                    name=dmn,
                    showlegend=False,
                    text=[dmn],
                    textposition='inside',
                    marker=dict(
                        color='rgb(245,245,245)',
                        line=dict(
                            width=2
                        )
                    )
                ))
        cols = len(self.feature_dict.keys())
        fig = tools.make_subplots(rows=1, cols=cols)
        for traces, i in zip(trace_dict.values(), range(len(trace_dict.keys()))):
            row, col = int(i // cols + 1), int(i % cols + 1)
            for trace in traces:
                fig.append_trace(trace, row, col)
            xaxis, yaxis = 'xaxis' + str(i + 1), 'yaxis' + str(i + 1)
            fig['layout'][xaxis].update(
                showticklabels=True,
                automargin=True,
                tickangle=90
            )
            fig['layout'][yaxis].update(
                showticklabels=False,
            )
        # data, base = [], [0]*len(self.feature_dict.keys())
        # for dmn in self.feature_dict[list(self.feature_dict.keys())[0]].keys():
        #     data.append(go.Bar(
        #         x=[key for key in self.feature_dict.keys()],
        #         y=[est[dmn] for est in self.feature_dict.values()],
        #         name=dmn,
        #         showlegend=False,
        #         text=[dmn]*len(self.feature_dict.keys()),
        #         textposition='inside',
        #         marker=dict(
        #             color='rgb(255,255,255)',
        #             line=dict(
        #                 width=2
        #             )
        #         )
        #     ))

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig['layout'].update(barmode='stack')

        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
