import os
import openshift as oc

class Route:

    routes = []

    @classmethod
    def fetch(cls):
        return oc.selector('route').objects()
   
    @classmethod
    def add(cls, route):
        cls.routes.append(route)

    @classmethod
    def all(cls):
        return cls.routes

    @classmethod
    def writeHostFile(cls, filename='/tmp/maxcert-hosts'):
        filetype = {'txt': os.linesep, 'csv': ','}
        for suffix in filetype:
            f = open(filename + '.' + suffix, 'w')
            routes = [r.host for r in Route.all()]
            routes = set(routes)
            for route in routes:
                f.write(route)
                f.write(filetype[suffix])
            f.truncate(f.tell() - len(filetype[suffix]) )
            f.close()    
    
    def __init__(self, project, route, host):
        self.project = project
        self.route = route
        self.host = host
        Route.add(self)

    def save(self, filename='/tmp/maxcert-tmphost.txt'):
        f = open(filename, 'w')
        f.write(self.host)
        f.close()

    def setHost(self, host):
        with oc.project(self.project):
            obj = oc.selector('route/' + self.route).object()
            obj.model.spec['host'] = host
            obj.apply()

    def setTmpHost(self):
        self.setHost('tmp-maxcert-' + self.host)

    def restoreHost(self):
        self.setHost(self.host)

class Project:

    projects = []
    
    @classmethod
    def add(cls, project):
        cls.projects.append(project)
       
    @classmethod
    def sub(cls, project):
        cls.projects.remove(project)

    @classmethod
    def all(cls):
        return cls.projects

    @classmethod
    def init(cls):
        cls.projects = oc.selector('projects').names()
        return cls.projects

    @classmethod
    def select(cls, project):
        if project in cls.projects:
            return oc.project(project)
        else:
            raise Exception('Sorry, missing project', project, '.')

class Environment:

    @classmethod
    def get(cls, name):
        return os.environ[name]

class AcmeChallenge:

    @classmethod
    def start(cls, project):
        os.system('oc project ' + project)
        os.system('oc create -f /ocp/maxcert_np.yaml')
        os.system('oc create -f /ocp/maxcert_svc.yaml')
        os.system("cat /tmp/maxcert-hosts.txt | xargs -n 1 -I {} oc process -f /ocp/maxcert-route.yaml -p 'NAME=acme-challenge-{}' -p 'HOST={}' | oc create -f -")

    @classmethod
    def cleanup(cls, project):
        os.system('oc project ' + project)
        os.system('oc delete route,svc,networkpolicy -l app=maxcert,well-known=acme-challenge')