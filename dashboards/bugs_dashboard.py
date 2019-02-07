from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from plotly import tools
from datetime import datetime
from adapters.issue_utils import get_domain, get_domain_by_project
import textwrap
import math


def color_for_status(status):
    return {
        'Open': 'rgb(217,98,89)',
        'In Fix': 'rgb(254,210,92)',
        'Closed': 'rgb(29,137,49)'
    }[status]


class BugsDashboard(AbstractDashboard):
    key_list, created_list, status_list, components_list, project_list = [], [], [], [], []
    auto_open, priority, projects, statuses, labels, repository = True, None, None, None, None, None
    bugs_annotation_dict, statuses_dict = {}, {}

    def prepare(self, data):
        self.key_list.clear(), self.created_list.clear(), self.status_list.clear(), self.components_list.clear(),\
            self.project_list.clear(), self.bugs_annotation_dict.clear(), self.statuses_dict.clear()
        self.key_list, self.created_list, self.status_list, self.components_list, self.project_list =\
            data.get_bugs(self.projects, self.priority, self.statuses, self.labels)
        for i in range(len(self.key_list)):
            self.created_list[i] = datetime.strptime(self.created_list[i][:11].strip(), '%Y-%m-%d')
            self.components_list[i] = self.components_list[i].split(',')
            if len(self.components_list[i]) != 1:
                for _ in range(1, len(self.components_list[i])):
                    self.components_list.append([self.components_list[i].pop()])
                    self.key_list.append(self.key_list[i])
                    self.status_list.append(self.status_list[i])
                    self.created_list.append(self.created_list[i])
                    self.project_list.append(self.project_list[i])
        for i in range(len(self.key_list)):
            if self.components_list[i] != [''] and get_domain(*self.components_list[i]) != 'OTHERS':
                self.components_list[i] = get_domain(*self.components_list[i])
            else:
                self.components_list[i] = get_domain_by_project(self.project_list[i])
            if self.components_list[i] not in self.bugs_annotation_dict.keys():
                self.bugs_annotation_dict[self.components_list[i]] = {'key': [], 'created': [], 'status': []}
                self.statuses_dict[self.components_list[i]] = {'Open': 0, 'In Fix': 0, 'Closed': 0}
            self.bugs_annotation_dict[self.components_list[i]]['key'].append(self.key_list[i])
            self.bugs_annotation_dict[self.components_list[i]]['created'].append(self.created_list[i])
            self.bugs_annotation_dict[self.components_list[i]]['status'].append(self.status_list[i])
            self.statuses_dict[self.components_list[i]][self.status_list[i]] += 1

    def export_to_plotly(self):
        if len(self.key_list) == 0:
            raise ValueError('There is no issues to show')

        plotly.tools.set_credentials_file(username='Rnd-Rnd', api_key='GFSxsbDP8rOiakf0rs8U')

        trace_dict = {domain: [] for domain in self.statuses_dict.keys()}
        annotations_open, annotations_fix = [], []
        for domain, statuses, annotation in zip(self.statuses_dict.keys(), self.statuses_dict.values(),
                                                self.bugs_annotation_dict.values()):
            annotation_open, annotation_fix = '<b>Open:</b> ', '<b>In Fix:</b> '
            for i in range(len(annotation["key"])):
                if annotation["status"][i] == 'Open':
                    if annotation["created"][i].date() == datetime.now().date():
                        annotation_open += '<b>' + annotation["key"][i] + '</b> '
                    else:
                        annotation_open += annotation["key"][i] + ' '
                elif annotation["status"][i] == 'In Fix':
                    if annotation["created"][i].date() == datetime.now().date():
                        annotation_fix += '<b>' + annotation["key"][i] + '</b> '
                    else:
                        annotation_fix += annotation["key"][i] + ' '
            annotations_open.append('<br>'.join(textwrap.wrap(annotation_open, 33)))
            annotations_fix.append('<br>'.join(textwrap.wrap(annotation_fix, 33)))
            for status in statuses:
                trace_dict[domain].append(go.Bar(
                    x=[domain],
                    y=[statuses[status]],
                    name=status,
                    marker=dict(
                        color=color_for_status(status),
                        line=dict(
                            color='black',
                            width=1
                        )
                    ),
                    showlegend=True if domain == list(self.statuses_dict.keys())[0] else False
                ))
        cols = math.ceil(len(self.statuses_dict.keys())/2)
        fig = tools.make_subplots(rows=2, cols=cols, subplot_titles=list(self.statuses_dict.keys()))
        for traces, i in zip(trace_dict.values(), range(len(trace_dict.keys()))):
            row, col = int(i // cols + 1), int(i % cols + 1)
            for trace in traces:
                fig.append_trace(trace, row, col)
            xaxis = 'xaxis' + str(i+1)
            fig["layout"][xaxis].update(
                showticklabels=False,
                # title=annotations_open[i] + '<br>' + annotations_fix[i],
                # titlefont=dict(
                #     size=10
                # ),
                title=dict(
                    text=annotations_open[i] + '<br>' + annotations_fix[i],
                    font=dict(
                        size=10
                    )
                ),
                automargin=True
            )

        title = self.dashboard_name
        # html_file = self.png_dir + "{0}.html".format(title)
        html_file = '//billing.ru/dfs/incoming/ABryntsev/' + "{0}.html".format(title)

        fig["layout"].update(title='<b>{0} as of {1}</b>'.format(title, datetime.now().strftime("%d.%m.%y %H:%M"))
                                   + (' <sup>in cloud</sup>' if self.repository == 'online' else ''))
        if self.repository == 'offline':
            plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)
        elif self.repository == 'online':
            plotly.plotly.plot(fig, filename=title, fileopt='overwrite', sharing='public', auto_open=False)

    def export_to_plot(self):
        self.export_to_plotly()
