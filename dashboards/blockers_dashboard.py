from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from plotly import tools
from datetime import datetime
from adapters.issue_utils import get_domain, get_domain_by_project


def color_for_status(status):
    return {
        'Open': 'rgb(75,103,132)',
        'Dev': 'rgb(254,210,92)',
        'Closed': 'rgb(29,137,49)'
    }[status]


class BlockersDashboard(AbstractDashboard):
    key_list, created_list, status_list, components_list, project_list = [], [], [], [], []
    auto_open, priority, fixversion, projects, statuses = True, None, None, None, None
    bugs_annotation_dict, statuses_dict = {}, {}

    def prepare(self, data):
        self.key_list, self.created_list, self.status_list, self.components_list, self.project_list =\
            data.get_bugs(self.projects, self.priority, self.fixversion, self.statuses)
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
            if self.components_list[i] != ['']:
                self.components_list[i] = get_domain(*self.components_list[i])
            else:
                self.components_list[i] = get_domain_by_project(self.project_list[i])
            if self.components_list[i] not in self.bugs_annotation_dict.keys():
                self.bugs_annotation_dict[self.components_list[i]] = {'key': [], 'created': [], 'status': []}
                self.statuses_dict[self.components_list[i]] = {'Open': 0, 'Dev': 0, 'Closed': 0}
            self.bugs_annotation_dict[self.components_list[i]]['key'].append(self.key_list[i])
            self.bugs_annotation_dict[self.components_list[i]]['created'].append(self.created_list[i])
            self.bugs_annotation_dict[self.components_list[i]]['status'].append(self.status_list[i])
            self.statuses_dict[self.components_list[i]][self.status_list[i]] += 1
        print(self.bugs_annotation_dict)

    def export_to_plotly(self):
        if len(self.key_list) == 0:
            raise ValueError('There is no issues to show')

        trace_dict = {domain: [] for domain in self.statuses_dict.keys()}
        titles = []
        for domain, statuses, annotation in zip(self.statuses_dict.keys(), self.statuses_dict.values(),
                                                self.bugs_annotation_dict.values()):
            title = ['<textarea cols="20" wrap="hard">']
            for i in range(len(annotation["key"])):
                if annotation["status"][i] in ('Open', 'Dev'):
                    title.append(annotation["key"][i])
            title.append('</textarea>')

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
        fig = tools.make_subplots(rows=2, cols=4, subplot_titles=list(self.statuses_dict.keys()))
        for traces, i in zip(trace_dict.values(), range(len(trace_dict.keys()))):
            row, col = int(i // 4 + 1), int(i % 4 + 1)
            for trace in traces:
                fig.append_trace(trace, row, col)
            xaxis = 'xaxis' + str(i+1)
            fig["layout"][xaxis].update(
                showticklabels=False,
                title=titles[i]
            )

        title = self.dashboard_name
        html_file = self.png_dir + "{0}.html".format(title)

        plotly.offline.plot(fig, filename=html_file, auto_open=self.auto_open)

    def export_to_plot(self):
        self.export_to_plotly()
