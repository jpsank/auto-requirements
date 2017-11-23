import os
import ast
import subprocess
import sys


class REQER:
    def __init__(self,REQ_TXT_FN="requirements.txt"):
        self.MODULES = subprocess.Popen("pip freeze", stdout=subprocess.PIPE).stdout.read().decode().replace("\r\n", "\n")
        self.MODULES = [m.split("==") for m in self.MODULES.split("\n") if "==" in m]
        self.MODULES = {p[0]:p[1] for p in self.MODULES}

        self.REQ_TXT_FN = REQ_TXT_FN

    def get_imports(self,path):
        with open(path) as fh:
            try:
                root = ast.parse(fh.read(), path)
            except UnicodeDecodeError:
                root = ast.parse(fh.read().encode(sys.stdout.encoding), path)

        modules = []

        for node in ast.iter_child_nodes(root):
            if isinstance(node, ast.Import):
                module = []
            elif isinstance(node, ast.ImportFrom):
                module = node.module.split('.')
            else:
                continue

            for n in node.names:
                # {"module":module, "name":n.name.split('.'), "alias":n.asname}
                modules.append(module[0] if module else n.name.split(".")[0])
        return modules

    def get_requirements(self,path):
        files = os.listdir(path)
        modules = []
        for fn in files:
            if fn.endswith(".py"):
                m = [i for i in self.get_imports(os.path.join(path,fn)) if i+".py" not in files]
                modules += m
        modules = ["%s==%s" % (m,self.MODULES[m]) for m in list(set(modules)) if m in self.MODULES]
        return modules

    def mk_requirementsTXT(self,path,fn=None, venv=False):
        fn = fn if fn is not None else self.REQ_TXT_FN
        required = self.get_requirements(path)
        print(required)
        if required:
            with open(os.path.join(path,fn),"w") as f:
                f.write('\n'.join(required))
            if venv:
                self.mk_venv(path,"{}_venv".format(os.path.split(path)[-1]),fn)

    def batch_mk_requirementsTXT(self, container_path, fn=None, venv=False):
        fn = fn if fn is not None else self.REQ_TXT_FN
        for project in os.listdir(container_path):
            joined = os.path.join(container_path, project)
            if os.path.isdir(joined):
                print(project)
                self.mk_requirementsTXT(joined, fn, venv)


    def rm_requirementsTXT(self,path,fn=None):
        fn = fn if fn is not None else self.REQ_TXT_FN
        joined = os.path.join(path, fn)
        if os.path.isfile(joined):
            os.remove(joined)

    def batch_rm_requirementsTXT(self, container_path, fn=None):
        fn = fn if fn is not None else self.REQ_TXT_FN
        for project in os.listdir(container_path):
            joined = os.path.join(container_path,project)
            if os.path.isdir(joined):
                self.rm_requirementsTXT(joined,fn)


    def mk_venv(self,path,name,reqfn=None):
        reqfn = reqfn if reqfn is not None else self.REQ_TXT_FN
        if sys.platform == "win32":
            commands = ["pip install virtualenvwrapper-win",
                        "cd %s" % path,
                        "mkvirtualenv %s" % name,
                        "workon %s" % name,
                        "pip install -r %s" % reqfn]
            subprocess.check_call(' && '.join(commands), shell=True)
        else:
            commands = ["pip install virtualenv",
                        "cd %s" % path,
                        "virtualenv %s" % name,
                        "source %s/bin/activate" % name,
                        "pip install -r %s" % reqfn]
            subprocess.check_call(' && '.join(commands), shell=True)


req = REQER()

#req.batch_mk_requirementsTXT(r"C:\Users\user\PycharmProjects",venv=True)
req.mk_requirementsTXT(r"C:\Users\user\Documents\GitHub\auto-requirements",venv=True)
