from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain, get_domain_by_project
import plotly
import plotly.graph_objs as go
from datetime import datetime


def color_for_status(status):
    return {
        'open': 'rgb(217,98,89)',
        'in fix': 'rgb(254,210,92)',
        'resolved': 'rgb(75,103,132)',
        'closed': 'rgb(29,137,49)'
    }[status]


class AllBugsDashboard(AbstractDashboard):
    auto_open, repository, plotly_auth = True, None, None
    bssbox_dict, domain_dict = {'BSSBox': {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}},\
                               {'Total': {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}}

    def prepare(self, data):
        for project, component, status in zip(data['project'], data['component'], data['status']):
            if project != 'BSSBOX':
                domain = get_domain_by_project(project)
                if domain not in self.domain_dict.keys():
                    self.domain_dict[domain] = {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}
                self.domain_dict[domain][status] += 1
                self.domain_dict['Total'][status] += 1
            else:
                domain = get_domain(component)
                if domain not in self.bssbox_dict.keys():
                    self.bssbox_dict[domain] = {'open': 0, 'in fix': 0, 'resolved': 0, 'closed': 0}
                self.bssbox_dict[domain][status] += 1
                self.bssbox_dict['BSSBox'][status] += 1

    def export_to_plotly(self):
        if len(self.domain_dict.keys()) == 1:
            raise ValueError('There is no issues to show')

        data = []
        for status in self.domain_dict[list(self.domain_dict)[0]].keys():
            data.append(go.Bar(
                orientation='v',
                x=[dmn for dmn in self.bssbox_dict if dmn != 'BSSBox'],
                y=[self.bssbox_dict[dmn][status] for dmn in self.bssbox_dict if dmn != 'BSSBox'],
                text=[self.bssbox_dict[dmn][status] for dmn in self.bssbox_dict if dmn != 'BSSBox'],
                name=status,
                textposition='auto',
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                xaxis='x1',
                yaxis='y1',
                showlegend=True
            ))
            data.append(go.Bar(
                orientation='h',
                x=[self.bssbox_dict['BSSBox'][status]],
                y=['BSSBox'],
                text=[self.bssbox_dict['BSSBox'][status]],
                name=status,
                textposition='auto',
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                xaxis='x2',
                yaxis='y2',
                showlegend=False
            ))
            data.append(go.Bar(
                orientation='v',
                x=[dmn for dmn in self.domain_dict if dmn != 'Total'],
                y=[self.domain_dict[dmn][status] for dmn in self.domain_dict if dmn != 'Total'],
                text=[self.domain_dict[dmn][status] for dmn in self.domain_dict if dmn != 'Total'],
                name=status,
                textposition='auto',
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                xaxis='x3',
                yaxis='y3',
                showlegend=False
            ))
            data.append(go.Bar(
                orientation='h',
                x=[self.domain_dict['Total'][status]],
                y=['Total'],
                text=[self.domain_dict['Total'][status]],
                name=status,
                textposition='auto',
                marker=dict(
                    color=color_for_status(status),
                    line=dict(
                        color='black',
                        width=1
                    )
                ),
                xaxis='x4',
                yaxis='y4',
                showlegend=False
            ))

        title = self.dashboard_name
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        layout = dict(
            title='<b>{0} as of {1}</b>'.format(self.dashboard_name, datetime.now().strftime("%d.%m.%y %H:%M"))
                  + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
            barmode='stack',
            xaxis1=dict(domain=[0, 0.48], anchor='y1', ticks='outside', ticklen=4, tickcolor='rgba(0,0,0,0)'),
            yaxis1=dict(domain=[0.15, 1], anchor='x1', ticks='outside', ticklen=8, tickcolor='rgba(0,0,0,0)'),
            xaxis2=dict(domain=[0, 0.48], anchor='y2'),
            yaxis2=dict(domain=[0, 0.1], anchor='x2', ticks='outside', ticklen=8, tickcolor='rgba(0,0,0,0)'),
            xaxis3=dict(domain=[0.52, 1], anchor='y3', ticks='outside', ticklen=4, tickcolor='rgba(0,0,0,0)'),
            yaxis3=dict(domain=[0.15, 1], anchor='x3', ticks='outside', ticklen=8, tickcolor='rgba(0,0,0,0)'),
            xaxis4=dict(domain=[0.52, 1], anchor='y4'),
            yaxis4=dict(domain=[0, 0.1], anchor='x4', ticks='outside', ticklen=8, tickcolor='rgba(0,0,0,0)'),
            legend=dict(x=0.39, y=1.04, orientation='h')
        )

        fig = go.Figure(data=data, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
