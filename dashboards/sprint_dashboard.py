from dashboards.dashboard import AbstractDashboard
from adapters.issue_utils import get_domain_by_project, get_domain


class SprintDashboard(AbstractDashboard):
    auto_open, fixversion = True, None
    key_list, project_list, status_list, components_list, timeoriginalestimate_list, timespent_list, issuetype_list = \
        [], [], [], [], [], [], []
    domain_list, bugs_dict, accuracy_dict = [], {}, {}

    def prepare(self, data):
        self.key_list, self.project_list, self.status_list, self.components_list, self.timeoriginalestimate_list,\
         self.timespent_list, self.issuetype_list = data.get_sprint_info(self.fixversion)
        print(len(self.key_list))
        for i in range(len(self.key_list)):
            if self.issuetype_list[i] == 'Bug':
                self.components_list[i] = self.components_list[i].split(',')
                if len(self.components_list[i]) != 1:
                    for _ in range(1, len(self.components_list[i])):
                        self.components_list.append([self.components_list[i].pop()])
                        self.key_list.append(self.key_list[i])
                        self.project_list.append(self.project_list[i])
                        self.status_list.append(self.status_list[i])
                        self.timeoriginalestimate_list.append(self.timeoriginalestimate_list[i])
                        self.timespent_list.append(self.timespent_list[i])
                        self.issuetype_list.append(self.issuetype_list[i])
        self.domain_list = [None] * len(self.key_list)
        for i in range(len(self.key_list)):
            if self.issuetype_list[i] != 'Bug':
                self.domain_list[i] = get_domain_by_project(self.project_list[i])
                if self.domain_list[i] not in self.accuracy_dict.keys():
                    self.accuracy_dict[self.domain_list[i]] = {'Plan': 0, 'Fact': 0}
                self.accuracy_dict[self.domain_list[i]]['Plan'] += self.timeoriginalestimate_list[i]
                self.accuracy_dict[self.domain_list[i]]['Fact'] += self.timespent_list[i]
            else:
                if self.components_list[i] != [''] and get_domain(*self.components_list[i]) != 'Others':
                    self.domain_list[i] = get_domain(*self.components_list[i])
                else:
                    self.domain_list[i] = get_domain_by_project(self.project_list[i])
                if self.domain_list[i] not in self.bugs_dict.keys():
                    self.bugs_dict[self.domain_list[i]] = {'Open': 0, 'In Fix': 0, 'Closed': 0}
                self.bugs_dict[self.domain_list[i]][self.status_list[i]] += 1
        print(self.bugs_dict)
        print(self.accuracy_dict)
