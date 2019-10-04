SELECT CONCAT_WS('-', prj_b.pkey, ji_b.issuenum) AS 'Key', ji_b.SUMMARY AS 'Summary', (CASE WHEN ji_b.ASSIGNEE IS NOT NULL THEN ji_b.ASSIGNEE ELSE '' END) AS 'Assignee',
    pr_b.pname AS 'Priority', ist_b.pname AS 'Status', component.component AS 'Domain', (CASE WHEN ji_b.DUEDATE IS NULL THEN '' ELSE CONVERT(varchar, FORMAT(CONVERT(date, ji_b.DUEDATE), 'dd.MM.yyyy')) END) AS 'Due date', ji_b.CREATED AS 'Days in progress', ji_b.RESOLUTIONDATE AS 'Resolved'
FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji_b
	INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj_b ON prj_b.ID = ji_b.PROJECT
	INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it_b ON it_b.ID = ji_b.issuetype
	INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS ist_b ON ist_b.ID = ji_b.issuestatus
	INNER JOIN [srv-jira-prod-report].[dbo].[priority] AS pr_b ON pr_b.ID = ji_b.PRIORITY
	INNER JOIN (
		SELECT pp_ji.ID
		FROM [srv-jira-prod-report].[dbo].[label] AS pp_lbl
			INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS pp_ji ON pp_ji.ID = pp_lbl.ISSUE
		WHERE pp_lbl.LABEL = 'Pilot2.0') AS us_pp ON us_pp.ID = ji_b.ID
	FULL JOIN (
		SELECT CONCAT_WS('-', prj_c.pkey, ji_c.issuenum) AS 'jira_key', cmp_c.cname AS 'component'
		FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji_c
			INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj_c ON prj_c.ID = ji_c.PROJECT
			INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it_c ON it_c.ID = ji_c.issuetype
			INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS ist_c ON ist_c.ID = ji_c.issuestatus
			INNER JOIN [srv-jira-prod-report].[dbo].[priority] AS pr_c ON pr_c.ID = ji_c.PRIORITY
			INNER JOIN (
				SELECT pp_ji.ID
				FROM [srv-jira-prod-report].[dbo].[label] AS pp_lbl
					INNER JOIN [srv-jira-prod-report].[dbo].[jiraissue] AS pp_ji ON pp_ji.ID = pp_lbl.ISSUE
				WHERE pp_lbl.LABEL = 'Pilot2.0') AS us_pp ON us_pp.ID = ji_c.ID
			INNER JOIN [srv-jira-prod-report].[dbo].[nodeassociation] AS na_c ON na_c.SOURCE_NODE_ID = ji_c.ID
			INNER JOIN [srv-jira-prod-report].[dbo].[component] AS cmp_c ON cmp_c.ID = na_c.SINK_NODE_ID
		WHERE prj_c.pname = 'BSSBOX'
			AND it_c.pname = 'Bug'
			AND pr_c.pname IN ('Critical', 'Blocker')
			AND na_c.ASSOCIATION_TYPE = 'IssueComponent'
	) AS component ON component.jira_key = CONCAT_WS('-', prj_b.pkey, ji_b.issuenum)
WHERE prj_b.pname = 'BSSBOX'
	AND it_b.pname = 'Bug'
	AND pr_b.pname IN ('Critical', 'Blocker')
ORDER BY 'Priority', 'Days in progress'