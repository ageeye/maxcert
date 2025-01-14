import os
import openshift_client as oc

class Route:

    routes = {}
    csv = {}

    @classmethod
    def fetch(cls):
        return oc.selector('route').objects()
   
    @classmethod
    def add(cls, route, project):
        if project not in cls.routes:
           cls.routes[project] = [] 
        cls.routes[project].append(route)

    @classmethod
    def all(cls, project):
        return cls.routes[project]
        
    @classmethod
    def setENV(cls, project):
        self.cmd('CERTIFICATE="$(awk \'{printf "%s\\n", $0}\' ' + '/etc/letsencrypt/live/'+project+'/cert.pem)')
        self.cmd('KEY="$(awk \'{printf "%s\\n", $0}\' ' + '/etc/letsencrypt/live/'+project+'/privkey.pem)')
        self.cmd('CABUNDLE="$(awk \'{printf "%s\\n", $0}\' ' + '/etc/letsencrypt/live/'+project+'/fullchain.pem)')
        
    @classmethod
    def cleanHostFiles(cls):    
        os.system('rm /tmp/*')

    @classmethod
    def writeHostFile(cls, project, filename='/tmp/hosts_'):
        filename = filename + project
        filetype = {'txt': os.linesep, 'csv': ','}
        for suffix in filetype:
            f = open(filename + '.' + suffix, 'a+')
            routes = [r.host for r in Route.all(project)]
            routes = set(routes)
            for route in routes:
                f.write(route)
                f.write(filetype[suffix])
            f.truncate(f.tell() - len(filetype[suffix]) )
            if (suffix=='csv'):
                f.seek(0)
                cls.csv[project] = f.read()
            f.close()    
    
    def __init__(self, project, route, host):
        self.project = project
        self.route = route
        self.host = host
        Route.add(self, project)

    def setHost(self, host):
        with oc.project(self.project):
            obj = oc.selector('route/' + self.route).object()
            obj.model.spec['host'] = host
            obj.apply()

    def setTmpHost(self):
        self.setHost('tmp-maxcert-' + self.host)

    def restoreHost(self):
        self.setHost(self.host)
        
    def cmd(self, c):
        os.system(c)
        
    def patchRoute(self):
        self.cmd("oc patch \"route/"+self.route+"\" -p '{\"spec\":{\"tls\":{\"certificate\":\"'\"${CERTIFICATE}\"'\",\"key\":\"'\"${KEY}\"'\",\"caCertificate\":\"'\"${CABUNDLE}\"'\"}}}'")

        

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
        
    @classmethod
    def has(cls, name):
        return name in os.environ

class AcmeChallenge:

    def __init__(self, base, project):
        self.base = base
        self.project = project  
        
    def cmd(self, c):
        os.system(c)
        
    def setBase(self):
        self.cmd('oc project ' + self.base)      

    def start(self):
        self.setBase()
        self.cmd('oc create -f /ocp/maxcert_np.yaml')
        self.cmd('oc create -f /ocp/maxcert_svc.yaml')
        self.cmd("cat /tmp/hosts_"+self.project+".txt | xargs -n 1 -I {} oc process -f /ocp/maxcert-route.yaml -p 'NAME=acme-challenge-{}' -p 'HOST={}' | oc create -f -")

    def getcert(self):
        self.setBase()
        self.cmd("certbot --config /bot/certbot.ini certonly --server https://acme-v02.api.letsencrypt.org/directory --allow-subset-of-names --non-interactive --keep-until-expiring --cert-name " + self.project + " --expand --standalone -d " + Route.csv[self.project])

    def cleanup(self):
        self.setBase()
        self.cmd('oc delete route,svc,networkpolicy -l app=maxcert,well-known=acme-challenge')