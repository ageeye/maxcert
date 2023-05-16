import time, os
import openshift as oc

print("cron started")

# get projects
projects = oc.selector('projects').objects()

# get routes
for project in projects:
    name = project.name()
    print("switch to project", name)
    with oc.project(name):
        routes = oc.selector('route', labels={'certbot-managed':'true'})
        for route in routes.objects():
            data = route.as_dict()
            host = data['spec']['host']
            print('-', route.name(), host)

while os.environ['MAXCERT_CRON']=='false':
    time.sleep(60 * 60)
    print("cron wake up")