from dashboards.dashboard import AbstractDashboard
from datetime import datetime


class ArbaIssuesDashboard(AbstractDashboard):
    name_list, assignee_list, created_list, duedate_list = [], [], [], []
    auto_open, assignees = True, None
    team_dict = {}

    def prepare(self, data):
        self.name_list, self.assignee_list, self.created_list, self.duedate_list = data.get_arba_issues(self.assignees)

        for i in range(len(self.name_list)):
            if self.assignee_list[i] not in self.team_dict:
                self.team_dict[self.assignee_list[i]] = {}
            self.team_dict[self.assignee_list[i]] = {
                self.name_list[i]: [
                    datetime.strptime(self.created_list[i][:11].strip(), '%Y-%m-%d').date(),
                    datetime.strptime(self.duedate_list[i][:11].strip(), '%Y-%m-%d').date()
                ]
            }

        print(self.team_dict)
