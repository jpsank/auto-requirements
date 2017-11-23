# auto-requirements
Automatically create requirements.txt files for all your Python projects.

## Usage

    usage: python main.py [-h] (-mk | -rm) [--batch] [--venv] [paths [paths ...]]
    
    positional arguments:
      paths       Locations of project folders, or locations of project folder
                  containers (if --batch), to add/remove requirements.txt from

    optional arguments:
      -h, --help  show this help message and exit
      -mk         Make requirements.txt files for the specified project folder
                  paths
      -rm         Remove requirements.txt files for the specified project folder
                  paths
      --batch     Make requirements.txt files for all project folders in a
                  container location
      --venv      Make virtual environment based on requirements.txt



