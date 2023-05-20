import time, os
import openshift as oc
import maxcert as mc

print("cron started")

# get projects
base = os.environ['MAXCERT_PROJECT']
projects = oc.selector('projects').names()
projects.remove(base)

# get routes
for project in projects:
    print("switch to project", project)
    with oc.project(project):
        routes = oc.selector('route')
        for route in routes.objects():
            data = route.as_dict()
            name = route.name()
            host = data['spec']['host']
            mc.Route(project, name, host)
            print('-', name, host)

mc.Routes.writeHostFile()

while os.environ['MAXCERT_CRON']=='false':
    time.sleep(60 * 60)
    print("cron wake up")