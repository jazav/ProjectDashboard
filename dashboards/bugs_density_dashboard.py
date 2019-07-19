from datetime import datetime
import plotly
import plotly.graph_objs as go
# from plotly import tools
# from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain, get_domain_by_project
import numpy
import statistics


class BugsDensityDashboard(AbstractDashboard):
    domain_list, density_list = [], []
    auto_open, repository, plotly_auth = True, None, None

    def prepare(self, data):
        self.domain_list.clear()
        self.density_list.clear()
        self.domain_list, self.density_list =  data.get_bugs_density(self.labels, self.priority, self.creators)

    def export_to_plotly(self):
        if len(self.domain_list) == 0:
            raise ValueError('There is no issues to show')

        trace_dens = go.Bar(
            x=list(self.domain_list()),
            y=self.density_list,
            text=self.density_list,
            name='density',
            textposition='auto',
            marker=dict(
                color='rgb(126,135,215)',
                line=dict(color='black',
                          width=1),
            ),
            insidetextfont=dict(family='sans-serif',
                                size=18,
                                color='white')
        )

        traces = [trace_dens]

        plan_fact_str = "pf"

        title = "Density for last 2 monthes"
        html_file = "bugs_density.html"


        layout = go.Layout(
            annotations=[],
            legend=dict(
                x=1,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=16,
                    color='#000'
                )
            ),
            showlegend=True,
            margin=dict(t=50, b=50, r=100, l=36),
            autosize=True,
            font=dict(size=12, color='black'),
            barmode='group',
            title=title + (' <sup>in cloud</sup>' if self.repository == 'online' else ''),
            plot_bgcolor='white',
            yaxis=dict(
                rangemode="tozero",
                autorange=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                ticks='',
                showticklabels=True,
                tickangle=0,
                title='Days',
                titlefont=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                ),
                # title=dict(
                #     text='Days between creation and resolution',
                #     font=dict(
                #         family='sans-serif',
                #         size=12,
                #         color='black'
                #     )
                # ),
                tickfont=dict(
                    family='sans-serif',
                    size=16,
                    color='black'

                ),
            ),
            xaxis=dict(
                rangemode="tozero",
                autorange=True,
                showgrid=True,
                zeroline=True,
                showline=True,
                ticks='',
                tickangle=0,
                showticklabels=True,
                tickfont=dict(
                    family='sans-serif',
                    size=16,
                    color='black'

                ),
                title='Domains',
                titlefont=dict(
                    family='sans-serif',
                    size=12,
                    color='black'
                )
                # title=dict(
                #     text='Domains',
                #     font=dict(
                #         family='sans-serif',
                #         size=12,
                #         color='black'
                #     )
                # )
            )
        )

        fig = go.Figure(data=traces, layout=layout)
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.tools.set_credentials_file(username=self.plotly_auth[0], api_key=self.plotly_auth[1])
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
