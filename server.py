#!/usr/bin/env python

import socket
import sys, os

from flake import FlakeService
from vng.gpi.flake import Flake
from vng.gpi.flake.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

if len(sys.argv) < 4 or sys.argv[1] == '--help' or ('-p' not in sys.argv and '--port' not in sys.argv):
    print ''
    print 'Usage: ' + sys.argv[0] + ' --port port --worker-id worker-id'
    print ''
    sys.exit(0)

worker_id = 0
port = 8000
argi = 1

while argi < len(sys.argv) - 1:
    if sys.argv[argi] == '--port':
        port = int(sys.argv[argi + 1])
        argi += 2
    elif sys.argv[argi] == '--worker-id':
        num_conns = int(sys.argv[argi + 1])
        argi += 2

FlakeService.worker_id = worker_id

handler = FlakeService()
processor = Flake.Processor(handler)
transport = TSocket.TServerSocket('0.0.0.0', port)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()
 
server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
server.serve()
