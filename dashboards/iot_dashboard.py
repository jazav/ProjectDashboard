from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime
import textwrap


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
                key = '{}: {}'.format(data['Key'][i], data['Summary'][i])
                if key not in self.iot_dict.keys():
                    self.iot_dict[key] = {'Plan estimate': 0, 'Fact estimate': 0, 'Spent time': 0}
                self.iot_dict[key]['Plan estimate'] += int(data['Original estimate'][i]) / 28800
        for k, v in self.iot_dict.items():
            print('{}: {}'.format(k, v))

    def export_to_plotly(self):
        if len(self.iot_dict.keys()) == 0:
            raise ValueError('There is no issues to show')

        data = []
        for est in self.iot_dict[list(self.iot_dict.keys())[0]].keys():
            data.append(go.Bar(
                x=list(self.iot_dict.keys()),
                y=[e[est] for e in self.iot_dict.values()],
                name=est,
                showlegend=True,
                text=[e[est] for e in self.iot_dict.values()],
                textposition='auto',
                marker=dict(
                    line=dict(
                        width=1
                    )
                )
            ))

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = dict(
            xaxis=dict(
                automargin=True,
                tickvals=list(self.iot_dict.keys()),
                ticktext=['<br>'.join(textwrap.wrap(epic, 12)) for epic in self.iot_dict.keys()]
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
