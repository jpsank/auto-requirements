import os
import ast
import subprocess
import sys
import argparse


class AutoReqBuilder:
    def __init__(self,REQ_TXT_FN="requirements.txt"):
        self.MODULES = subprocess.Popen("pip freeze", stdout=subprocess.PIPE).stdout.read().decode().replace("\r\n", "\n")
        self.MODULES = [m.split("==") for m in self.MODULES.split("\n") if "==" in m]
        self.MODULES = {p[0]:p[1] for p in self.MODULES}

        self.REQ_TXT_FN = REQ_TXT_FN

    def get_imports(self,path):
        # find all modules imported in a Python file by searching for import statements
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
        # find all non-built-in modules imported in an entire Python project folder
        files = os.listdir(path)
        modules = []
        for fn in files:
            if fn.endswith(".py"):
                m = [i for i in self.get_imports(os.path.join(path,fn)) if i+".py" not in files]
                modules += m
        modules = ["%s==%s" % (m,self.MODULES[m]) for m in list(set(modules)) if m in self.MODULES]
        return modules

    def mk_requirementsTXT(self,path,fn=None, venv=False):
        # make a requirements.txt file (and optionally virtualenv) for a Python project folder
        fn = fn if fn is not None else self.REQ_TXT_FN
        required = self.get_requirements(path)
        print(required)
        if required:
            with open(os.path.join(path,fn),"w") as f:
                f.write('\n'.join(required))
            if venv:
                self.mk_venv(path,venv if isinstance(venv,str) else "{}_venv".format(os.path.split(path)[-1]),fn)

    def batch_mk_requirementsTXT(self, container_path, fn=None, venv=False):
        # make requirements.txt files (and optionally virtualenv) for every Python project folder in a location
        fn = fn if fn is not None else self.REQ_TXT_FN
        for project in os.listdir(container_path):
            joined = os.path.join(container_path, project)
            if os.path.isdir(joined):
                print(project)
                self.mk_requirementsTXT(joined, fn, venv)


    def rm_requirementsTXT(self,path,fn=None):
        # remove requirements.txt from a Python project folder
        fn = fn if fn is not None else self.REQ_TXT_FN
        joined = os.path.join(path, fn)
        if os.path.isfile(joined):
            os.remove(joined)

    def batch_rm_requirementsTXT(self, container_path, fn=None):
        # remove requirements.txt files for every Python project folder in a location
        fn = fn if fn is not None else self.REQ_TXT_FN
        for project in os.listdir(container_path):
            joined = os.path.join(container_path,project)
            if os.path.isdir(joined):
                self.rm_requirementsTXT(joined,fn)


    def mk_venv(self,path,name,reqfn=None):
        # use the appropriate venv module to make virtualenv for a Python project based on its requirements.txt file
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


req = AutoReqBuilder()


def main():
    parser = argparse.ArgumentParser(description='Automatically create requirements.txt files and virtual environments')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-mk', dest="action", action='store_true',
                       help='Make requirements.txt files for the specified project folder paths')
    group.add_argument('-rm', dest="action", action='store_false',
                       help='Remove requirements.txt files for the specified project folder paths')
    parser.add_argument('paths', nargs="*", type=str,
                        help="Locations of project folders, or locations of project folder "
                             "containers (if --batch), to add/remove requirements.txt from")
    parser.add_argument('--batch', action="store_true",
                        help='Make requirements.txt files for all project folders in a container location')
    parser.add_argument('--venv', action="store_true",
                        help='Make virtual environment based on requirements.txt')

    args = parser.parse_args()
    if args.action:
        if args.batch:
            for p in args.paths:
                req.batch_mk_requirementsTXT(p, venv=args.venv)
        else:
            for p in args.paths:
                req.mk_requirementsTXT(p, venv=args.venv)
    else:
        if args.batch:
            for p in args.paths:
                req.batch_rm_requirementsTXT(p)
        else:
            for p in args.paths:
                req.rm_requirementsTXT(p)


if __name__ == '__main__':
    main()

    # req.batch_mk_requirementsTXT(r"C:\Users\user\PycharmProjects",venv=True)
    # req.mk_requirementsTXT(r"C:\Users\user\Documents\GitHub\auto-requirements",venv=True)

