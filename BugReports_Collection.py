import requests
import os
from bs4 import BeautifulSoup
import pickle
import time

reportData = []
request_url = "https://issues.apache.org/jira/sr/jira.issueviews:searchrequest-xml/temp/SearchRequest.xml"

# configFormat = "project = {} AND status = Closed AND resolution = Fixed AND issuetype = Bug ORDER BY key ASC"
configFormat = "project = {} AND resolution = Fixed AND issuetype = Bug ORDER BY key ASC"

bugReportRoot = "bugReport/"

def get_by_url(url, project, start):
    config = {"jqlQuery": configFormat.format(project),
              "tempMax": 1000,
              "pager/start": start}
    r = requests.get(url, params=config)
    print(r.url)
    if r.status_code == 200:
        reponse_xml = r.text
        with open(os.path.join(bugReportRoot, "report.xml"), "w", encoding="utf-8") as fw:
            fw.write(reponse_xml)
        with open(os.path.join(bugReportRoot, ("report_start_" + str(start) + ".xml")), "w", encoding="utf-8") as fw:
            fw.write(reponse_xml)
        return True
    return False

def main(project):
    bugProjectName = project.upper()
    global bugReportRoot, reportData
    bugReportRoot = os.path.join(bugReportRoot, project+"/")
    if not os.path.exists(bugReportRoot):
        os.mkdir(bugReportRoot)
    start = 0
    while True:
        if get_by_url(request_url, bugProjectName, start):
            soup = BeautifulSoup(open(os.path.join(bugReportRoot, "report.xml"), 'r', encoding='UTF-8'), "lxml")
            if len(soup.find_all('item'))==0:
                break
            s = soup.issue['start']
            e = soup.issue['end']
            t = soup.issue['total']
            print(project, ": start=",s,", end=", e, ", total=", t, "\n")
            for item in soup.find_all('item'):
                temp = {}
                temp['priority'] = ''
                temp['key'] = item.key.text
                temp['title'] = item.title.text
                temp['description'] = item.description.text
                temp['type'] = item.type.text
                if item.priority:
                    temp['priority'] = item.priority.text
                temp['status'] = item.status.text
                temp['resolution'] = item.resolution.text
                temp['created'] = item.created.text
                temp['resolved'] = item.resolved.text
                reportData.append(temp)
            start += 1000
            time.sleep(30)
        else:
            break
    with open(os.path.join(bugReportRoot, "bugId.csv"), "a+", encoding="utf-8") as fw:
        for item in reportData:
            fw.write(item['key'] + ',' + item['type'] + ',' + item['status'] + ',' + item['resolution'] + "\n")
    pickle.dump(reportData, open(os.path.join(bugReportRoot, "reportData.pickle"), "wb"))

if __name__ == "__main__":
    main("ZOOKEEPER")
