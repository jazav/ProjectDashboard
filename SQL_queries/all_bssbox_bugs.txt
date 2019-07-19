SELECT CONCAT_WS('-', prj.pkey, ji.issuenum) AS 'Key', ist.pname AS 'Status', ji.RESOLUTIONDATE AS 'Resolution date'
FROM [srv-jira-prod-report].[dbo].[jiraissue] AS ji
    INNER JOIN [srv-jira-prod-report].[dbo].[project] AS prj ON prj.ID = ji.PROJECT
	INNER JOIN [srv-jira-prod-report].[dbo].[issuetype] AS it ON it.ID = ji.issuetype
	INNER JOIN [srv-jira-prod-report].[dbo].[issuestatus] AS ist ON ist.ID = ji.issuestatus
WHERE prj.pname = 'BSSBOX'
	AND it.pname = 'Bug'