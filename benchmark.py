#!/usr/bin/env python
import sys, os

from time import time
from math import fsum
import socket

from multiprocessing import Pool

from vng.gpi.flake import Flake
from vng.gpi.flake.ttypes import *
from vng.gpi.flake.constants import *

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol

class Connection(object):

    def __init__(self, host, port):
        transport = TSocket.TSocket(host, port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        self.client = Flake.Client(protocol)
        transport.open()

    def disconnect(self):
        pass

# TODO: add ability to block waiting on a connection to be released
class ConnectionPool(object):
    "Generic connection pool"
    def __init__(self, connection_class=Connection, max_connections=None,
                 **connection_kwargs):
        self.connection_class = connection_class
        self.connection_kwargs = connection_kwargs
        self.max_connections = max_connections or 2**31
        self._created_connections = 0
        self._available_connections = []
        self._in_use_connections = set()

    def get_connection(self):
        "Get a connection from the pool"
        try:
            connection = self._available_connections.pop()
        except IndexError:
            connection = self.make_connection()
        self._in_use_connections.add(connection)
        return connection

    def make_connection(self):
        "Create a new connection"
        if self._created_connections >= self.max_connections:
            raise ConnectionError("Too many connections")
        self._created_connections += 1
        return self.connection_class(**self.connection_kwargs)

    def release(self, connection):
        "Releases the connection back to the pool"
        self._in_use_connections.remove(connection)
        self._available_connections.append(connection)

    def disconnect(self):
        "Disconnects all connections in the pool"
        all_conns = chain(self._available_connections, self._in_use_connections)
        for connection in all_conns:
            connection.disconnect()

if len(sys.argv) <= 2 or sys.argv[1] == '--help' or '-h' not in sys.argv:
    print ''
    print 'Usage: ' + sys.argv[0] + ' -h host:port [-c num_conns] [-n num_reqs]'
    print ''
    sys.exit(0)

host = 'localhost'
port = 8000
num_conns = 1
num_reqs = 1000
argi = 1

while argi < len(sys.argv) - 1:
    if sys.argv[argi] == '-h':
        parts = sys.argv[argi + 1].split(':') 
        host = parts[0]
        port = int(parts[1])
        argi += 2
    elif sys.argv[argi] == '-c':
        num_conns = int(sys.argv[argi + 1])
        argi += 2
    elif sys.argv[argi] == '-n':
        num_reqs = int(sys.argv[argi + 1])
        argi += 2

conn_pool = ConnectionPool(host=host, port=port)

def get_stats():
    connection = conn_pool.get_connection()
    client = connection.client
    stats = client.get_stats()
    #print "From server: %s" % (stats)
    conn_pool.release(connection)

def get_timestamp():
    connection = conn_pool.get_connection()
    client = connection.client
    timestamp = client.get_timestamp()
    conn_pool.release(connection)

def get_worker_id():
    connection = conn_pool.get_connection()
    client = connection.client
    woker_id = client.get_worker_id()
    conn_pool.release(connection)

def get_id():
    start = time()
    try:
        connection = conn_pool.get_connection()
        client = connection.client
        id = client.get_id()
        conn_pool.release(connection)
    except Exception, e:
        error += 1
    duration = time() - start
    return duration

pool = Pool(processes=num_conns)
durations = []
error = 0

print 'Benchmarking... Plz wait...'
def add_duration(duration):
    durations.append(duration)

begin = time()
for i in range(num_reqs):
    #pool.apply_async(hell)
    pool.apply_async(get_id, callback = add_duration)
    #pool.apply_async(get_worker_id)
    #pool.apply_async(get_timestamp)
    #pool.apply_async(get_stats)

pool.close()
pool.join()

total_time = time() - begin;

error_per = error * 100 / num_reqs
durations.sort(reverse=True)
duration = fsum(durations)
complete_reqs = num_reqs - error
req_per_sec = num_reqs / total_time 
time_per_req = duration / complete_reqs
transfer_rate = 0
avg_time = 1000 * duration / num_reqs if num_reqs else 0
min_time = 1000 * durations[-1] if len(durations) else 0
max_time = 1000 * durations[0] if len(durations) else 0
fifty_p = 1000 * durations[num_reqs / 2] if len(durations) else 0
sixty_p = 1000 * durations[num_reqs * 2 / 5] if len(durations) else 0
seventy_p = 1000 * durations[num_reqs * 3 / 10] if len(durations) else 0
eighty_p = 1000 * durations[num_reqs / 5] if len(durations) else 0
ninety_p = 1000 * durations[num_reqs / 10] if len(durations) else 0
ninetynine_p = 1000 * durations[num_reqs / 100] if len(durations) else 0

print ''
print 'Concurrency Level:\t%d' % (num_conns)
print 'Time taken for tests:\t%.3f secs' % (duration)
print 'Complete requests:\t', complete_reqs
print 'Failed requests:\t%d (%1.2f%%)' % (error, error_per)
print 'Requests per second:\t%.2f [#/sec] (average)' % (req_per_sec)
print 'Time per request:\t%.4f [ms] (average)' % (time_per_req)
#print 'Total transferred:\t', 0, 'bytes'
#print 'Transfer rate:\t', transfer_rate, '[Kbytes/sec]'
print ''
print 'Connection Times (ms)'
print '\tmin\tmean\tmax'
print "\t%2.2f\t%2.2f\t%2.2f" % (min_time, avg_time, max_time)
print ''
#              min  mean[+/-sd] median   max
#Connect:       49   51   1.7     52      52
#Processing:    37   45  11.6     53      53
#Waiting:       37   45  11.6     53      53
#Total:         89   96   9.9    103     103

print 'Percentage of the requests served within a certain time (ms)'
print '\t50%%\t%.3f' % (fifty_p)
print '\t60%%\t%.3f' % (sixty_p)
print '\t70%%\t%.3f' % (seventy_p)
print '\t80%%\t%.3f' % (eighty_p)
print '\t90%%\t%.3f' % (ninety_p)
print '\t99%%\t%.3f' % (ninetynine_p)

