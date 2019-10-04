WITH user_stories AS (
	SELECT us.ID, us.[Key], us.[Issue type], CONCAT('{', STRING_AGG(us.Estimate, ', '), '}') AS 'Estimate', us.[Spent time], us.Component, us.[Status], us.Feature, us.[Feature name], us.FL, us.[Due date]
	FROM (
		SELECT us_ji.ID AS 'ID', CONCAT_WS('-', us_prj.pkey, us_ji.issuenum) AS 'Key', us_it.pname AS 'Issue type', (CASE WHEN bulks.Estimate IS NULL THEN '' ELSE CONCAT('"', bulks.Component, '": "', bulks.Estimate, '"') END) AS 'Estimate',
			NULL AS 'Spent time', NULL AS 'Component', us_is.pname AS 'Status', NULL AS 'Feature', us_ji.SUMMARY AS 'Feature name', us_pm.STRINGVALUE AS 'FL', CONVERT(varchar, FORMAT(CONVERT(date, us_ji.DUEDATE), 'dd.MM.yyyy')) AS 'Due date'
		FROM [srv-jira-prod-report].[dbo].[jiraissue] AS us_ji
			INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS us_it ON us_it.ID = us_ji.issuetype
			INNER JOIN [srv-jira-prod-report].[dbo].[project] AS us_prj ON us_prj.ID = us_ji.PROJECT
			INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS us_is ON us_is.ID = us_ji.issuestatus
			LEFT JOIN (
				SELECT uspm_cfv.ISSUE, uspm_cfv.STRINGVALUE
				FROM [srv-jira-prod-report].[dbo].[customfieldvalue] AS uspm_cfv
					INNER JOIN [srv-jira-prod-report].[dbo].[customfield] AS uspm_cf ON uspm_cf.ID = uspm_cfv.CUSTOMFIELD
				WHERE uspm_cf.cfname = 'Project manager') AS us_pm ON us_pm.ISSUE = us_ji.ID
			LEFT JOIN (
				SELECT be.ISSUE_ID, be.[VALUE] AS 'Estimate', cmp.cname AS 'Component'
				FROM [srv-jira-prod-report].[dbo].[AO_983835_BE_ITEM] AS be
					INNER JOIN [srv-jira-prod-report].[dbo].[component] AS cmp ON cmp.ID = be.COMPONENT_ID) AS bulks ON bulks.ISSUE_ID = us_ji.ID
			INNER JOIN [srv-jira-prod-report].[dbo].[label] AS us_lbl ON us_lbl.ISSUE = us_ji.ID
		WHERE us_prj.pname = 'BSSBOX' AND us_it.pname = 'User Story (L3)' AND us_is.pname != 'Canceled' AND us_lbl.LABEL = 'Pilot2.0') AS us
	GROUP BY us.ID, us.[Key], us.[Issue type], us.[Spent time], us.Component, us.[Status], us.Feature, us.[Feature name], us.FL, us.[Due date]),
epics AS (
	SELECT e_ji.ID AS 'ID', epics_cmp.Component AS 'Component', user_stories.[Key] AS 'Feature', user_stories.[Feature name] AS 'Feature name', user_stories.FL AS 'FL', CONVERT(varchar, FORMAT(CONVERT(date, e_ji.DUEDATE), 'dd.MM.yyyy')) AS 'Due date'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS e_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS e_il ON e_il.DESTINATION = e_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS e_ilt ON e_ilt.ID = e_il.LINKTYPE
		INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS e_ist ON e_ist.ID = e_ji.issuestatus
		LEFT JOIN (
			SELECT ec_ji.ID AS 'ID', ec_cmp.cname AS 'Component'
			FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ec_ji
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS ec_il ON ec_il.DESTINATION = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS ec_ilt ON ec_ilt.ID = ec_il.LINKTYPE
				INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS ec_na ON ec_na.SOURCE_NODE_ID = ec_ji.ID
				INNER JOIN [srv-jira-prod-report].[dbo].[component] AS ec_cmp ON ec_cmp.ID = ec_na.SINK_NODE_ID
			WHERE ec_ilt.LINKNAME = 'nexign_hierarchy_link' AND ec_il.SOURCE IN (SELECT ID FROM user_stories) AND ec_na.ASSOCIATION_TYPE = 'IssueComponent') AS epics_cmp ON epics_cmp.ID = e_ji.ID
		INNER JOIN user_stories ON user_stories.ID = e_il.SOURCE
	WHERE e_ilt.LINKNAME = 'nexign_hierarchy_link' AND e_il.SOURCE IN (SELECT ID FROM user_stories) AND e_ist.pname != 'Canceled'),
