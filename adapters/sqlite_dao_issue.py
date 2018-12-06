# coding: utf-8
#
# Copyright © 2018 .
#
import logging
import sqlite3

import sys

from adapters.dao_issue import DaoIssue
from adapters.issue_utils import get_domain_by_project

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
                               resolution TEXT, issuetype TEXT, summary TEXT, fixversions TEXT, parent TEXT,
                               created TEXT, resolutiondate TEXT, components TEXT, priority TEXT, creator TEXT,
                               assignee TEXT, duedate TEXT)''')

        self.connection.commit()

    def insert_issues(self, issues):
        if len(issues) == 0:
            return
        handle = open("sql.txt", "w")

        for key, value in issues.items():
            try:
                if "fixversions" in value:
                    fixversions = value["fixversions"]
                else:
                    fixversions = ""
                sql_str = '''INSERT INTO issues (issue_key, id, status, project,
                                        labels, epiclink, timeoriginalestimate, timespent,
                                       resolution, issuetype, summary, fixversions, 
                                       parent, created, resolutiondate, components, priority, creator,
                                       assignee, duedate)'''
                self.cursor.execute(sql_str + ''' VALUES (?,?,?,?,
                                                 ?,?,?,?,
                                                 ?,?,?,?,
                                                 ?,?,?,?,
                                                 ?,?,?,?)''',
                                    (key, value["id"], value["status"], value["project"],
                                     ','+value["labels"]+',', value["epiclink"], value["timeoriginalestimate"], value["timespent"],
                                     value["resolution"],value["issuetype"],value["summary"],','+fixversions+',',
                                     value["parent"], value["created"], value["resolutiondate"], value["components"],
                                     value["priority"], value["creator"], value["assignee"], value["duedate"]))
                if 1 == 0 :
                    write_str=sql_str +'''VALUES ("{0}",{1},"{2}","{3}",
                                                 "{4}","{5}","{6}","{7}",
                                                 "{8}","{9}","{10}","{11}",
                                                 "{12}");'''.format(key, value["id"], value["status"], value["project"],
                                     ','+value["labels"]+',', value["epiclink"], value["timeoriginalestimate"], value["timespent"],
                                     value["resolution"],value["issuetype"],value["summary"].replace('"', "'"),','+fixversions+',',
                                     value["parent"])
                    #value["summary"].replace('"', "'")
                    handle.write(write_str)
            except:
                logging.error("Unexpected error on key:", key, ' value:  ', value, ', error:', sys.exc_info()[0])
        handle.close()
        self.connection.commit()

    def get_sum_by_projects(self, project_filter, label_filter,fixversions_filter, group_by):  # must return arrays
        open_list= []
        dev_list= []
        close_list= []
        name_list = []
        prj_list = []
        domain_list = []
        sql_str = '''SELECT project,
                           summary,
                           SUM(CASE WHEN status IN ('Closed', 'Resolved') THEN timeoriginalestimate ELSE 0 END) close,
                           SUM(CASE WHEN status IN ('Open','New') THEN timeoriginalestimate ELSE 0 END) open,
                           SUM(CASE WHEN status IN ('Open','New','Closed', 'Resolved') THEN 0 ELSE timeoriginalestimate END) dev,
                           domain
                      FROM (
                               SELECT i.project,
                                      e.summary,
                                      i.status,
                                      i.timeoriginalestimate,
                                          CASE
                                            WHEN i.project = 'BSSARBA' THEN 'ARBA'
                                            WHEN i.project ='BSSBFAM' THEN 'Billing'
                                            WHEN i.project ='Billing' THEN 'Billing'
                                            WHEN i.project ='BSSGUS' THEN 'Billing'
                                            WHEN i.project ='BSSCRM' THEN 'CRM'
                                            WHEN i.project ='BSSCAM' THEN 'CRM'
                                            WHEN i.project ='BSSCCM'  THEN  'CRM'
                                            WHEN i.project ='BSSCPM' THEN  'Ordering'
                                            WHEN i.project ='BSSUFM' THEN  'Billing'
                                            WHEN i.project ='BSSORDER' THEN  'Ordering'
                                            WHEN i.project ='BSSCRMP' THEN  'DFE'
                                            WHEN i.project ='BSSDAPI' THEN  'DFE'
                                            WHEN i.project ='BSSSCP' THEN  'DFE'
                                            WHEN i.project ='UIKIT' THEN  'DFE'
                                            WHEN i.project ='RNDDOC' THEN  'Doc'
                                            WHEN i.project ='BSSLIS' THEN  'Billing'
                                            WHEN i.project ='BSSPRM' THEN  'PRM'
                                            WHEN i.project ='BSSPSC' THEN  'Catalog'
                                            WHEN i.project ='BSSPAY' THEN  'Billing'
                                            WHEN i.project ='BSSBOX' THEN  'BSSBOX'
                                            WHEN i.project ='NWMOCS' THEN  'NWM'
                                            ELSE '!'||i.project
                                            END domain
                                 FROM issues e
                                      LEFT JOIN
                                      issues i ON e.issue_key = i.epiclink
                                      LEFT OUTER JOIN
                                      issues st ON i.issue_key = st.parent
                                WHERE e.issuetype = "Epic" AND 
                                      st.parent IS NULL  '''
        if project_filter !='':
            sql_str = sql_str + ' AND  i.project = "'''+project_filter+'" '
        if label_filter !='':
            sql_str = sql_str + ' AND e.labels LIKE "%,'+label_filter+',%"  '
        if fixversions_filter != '':
                sql_str = sql_str + ' AND e.fixversions LIKE "%,'+fixversions_filter+',%"  '
        # add subtasks query with estimates in tasks
        sql_str = sql_str +''' UNION ALL
                                   SELECT i.project,
                                          e.summary,
                                          i.status,
                                          i.timeoriginalestimate,
                                          CASE
                                            WHEN i.project = 'BSSARBA' THEN 'ARBA'
                                            WHEN i.project ='BSSBFAM' THEN 'Billing'
                                            WHEN i.project ='Billing' THEN 'Billing'
                                            WHEN i.project ='BSSGUS' THEN 'Billing'
                                            WHEN i.project ='BSSCRM' THEN 'CRM'
                                            WHEN i.project ='BSSCAM' THEN 'CRM'
                                            WHEN i.project ='BSSCCM'  THEN  'CRM'
                                            WHEN i.project ='BSSCPM' THEN  'Ordering'
                                            WHEN i.project ='BSSUFM' THEN  'Billing'
                                            WHEN i.project ='BSSORDER' THEN  'Ordering'
                                            WHEN i.project ='BSSCRMP' THEN  'DFE'
                                            WHEN i.project ='BSSDAPI' THEN  'DFE'
                                            WHEN i.project ='BSSSCP' THEN  'DFE'
                                            WHEN i.project ='UIKIT' THEN  'DFE'
                                            WHEN i.project ='RNDDOC' THEN  'Doc'
                                            WHEN i.project ='BSSLIS' THEN  'Billing'
                                            WHEN i.project ='BSSPRM' THEN  'PRM'
                                            WHEN i.project ='BSSPSC' THEN  'Catalog'
                                            WHEN i.project ='BSSPAY' THEN  'Billing'
                                            WHEN i.project ='BSSBOX' THEN  'BSSBOX'
                                            WHEN i.project ='NWMOCS' THEN  'NWM'
                                            ELSE '!'||i.project
                                            END domain
                                     FROM issues e
                                          LEFT JOIN
                                          issues i ON e.issue_key = i.epiclink
                                    WHERE e.issuetype = "Epic" AND 
                                          0= (Select sum(st2.timeoriginalestimate) from issues st2 where i.issue_key = st2.parent) '''
        if project_filter != '':
            sql_str = sql_str + ' AND  i.project = "''' + project_filter + '" '
        if label_filter != '':
             sql_str = sql_str + ' AND e.labels LIKE "%,' + label_filter + ',%"  '
        if fixversions_filter != '':
             sql_str = sql_str + ' AND e.fixversions LIKE "%,' + fixversions_filter + ',%"  '
        # add subtasks query with estimates in Subtasks
        sql_str = sql_str +''' UNION ALL
                                   SELECT i.project,
                                          e.summary,
                                          st.status,
                                          st.timeoriginalestimate,
                                          CASE
                                            WHEN i.project = 'BSSARBA' THEN 'ARBA'
                                            WHEN i.project ='BSSBFAM' THEN 'Billing'
                                            WHEN i.project ='Billing' THEN 'Billing'
                                            WHEN i.project ='BSSGUS' THEN 'Billing'
                                            WHEN i.project ='BSSCRM' THEN 'CRM'
                                            WHEN i.project ='BSSCAM' THEN 'CRM'
                                            WHEN i.project ='BSSCCM'  THEN  'CRM'
                                            WHEN i.project ='BSSCPM' THEN  'Ordering'
                                            WHEN i.project ='BSSUFM' THEN  'Billing'
                                            WHEN i.project ='BSSORDER' THEN  'Ordering'
                                            WHEN i.project ='BSSCRMP' THEN  'DFE'
                                            WHEN i.project ='BSSDAPI' THEN  'DFE'
                                            WHEN i.project ='BSSSCP' THEN  'DFE'
                                            WHEN i.project ='UIKIT' THEN  'DFE'
                                            WHEN i.project ='RNDDOC' THEN  'Doc'
                                            WHEN i.project ='BSSLIS' THEN  'Billing'
                                            WHEN i.project ='BSSPRM' THEN  'PRM'
                                            WHEN i.project ='BSSPSC' THEN  'Catalog'
                                            WHEN i.project ='BSSPAY' THEN  'Billing'
                                            WHEN i.project ='BSSBOX' THEN  'BSSBOX'
                                            WHEN i.project ='NWMOCS' THEN  'NWM'
                                            ELSE '!'||i.project
                                            END domain
                                     FROM issues e
                                          LEFT JOIN
                                          issues i ON e.issue_key = i.epiclink
                                          LEFT JOIN
                                          issues st ON i.issue_key = st.parent
                                    WHERE e.issuetype = "Epic" AND 
                                          st.parent IS NOT NULL  AND 
                                          0< (Select sum(st2.timeoriginalestimate) from issues st2 where i.issue_key = st2.parent)'''
        if project_filter != '':
            sql_str = sql_str + ' AND  i.project = "''' + project_filter + '" '
        if label_filter != '':
             sql_str = sql_str + ' AND e.labels LIKE "%,' + label_filter + ',%"  '
        if fixversions_filter != '':
             sql_str = sql_str + ' AND e.fixversions LIKE "%,' + fixversions_filter + ',%"  '
        sql_str = sql_str + ' ) GROUP BY ' + group_by +' HAVING SUM(timeoriginalestimate) > 0 '

        for row in self.cursor.execute(sql_str):
            prj_list.append(row[0] if row[0] is not None else "")
            name_list.append(row[1])
            close_list.append(round(row[2]))
            open_list.append(round(row[3]))
            dev_list.append(round(row[4]) if row[4] is not None else 0)
            domain_list.append(row[5])

        return open_list, dev_list, close_list, name_list, prj_list, domain_list

    # By @alanbryn
    def get_bugs_duration(self, label_filter, priority_filter, creators_filter):
        project_list = []
        name_list = []
        components_list = []
        created_list = []
        resolutiondate_list = []
        sql_str = '''SELECT project,
                            summary,
                            created,
                            resolutiondate,
                            components
                     FROM issues
                     WHERE issuetype = "Bug" AND 
                           status IN ('Closed', 'Resolved') AND
                           resolution IN ('Fixed', 'Done')'''
        if label_filter != '':
            sql_str = sql_str + ' AND labels LIKE \'%' + label_filter + '%\''
        if priority_filter != '':
            sql_str = sql_str + ' AND priority LIKE \'%' + priority_filter + '%\''

        creator_dict = creators_filter.split(',')
        creator_dict = [item.strip() for item in creator_dict]

        if creators_filter != '':
            sql_str = sql_str + ' AND creator IN ('
            for creator in creator_dict:
                sql_str = sql_str + '\'' + creator + '\''
                if creator != creator_dict[-1]:
                    sql_str = sql_str + ', '
                else:
                    sql_str = sql_str + ')'
        sql_str = sql_str + ' ORDER BY components'

        for row in self.cursor.execute(sql_str):
            project_list.append(row[0])
            name_list.append(row[1])
            created_list.append(row[2])
            resolutiondate_list.append(row[3])
            components_list.append(row[4])

        return project_list, name_list, created_list, resolutiondate_list, components_list

    # By @alanbryn
    def get_arba_issues(self, assignees_filter):
        name_list = []
        assignee_list = []
        created_list = []
        duedate_list = []
        sql_str = '''SELECT summary,
                            assignee,
                            created,
                            duedate
                     FROM issues
                     WHERE project IN ('BSSBOX', 'BSSARBA') AND
                           issuetype IN ('Task', 'Sub-task', 'Bug') AND
                           status = 'Dev' AND
                           duedate IS NOT NULL'''
        if assignees_filter != '':
            sql_str = sql_str + ' AND assignee IN ('
            for assignee in assignees_filter.split(', '):
                sql_str = sql_str + '\'' + assignee + '\''
                if assignee != assignees_filter.split(', ')[-1]:
                    sql_str = sql_str + ', '
                else:
                    sql_str = sql_str + ')'
        sql_str = sql_str + ' ORDER BY assignee'

        for row in self.cursor.execute(sql_str):
            name_list.append(row[0])
            assignee_list.append(row[1])
            created_list.append(row[2])
            duedate_list.append(row[3])

        return name_list, assignee_list, created_list, duedate_list
