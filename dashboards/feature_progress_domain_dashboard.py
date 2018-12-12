import datetime
import plotly
import plotly.graph_objs as go
import plotly.io as pio
from plotly import tools

from config_controller import cc_klass
from dashboards.dashboard import AbstractDashboard

from enum import Enum, auto
class DashboardType(Enum):
     PROJECT = auto()
     FEATURE = auto()
     DOMAIN = auto()


class DashboardFormat(Enum):
    HTML = auto()
    PNG = auto()

PLAN_PREFIX = '<b>Plan</b>'
FACT_PREFIX = '<b>Closed</b>'
OPEN_PREFIX = '<b>Open</b>'
DEV_PREFIX = '<b>Dev</b>'


def stringDivider(strval, width, spaceReplacer):
    if (len(strval) > width):
        p = width
        while ((p > 0) and (strval[p] != ' ')):
            p = p - 1
        if (p == 0):
            while (p < len(strval) and (strval[p] != ' ')):
                p = p + 1
        if (p > 0):
            left = strval[0:p]
            right = strval[p + 1:]
            return left + spaceReplacer + stringDivider(right, width, spaceReplacer)
    return strval

class FeatureProgressDomainDashboard(AbstractDashboard):
    '''Plotly Bar Stacked Chart'''
    open_list = []
    dev_list = []
    close_list = []
    name_list = []
    brnamelist = []
    auto_open = True
    fixversion = None
    project = None
    dashboard_type = DashboardType.PROJECT
    dashboard_format = DashboardFormat.HTML

    def prepare(self, data):
        if self.fixversion is None:
            raise ValueError('fixversion is undefined')
        self.open_list, self.dev_list, self.close_list, self.name_list, self.prj_list, self.domain_list = \
            data.get_sum_by_projects(self.project, "", self.fixversion, 'domain' if self.dashboard_type == DashboardType.DOMAIN else 'summary, project')

    def get_name_list(self):
        if self.dashboard_type == DashboardType.PROJECT:
            return self.prj_list
        elif self.dashboard_type == DashboardType.FEATURE:
            return self.brnamelist
        else:
            return self.domain_list

    def get_title_xaxis(self):
        if self.dashboard_type == DashboardType.PROJECT:
            return "Projects"
        elif self.dashboard_type == DashboardType.FEATURE:
            return "Features(L3)"
        else:
            return "Domains"

    def export_to_plotly(self):
        if len(self.name_list) == 0:
            return
        cc = cc_klass()

        self.brnamelist = []
        for vl in self.name_list:
            self.brnamelist.append(stringDivider(vl, int(cc.read_display_width()/10/len(self.name_list)), "<br>"))
            #colors.append()

        traces = []
        # was: brnamelist
        trace1 = go.Bar(
            x=self.get_name_list(),
            y=self.close_list,
            text=self.close_list,
            name=FACT_PREFIX,
            textposition='auto',
            marker=dict(
                color='rgb(29,137,49)',#'palegreen',
                line=dict(
                    color='black',
                    width=1),
            ),
            insidetextfont=dict(family='Arial', size=12,
                      color='white')
        )
        # was: brnamelist
        trace2 = go.Bar(
            x=self.get_name_list(),
            y=self.dev_list,
            text=self.dev_list,
            name=DEV_PREFIX,
            textposition='auto',
            marker=dict(
                color='rgb(254,210,92)',#'lightgoldenrodyellow',
                line=dict(
                    color='black',
                    width=1),
            ),
            insidetextfont=dict(family='Arial', size=12,
                      color='black')
        )
        # was: brnamelist
        trace3 = go.Bar(
            x=self.get_name_list(),
            y=self.open_list,
            text=self.open_list,
            name=OPEN_PREFIX,
            textposition='auto',
            marker=dict(
                color='rgb(75,103,132)',#'powderblue',
                line=dict(
                    color='black',
                    width=1),
            ),
            insidetextfont=dict(family='Arial', size=12,
                      color='white')
        )
        traces.append(trace1)
        traces.append(trace2)
        traces.append(trace3)
        all_open = 0
        for value in self.open_list:
            all_open += value
        all_dev = 0
        for value in self.dev_list:
            all_dev += value
        all_closed = 0
        for value in self.close_list:
            all_closed += value
        all_tasks= all_closed + all_dev + all_open
        if all_tasks == 0:
            all_tasks = 1
        plan_fact_str = "pf"
        title_sum = "Open: {0:.2f}%, Dev: {1:.2f}%, Closed: {2:.2f}%, All tasks: {3:.2f} md".format(100*all_open/all_tasks, 100*all_dev/all_tasks, 100*all_closed/all_tasks, all_tasks)
        now_dt = datetime.datetime.now()

        length_ss = cc.read_supersprint_length(self.fixversion)

        if length_ss != 0:
            will_be_done = min(100, 100*(now_dt - cc.read_supersprint_start(self.fixversion)).days / length_ss)
        else:
            will_be_done = 0
        title = "{0} <br>{1} <br> Must be closed today ({4}) in {2}: {3:.2f}%".format(self.dashboard_name,  title_sum, self.fixversion, will_be_done, now_dt.strftime("%d.%m.%y %H:%M"))
        tools.make_subplots

        file_name1 = self.dashboard_name + ' ' + ("" if (self.dashboard_type == DashboardType.DOMAIN or self.project != "") else (self.dashboard_type.name +" "))+plan_fact_str
        file_name = self.png_dir + "{0}_{1}".format(file_name1, self.project)
        layout = go.Layout(
            annotations=[
                dict(
                    x=1.05,
                    y=1.03,
                    xref='paper',
                    yref='paper',
                    text='Status',
                    showarrow=False,
                    font=dict(
                        family='sans-serif',
                        size=14,
                        color='black'
                    )
                )
            ],
            legend=dict(
                x=1,
                y=1,
                traceorder='normal',
                font=dict(
                    family='sans-serif',
                    size=14,
                    color='#000'
                )
            ),
            showlegend=True,
            margin=dict(t=50, b=50, r=100, l=6 * 6),
            autosize=True,
            font=dict(size=12, color='black'),
            barmode='stack',
            title=title,
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
                title='Estimates (man-days)',
                tickfont=dict(
                    size=10,
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
                showticklabels=self.dashboard_type == DashboardType.PROJECT or self.dashboard_type == DashboardType.DOMAIN or (len(self.dev_list) < 30),
                tickfont=dict(
                    size=16 if self.dashboard_type == DashboardType.DOMAIN else 10,
                    color='black'

                ),
                title=self.get_title_xaxis(),
                titlefont=dict(
                    size=12,
                    color='black'
                )
            )
        )

        fig = go.Figure(data=traces, layout=layout)
        if self.dashboard_format == DashboardFormat.HTML:
            plotly.offline.plot(fig, filename=file_name+'.html', auto_open=self.auto_open)
        else:
            #plotly.offline.plot(fig,auto_open=self.auto_open, image='png', image_filename=file_name+'.png',
            #             output_type='file', filename=file_name+'.html')
            pio.write_image(fig, file_name+'.png')



    def export_to_plot(self):
        self.export_to_plotly()

    def export_to_json(self):
        raise NotImplementedError('export_to_json')