tasks AS (
	SELECT t_ji.ID AS 'ID', CONCAT_WS('-', t_prj.pkey, t_ji.issuenum) AS 'Key', t_it.pname AS 'Issue type',
		CAST((CASE WHEN t_ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE t_ji.TIMEORIGINALESTIMATE END) AS nvarchar(max)) AS 'Estimate',
		CAST((CASE WHEN t_ji.TIMESPENT IS NULL THEN 0 ELSE t_ji.TIMESPENT END) AS nvarchar(max)) AS 'Spent time',
		(CASE WHEN epics.Component IS NULL THEN '' ELSE epics.Component END) AS 'Component',
		(CASE WHEN t_is.pname IN ('Open', 'New', 'Reopen') THEN 'Open' WHEN t_is.pname IN ('Closed', 'Resolved', 'Done') THEN 'Done' ELSE 'Dev' END)  AS 'Status',
		epics.Feature AS 'Feature', epics.[Feature name] AS 'Feature name', epics.FL AS 'FL', epics.[Due date] AS 'Due date'
	FROM [srv-jira-prod-report].[dbo].[jiraissue] AS t_ji
		INNER JOIN [srv-jira-prod-report].[dbo].[project] AS t_prj ON t_prj.ID = t_ji.PROJECT
		INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS t_it ON t_it.ID = t_ji.issuetype
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS t_il ON t_il.DESTINATION = t_ji.ID
		INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS t_ilt ON t_ilt.ID = t_il.LINKTYPE
		INNER JOIN epics ON epics.ID = t_il.SOURCE
		INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS t_is ON t_is.ID = t_ji.issuestatus
	WHERE t_it.pname != 'Bug' AND t_ilt.LINKNAME = 'Epic-Story Link' AND t_il.SOURCE IN (SELECT ID FROM epics) AND t_is.pname != 'Canceled')

SELECT user_stories.ID, user_stories.[Key], user_stories.[Issue type], user_stories.Estimate, user_stories.[Spent time], user_stories.Component, user_stories.[Status], user_stories.Feature, user_stories.[Feature name], user_stories.FL,
	(CASE WHEN user_stories.[Due date] IS NULL THEN (CASE WHEN dd.[Due date] IS NULL THEN 'not duedated' ELSE dd.[Due date] END) ELSE user_stories.[Due date] END) AS 'Due date'
FROM user_stories
	LEFT JOIN (SELECT Feature, max([Due date]) AS 'Due date' FROM epics GROUP BY Feature) AS dd ON dd.Feature = user_stories.[Key]
UNION ALL
SELECT * FROM tasks
UNION ALL
SELECT st_ji.ID AS 'ID', CONCAT_WS('-', st_prj.pkey, st_ji.issuenum) AS 'Key', st_it.pname AS 'Issue type',
	CAST((CASE WHEN st_ji.TIMEORIGINALESTIMATE IS NULL THEN 0 ELSE st_ji.TIMEORIGINALESTIMATE END) AS nvarchar(max)) AS 'Estimate',
	CAST((CASE WHEN st_ji.TIMESPENT IS NULL THEN 0 ELSE st_ji.TIMESPENT END) AS nvarchar(max)) AS 'Spent time' ,
	(CASE WHEN tasks.Component IS NULL THEN '' ELSE tasks.Component END) AS 'Component',
	(CASE WHEN st_is.pname IN ('Open', 'New', 'Reopen') THEN 'Open' WHEN st_is.pname IN ('Closed', 'Resolved', 'Done') THEN 'Done' ELSE 'Dev' END)  AS 'Status',
	tasks.Feature AS 'Feature', tasks.[Feature name] AS 'Feature name', tasks.FL AS 'FL', tasks.[Due date] AS 'Due date'
FROM [srv-jira-prod-report].[dbo].[jiraissue] AS st_ji
	INNER JOIN [srv-jira-prod-report].[dbo].[project] AS st_prj ON st_prj.ID = st_ji.PROJECT
	INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS st_it ON st_it.ID = st_ji.issuetype
	INNER JOIN [srv-jira-prod-report].[dbo].[issuelink] AS st_il ON st_il.DESTINATION = st_ji.ID
	INNER JOIN [srv-jira-prod-report].[dbo].[issuelinktype] AS st_ilt ON st_ilt.ID = st_il.LINKTYPE
	INNER JOIN tasks ON tasks.ID = st_il.SOURCE
	INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS st_is ON st_is.ID = st_ji.issuestatus
WHERE st_it.pname != 'Sub-bug' AND st_ilt.LINKNAME = 'jira_subtask_link' AND st_il.SOURCE IN (SELECT ID FROM tasks) AND st_is.pname != 'Canceled'
ORDER BY Feature, FL