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
                               resolution TEXT, issuetype TEXT, summary TEXT, fixversions TEXT, parent TEXT)''')

        self.connection.commit()

    def insert_issues(self, issues):
        if len(issues) == 0:
            return

        for key, value in issues.items():
            try:
                if "fixversions" in value:
                    fixversions = value["fixversions"]
                else:
                    fixversions = ""
                sql_str = '''INSERT INTO issues (issue_key, id, status, project,
                                        labels, epiclink, timeoriginalestimate, timespent,
                                       resolution, issuetype, summary, fixversions, 
                                       parent)'''
                self.cursor.execute(sql_str + ''' VALUES (?,?,?,?,
                                                 ?,?,?,?,
                                                 ?,?,?,?,
                                                 ?)''',
                                    (key, value["id"], value["status"], value["project"],
                                     ','+value["labels"]+',', value["epiclink"], value["timeoriginalestimate"], value["timespent"],
                                     value["resolution"],value["issuetype"],value["summary"],','+fixversions+',',
                                     value["parent"],))
                if value["project"] == '!BSSGUS' :
                    logging.debug(sql_str +'''VALUES ("%s",%s,"%s","%s",
                                                 "%s","%s","%s","%s",
                                                 "%s","%s","%s","%s",
                                                 "%s");''', key, value["id"], value["status"], value["project"],
                                     ','+value["labels"]+',', value["epiclink"], value["timeoriginalestimate"], value["timespent"],
                                     value["resolution"],value["issuetype"],value["summary"].replace('"', "'"),','+fixversions+',',
                                     value["parent"])
            except:
                logging.error("Unexpected error on key:", key, ' value:  ', value, ', error:', sys.exc_info()[0])

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
        # add subtasks query
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
                                          st.parent IS NOT NULL  '''
        if project_filter != '':
            sql_str = sql_str + ' AND  i.project = "''' + project_filter + '" '
        if label_filter != '':
             sql_str = sql_str + ' AND e.labels LIKE "%,' + label_filter + ',%"  '
        if fixversions_filter != '':
             sql_str = sql_str + ' AND e.fixversions LIKE "%,' + fixversions_filter + ',%"  '
        sql_str = sql_str + ' ) GROUP BY ' + group_by + ' ORDER BY domain, project, summary'

        for row in self.cursor.execute(sql_str):
            prj_list.append(row[0] if row[0] is not None else "")
            name_list.append(row[1])
            close_list.append(round(row[2]))
            open_list.append(round(row[3]))
            dev_list.append(round(row[4]) if row[4] is not None else 0)
            domain_list.append(row[5])

        return open_list, dev_list, close_list, name_list, prj_list, domain_list

    # By @alanbryn
    def get_bugs_duration(self, label_filter, priority_filter):
        project_list = []
        name_list = []
        domain_list = []
        created_list = []
        resolutiondate_list = []
        sql_str = '''SELECT project,
                            summary,
                            created,
                            resolutiondate,
                            CASE
                                WHEN (components LIKE 'CES') OR (components LIKE '%BFAM%')
                                    OR (components LIKE '%Charge Events Storage%') OR (components LIKE '%Billing%')
                                    OR (components LIKE '%SPP%') OR (components LIKE '%Payment%')
                                    OR (components LIKE '%Collection%') OR (components LIKE '%ogical%nventory%')
                                    OR (components LIKE '%UFM%') THEN 'Billing'
                                WHEN (components LIKE '%Party Management%') OR (components LIKE '%Searching%')
                                    OR (components LIKE '%CRM Processes%') OR (components LIKE '%Interactions%')
                                    OR (components LIKE '%Processes engine%')
                                    OR (components LIKE '%Process Management%') OR (components LIKE '%Loyalty%')
                                    THEN 'CRM'
                                WHEN (components LIKE '%CSR Portal%') OR (components LIKE '%Partners portal%')
                                    OR (components LIKE '%DFE%') OR (components LIKE '%Common%')
                                    OR (components LIKE '%Admin UI%') THEN 'DFE'
                                WHEN (components LIKE '%Infra%') OR (components LIKE '%Message Bus%')
                                    OR (components LIKE '%SSO%') OR (components LIKE '%Security%')
                                    OR (components LIKE '%Notification%') OR (components LIKE '%Report Engine%')
                                    THEN 'Infra'
                                WHEN (components LIKE '%NWM%') OR (components LIKE '%Network Monetization%') THEN 'NWM'
                                WHEN (components LIKE '%Marketplace%') OR (components LIKE '%Product Instances%')
                                    OR (components LIKE '%Inventory%') OR (components LIKE '%Ordering%')
                                    OR (components LIKE '%Customer Order%') OR (components LIKE '%CRAB_AKKA%')
                                    THEN 'Ordering'
                                WHEN (components LIKE '%Partner Management%') OR (components LIKE '%PRM%') THEN 'PRM'
                                WHEN (components LIKE '%Product Catalog%') OR (components LIKE '%PSC%')
                                    OR (components LIKE '%Ref%Data%') THEN 'PSC'
                                WHEN components LIKE '' THEN 'COMPONENTS FIELD HAS NOT BEEN FILLED'
                                ELSE 'OTHERS'
                            END domains
                     FROM issues
                     WHERE issuetype = "Bug" AND 
                           status IN ('Closed', 'Resolved') AND
                           resolution IN ('Fixed', 'Done') AND
                           creator IN ('Alla.Denisova', 'APredtechensky', 'Danila.Nazarenko', 'Polina.Bednyakova', 
                                'Andrey.Karpenko', 'Denis.Sharov', 'Daniil.Shchukin', 'Mariya.Shibanova',
                                'Valentin.Sitnik', 'Aleksey.Zabelin', 'Sergey.Filyanin', 'Sergey.Borodkin',
                                'Dmitry.Ganin', 'Yuriy.Ivanov', 'Vitaly.Osipov', 'Stanislav.Prikhodko',
                                'Vladimir.Barkov', 'Vladimir.Likhtansky', 'Vitaly.Mamykin', 'Alexey.Savchkov',
                                'Yevgeny.Tokar') '''
        if label_filter != '':
            sql_str = sql_str + ' AND labels LIKE \'%' + label_filter + '%\''
        if priority_filter != '':
            sql_str = sql_str + ' AND priority LIKE \'%' + priority_filter + '%\''
        sql_str = sql_str + ' ORDER BY domains'

        for row in self.cursor.execute(sql_str):
            project_list.append(row[0])
            name_list.append(row[1])
            created_list.append(row[2])
            resolutiondate_list.append(row[3])
            domain_list.append(row[4])

        return project_list, name_list, created_list, resolutiondate_list, domain_list
