import os
import ast
from subprocess import Popen, PIPE
import sys


class REQER:
    def __init__(self,REQ_TXT_FN="requirements.txt"):
        self.MODULES = Popen("pip freeze", stdout=PIPE).stdout.read().decode().replace("\r\n", "\n")
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

    def mk_requirementsTXT(self,path,fn=None):
        fn = fn if fn is not None else self.REQ_TXT_FN
        required = self.get_requirements(path)
        print(required)
        if required:
            with open(os.path.join(path,fn),"w") as f:
                f.write('\n'.join(required))

    def recur_mk_requirementsTXT(self,container_path,fn=None):
        fn = fn if fn is not None else self.REQ_TXT_FN
        for project in os.listdir(container_path):
            joined = os.path.join(container_path, project)
            if os.path.isdir(joined):
                print(project)
                self.mk_requirementsTXT(joined, fn)


    def rm_requirementsTXT(self,path,fn=None):
        fn = fn if fn is not None else self.REQ_TXT_FN
        joined = os.path.join(path, fn)
        if os.path.isfile(joined):
            os.remove(joined)

    def recur_rm_requirementsTXT(self,container_path,fn=None):
        fn = fn if fn is not None else self.REQ_TXT_FN
        for project in os.listdir(container_path):
            joined = os.path.join(container_path,project)
            if os.path.isdir(joined):
                self.rm_requirementsTXT(joined,fn)


req = REQER()

req.recur_mk_requirementsTXT(r"C:\Users\julia\PycharmProjects")

