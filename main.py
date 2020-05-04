#!/usr/bin/env python

"""
Main entry
Just parse arguments and call main controller loop

Author: Michal Bobran
"""

import os
import argparse
import urllib3
import kubetools
import controller
import healthcheck

def parseArgs():
    parser = argparse.ArgumentParser(description='Flow controller - kubernetes meta deployment manager')
    parser.add_argument('crdName', help='master CRD name')
    parser.add_argument('--verbose', '-v', action='count', help='verbosity level')
    parser.add_argument('--noAction', action='store_true', help='do not modify anything')
    parser.add_argument('--yamlPath', default=os.path.join(os.path.dirname(__file__), 'yamls'), help='path to yaml files')
    parser.add_argument('--namespace', default='default', help='default namespace to use (if not supplied in masterYamls)')
    parser.add_argument('--resourceName', default='', help='override resource name (will replace name pulled from crd)')
    parser.add_argument('--namespacePath', default='/spec/namespace', help='path to namespace field in masterYamls')
    parser.add_argument('--tracebackLabel', default=None, help='name for traceback label used in every created resource')
    parser.add_argument('--excludedKinds', default='Event,MetricValueList,PodMetrics,PersistentVolumeClaim,ComponentStatus,Endpoints', help='kinds to exclude form children scan')
    parser.add_argument('--healthPort', default=8080, type=int, help='port for healthcheck http server (use 0 to turn off)')
    parser.add_argument('--loopTimeout', default=300, type=int, help='kubernetes events watch timieout (also used for health checks)')
    parser.add_argument('--create', default=None, help='manual creation (will not enter controller loop)')
    parser.add_argument('--delete', default=None, help='manual deletion (will not enter controller loop)')
    return parser.parse_args()

def main():
    urllib3.disable_warnings() # Temporary workaround
    args = parseArgs()
    kubetools.logLevel = args.verbose
    kubetools.loadKubernetesConfig()
    mainController = controller.Controller(args)
    if args.create is not None:
        mainController.directCreate(args.create)
        return
    if args.delete is not None:
        mainController.directDelete(args.delete)
        return
    if args.healthPort:
        healthcheck.ServerThread(mainController, args.healthPort)
    mainController.controllerLoop()

if __name__ == '__main__':
    main()
