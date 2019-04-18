from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from adapters.citrix_sharefile_adapter import CitrixShareFile
import shutil
import time
import datetime


class BaWorkDistributionDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth, citrix_token, local_user = True, None, None, None, None
    sprint_distribution = {}

    def prepare(self, data):
        for i in range(len(data['Sprint'])):
            if data['Sprint'][i] not in self.sprint_distribution.keys():
                self.sprint_distribution[data['Sprint'][i]] = 0
            self.sprint_distribution[data['Sprint'][i]] += int(data['Spent'][i]) / 28800

    def export_to_plotly(self):
        if len(self.sprint_distribution.keys()) == 0:
            raise ValueError('There is no issues to show')

        data = [go.Bar(
            x=list(self.sprint_distribution.keys()),
            y=list(self.sprint_distribution.values()),
            showlegend=False,
            text=[round(val, 2) for val in list(self.sprint_distribution.values())],
            textposition='inside',
            marker=dict(
                color='rgba(29,137,49,0.3)',
                line=dict(
                    color='rgb(29,137,49)',
                    width=2
                )
            )
        )]

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            hovermode='closest',
            title='<b>{} as of {}</b>'.format(title, datetime.datetime.now().strftime("%d.%m.%y %H:%M")),
            xaxis=dict(title='Sprints'),
            yaxis=dict(title='Man-days')
        )

        fig = go.Figure(data=data, layout=layout)
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
