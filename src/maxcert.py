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
    def writeHostFile(cls,filename='/tmp/maxcert-hosts.txt'):
        f = open(filename, 'w')
        for route in Route.all():
            f.write(route.host)
            f.write(os.linesep)
        f.truncate(f.tell() - len(os.linesep))
        f.close()    
    
    def __init__(self, project, route, host):
        self.project = project
        self.route = route
        self.host = host
        Route.add(self)

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
