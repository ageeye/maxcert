import time
from maxcert import Project, Route, Environment, AcmeChallenge

def getProjects(base):
    """
    Retrieve a list of projects, excluding the specified base project.

    Args:
        base (str): The base project to be excluded from the list.

    Returns:
        list: A list of projects excluding the base project.
    """
    projects = Project.init()
    if base in projects:
        projects.remove(base)
    return projects    

def setMail():
    """
    Set the email address for the certificate.

    Returns:
        str: The email address for the certificate.
    """
    mail = Environment.get('MAXCERT_MAIL')
    with open('/bot/certbot.ini', 'a') as fd:
        fd.write(f'email = {mail}\n')
    return mail

def getRoutes(projects):
    """
    Processes a list of projects to fetch and handle route information.

    Args:
        projects (list): A list of project names to process.

    Returns:
        None
    """
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

if not Environment.get('MAXCERT_MODE')=='debug':

    print("cron started")

    base = Environment.get('MAXCERT_PROJECT')
    projects = getProjects(base)

    setMail()
    getRoutes(projects)

    # ToDo: code review
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