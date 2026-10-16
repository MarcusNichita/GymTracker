import os
import sys

def resource_path(relative_path):
    """ Get path to resource, works for dev and for when running as EXE """
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

DB_PATH = resource_path('gym_tracker.db')