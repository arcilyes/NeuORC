import sys
import os

# Update this path to match your PythonAnywhere username
project_home = '/home/arcilyes/NeuORC'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

from app import app as application  # noqa
