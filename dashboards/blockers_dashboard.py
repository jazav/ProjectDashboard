from dashboards.dashboard import AbstractDashboard
import plotly
import plotly.graph_objs as go
from datetime import datetime
from adapters.issue_utils import get_domain, get_domain_by_project


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
                self.bugs_annotation_dict[self.components_list[i]] = {'key': [], 'created': []}
                self.statuses_dict[self.components_list[i]] = {'Open': 0, 'Dev': 0, 'Closed': 0}
            self.bugs_annotation_dict[self.components_list[i]]['key'].append(self.key_list[i])
            self.bugs_annotation_dict[self.components_list[i]]['created'].append(self.created_list[i])
            self.statuses_dict[self.components_list[i]][self.status_list[i]] += 1
        print(self.bugs_annotation_dict)
        print(self.statuses_dict)
