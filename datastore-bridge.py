import sys
sys.path.append('/Users/adam/python-yang-voodoo')
from yangvoodoo.Bridge import LibyangDataStore, Pyro4Bridge, startup

startup('integrationtest', 'yang')
