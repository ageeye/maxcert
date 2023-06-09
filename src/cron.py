import time
from maxcert import Project, Route, Environment, AcmeChallenge

print("cron started")

# get projects
base = Environment.get('MAXCERT_PROJECT')
projects = Project.init()
projects.remove(base)

# get routes
for project in projects:
    print('switch to project', project)
    with Project.select(project):
        for route in Route.fetch():
            data = route.as_dict()
            name = route.name()
            host = data['spec']['host']
            Route(project, name, host)
            print('-', name, host)

Route.writeHostFile()

"""
# route = Route.all()[0]
for route in Route.all():
    route.setTmpHost()

for route in Route.all():
    route.restoreHost()
"""

while Environment.get('MAXCERT_CRON')=='false':
    time.sleep(60 * 60)
    print("cron wake up")