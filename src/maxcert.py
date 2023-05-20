import os

class Route:

    routes = []
    
    @classmethod
    def addRoute(cls, route):
        cls.routes.append(route)

    @classmethod
    def getRoutes(cls):
        return cls.routes

    @classmethod
    def getRoutes(cls):
        return cls.routes

    @classmethod
    def writeHostFile(cls,filename='/tmp/maxcert-hosts.txt'):
        f = open(filename, 'w')
        for route in Route.getRoutes():
            f.write(route.host)
            f.write(os.linesep)
        f.truncate(f.tell() - len(os.linesep))
        f.close()    
    
    def __init__(self, project, route, host):
        self.project = project
        self.route = route
        self.host = host
        Route.addRoute(self)