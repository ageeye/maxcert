import time
from maxcert import Project, Route, Environment, AcmeChallenge

if not Environment.get('MAXCERT_MODE')=='debug':

    print("cron started")

    # get projects
    base = Environment.get('MAXCERT_PROJECT')
    projects = Project.init()
    projects.remove(base)

    # set email
    if Environment.has('MAXCERT_MAIL'):
        mail = Environment.get('MAXCERT_MAIL')
        with open('/bot/certbot.ini', 'a') as fd:
            fd.write(f'email = {mail}\n')

    # get routes
    Route.cleanHostFiles()
    for project in projects:
        print('switch to project', project)
        with Project.select(project):
            for route in Route.fetch():
                data = route.as_dict()
                name = route.name()
                host = data['spec']['host']
                Route(project, name, host)
                print('-', name, host)
            Route.writeHostFile(project)


    for project in projects:
        print('switch to project', project)
        for route in Route.all(project):
            route.setTmpHost()  
            
        acme = AcmeChallenge(base, project)
        acme.start()
        acme.getcert()
        acme.cleanup()
            
        for route in Route.all(project):
            route.restoreHost()

while Environment.get('MAXCERT_CRON')=='false':
    time.sleep(60 * 60)
    print("cron wake up")