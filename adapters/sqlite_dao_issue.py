# coding: utf-8
#
# Copyright © 2018 .
#

import sqlite3

import sys

from adapters.dao_issue import DaoIssue

__SqliteDaoIssue__ = None



def get_sqlite_dao():
    global __SqliteDaoIssue__
    if __SqliteDaoIssue__ == None:
        __SqliteDaoIssue__ = SqliteDaoIssue()
    return __SqliteDaoIssue__

class SqliteDaoIssue(DaoIssue):
    def __init__(self):
        self.connection = sqlite3.connect(":memory:")
        self.cursor = self.connection.cursor()
        # "UIKIT-233": {
        #     "key": "UIKIT-233",
        #     "id": 1265253,
        #     "issuetype": "Task",
        #     "status": "Resolved",
        #     "project": "UIKIT",
        #     "components": "",
        #     "domains": "",
        #     "labels": "devTicket,mark3",
        #     "epiclink": "UIKIT-164",
        #     "parent": "",
        #     "subtasks": "",
        #     "outwards": "BSSSCP-106",
        #     "inwards": "",
        #     "summary": "Update Card component",
        #     "description": "",
        #     "resolution": "Done",
        #     "resolutiondate": "2018-09-19 14:53:16.000000+0300",
        #     "timeoriginalestimate": 0.25,
        #     "timeestimate": 0.125,
        #     "timespent": 0.125,
        #     "storypoints": 0.0,
        #     "creator": "Andrew.Eremenko",
        #     "assignee": "Andrew.Eremenko",
        #     "reporter": "Andrew.Eremenko",
        #     "duedate": null,
        #     "aggregatetimeestimate": [
        #         0.125
        #     ],
        #     "aggregatetimeoriginalestimate": 0.25,
        #     "updated": "2018-09-19 14:53:17.000000+0300",
        #     "created": "2018-09-14 18:25:37.000000+0300",
        #     "progress": 50.0,
        #     "aggregateprogress": 50.0,
        #     "priority": "Major"
        # }
        self.cursor.execute('''CREATE TABLE issues
                               (issue_key TEXT,id INTEGER, status TEXT, project TEXT,
                                labels TEXT, epiclink TEXT, timeoriginalestimate REAL, timespent REAL,
                               resolution TEXT, issuetype TEXT, summary TEXT)''')

        self.connection.commit()

    def insert_issues(self, issues):
        for key, value in issues.items():
            try:
                self.cursor.execute('''INSERT INTO issues (issue_key, id, status, project,
                                        labels, epiclink, timeoriginalestimate, timespent,
                                       resolution, issuetype, summary)
                                         VALUES (?,?,?,?,
                                                 ?,?,?,?,
                                                 ?,?,?)''',
                                    (key, value["id"], value["status"], value["project"],
                                     ','+value["labels"]+',', 'value["epiclink"]', value["timeoriginalestimate"], value["timespent"],
                                     value["resolution"],value["issuetype"],value["summary"],))
            except:
                print("Unexpected error on key:", key, ' value:  ', value, ', error:', sys.exc_info()[0])

        self.connection.commit()

    def get_sum_by_projects(self, project_filter,label_filter):  # must return array of ReportRow
        open_list= [];
        dev_list= [];
        close_list= [];
        name_list = [];
        sql_str = '''SELECT
                                           i.project,
                                           e.summary,
                                           e.timeoriginalestimate,
                                           SUM(CASE WHEN i.status in ('Closed','Resolved') THEN
                                               i.timeoriginalestimate
                                           ELSE
                                               0
                                           END) close,
                                           SUM(CASE WHEN i.status in ('Open') THEN
                                               i.timeoriginalestimate
                                           ELSE
                                               0
                                           END) open,
                                           SUM(CASE WHEN i.status in ('Open','Closed','Resolved') THEN
                                               0
                                           ELSE
                                               i.timeoriginalestimate
                                           END) dev
                                  FROM issues e 
                                   LEFT JOIN issues i
                                        ON e.issue_key = i.epiclink
                                  WHERE e.issuetype = "Epic"
                                    AND e.project = "'''+project_filter+'"'+ ' AND e.labels LIKE "%,'+label_filter+',%"  group by e.summary, e.timeoriginalestimate, i.project';
        for row in self.cursor.execute(sql_str):
            name_list.append(row[1]);
            close_list.append(row[3])
            open_list.append(row[4]);
            dev_list.append(row[5]);
        return open_list, dev_list, close_list, name_list;

