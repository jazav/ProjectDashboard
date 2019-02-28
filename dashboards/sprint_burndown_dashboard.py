from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
import datetime


class SprintBurndownDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    all_spent = {}

    def prepare(self, data_spent, data_original):
        spent = 0
        for i in range(len(data['key'])):
            spent += float(data['spent'][i])
            self.all_spent[data['created'][i]] = spent

    def export_to_plotly(self):
        if len(self.all_spent.keys()) == 0:
            raise ValueError('There is no issues to show')

        data = [go.Scatter(
            x=list(self.all_spent.keys()),
            y=list(self.all_spent.values()),
            name='Spent',
            text=[str(round(sp, 1)) for sp in self.all_spent.values()],
            textposition='bottom right',
            mode='lines+markers+text',
            line=dict(
                width=2
            ),
            marker=dict(
                size=5
            )
        )]

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = go.Layout(
            xaxis=dict(
                type='date',
                dtick=86400000,
                title='Date',
                titlefont=dict(
                    size=12
                ),
                tickfont=dict(
                    size=16
                ),
                showline=True
            ),
            yaxis=dict(
                showline=True,
                title='Man-hour',
                titlefont=dict(
                    size=12
                ),
                tickfont=dict(
                    size=16
                )
            ),
            title=title
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
