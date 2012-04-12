#!/usr/bin/env python
 
import sys

sys.path.append('./gen-py')

from vng.gpi.flake import Flake
from vng.gpi.flake.ttypes import *
from vng.gpi.flake.constants import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
 
try:
    # Make socket
    transport = TSocket.TSocket('localhost', 30303)
 
    # Buffering is critical. Raw sockets are very slow
    transport = TTransport.TBufferedTransport(transport)
 
    # Wrap in a protocol
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
 
    # Create a client to use the protocol encoder
    client = Flake.Client(protocol)
 
    # Connect!
    transport.open()
 
    id = client.get_id()
    print "From server: %d" % (id)
  
    transport.close()
 
except Thrift.TException, tx:
    print "%s" % (tx.message)