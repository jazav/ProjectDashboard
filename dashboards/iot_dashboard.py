from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
import textwrap


def color_for_est(est):
    return {'Plan estimate': 'rgb(97,100,223)', 'Fact estimate': 'rgb(82,162,218)', 'Spent time': 'rgb(75,223,156)'}[est]


class IotDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    iot_dict = {}

    def prepare(self, data):
        for i in range(len(data['Key'])):
            if data['Issue type'][i] != 'Epic':
                if data['Epic'][i] not in self.iot_dict.keys():
                    self.iot_dict[data['Epic'][i]] = {'Plan estimate': 0, 'Fact estimate': 0, 'Spent time': 0}
                self.iot_dict[data['Epic'][i]]['Fact estimate'] += int(data['Original estimate'][i]) / 28800
                self.iot_dict[data['Epic'][i]]['Spent time'] += int(data['Spent time'][i]) / 28800
            else:
                if data['Key'][i] not in self.iot_dict.keys():
                    self.iot_dict[data['Key'][i]] = {'Plan estimate': 0, 'Fact estimate': 0, 'Spent time': 0}
                self.iot_dict[data['Key'][i]]['Plan estimate'] += int(data['Original estimate'][i]) / 28800
        for k, v in self.iot_dict.items():
            print('{}: {}'.format(k, v))

    def export_to_plotly(self):
        if len(self.iot_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        data = []
        for est in self.iot_dict[list(self.iot_dict.keys())[0]].keys():
            data.append(go.Bar(
                y=list(self.iot_dict.keys()),
                x=[e[est] for e in self.iot_dict.values()],
                orientation='h',
                name=est,
                showlegend=True,
                text=[round(e[est], 1) for e in self.iot_dict.values()],
                textposition='auto',
                marker=dict(
                    color=color_for_est(est),
                    line=dict(
                        width=1
                    )
                )
            ))

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = dict(
            yaxis=dict(
                automargin=True,
                tickvals=list(self.iot_dict.keys()),
                ticktext=['<a href="https://jira.billing.ru/browse/{0}">{0}   </a>'.format(epic) for epic in self.iot_dict.keys()],
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
