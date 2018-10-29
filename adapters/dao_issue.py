# coding: utf-8
#
# Copyright © 2018 .

class DaoIssue(object):
    def insert_issues(self, issues):
        raise NotImplementedError(
            _("Method insert_issues not yet supported in") + " \"" + self.__class__.__name__ + "\".")

    def get_sum_by_projects(self, project_filter,label_filter, fixversions_filter):  # must return 4 arrays
        raise NotImplementedError(_("Method get_sum not yet supported in") + " \"" + self.__class__.__name__ + "\".")

    def close(self):
        raise NotImplementedError(_("Method close not yet supported in") + " \"" + self.__class__.__name__ + "\".")

