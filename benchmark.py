#!/usr/bin/env python
import sys, os

from time import time
import socket

from threading import Thread
from multiprocessing import Pool

from vng.gpi.flake import Flake
from vng.gpi.flake.ttypes import *
from vng.gpi.flake.constants import *

from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol

def get_stats():
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Flake.Client(protocol)
    transport.open()
 
    stats = client.get_stats()
    #print "From server: %s" % (stats)
  
    transport.close()

def get_timestamp():
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Flake.Client(protocol)
    transport.open()
 
    timestamp = client.get_timestamp()
    #print "From server: %d" % (timestamp)
  
    transport.close()

def get_worker_id():
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Flake.Client(protocol)
    transport.open()

    id = client.get_worker_id()
    #print "From server: %d" % (id)

    transport.close()

def get_id():
    transport = TSocket.TSocket(host, port)
    transport = TTransport.TBufferedTransport(transport)
    protocol = TBinaryProtocol.TBinaryProtocol(transport)
    client = Flake.Client(protocol)
    transport.open()
 
    id = client.get_id()
    #print "From server: %d" % (id)
  
    transport.close()

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

pool = Pool(processes=num_conns)

print 'Benchmarking... Plz wait...'

stats = {'error': 0, 'duration': []}
for i in range(num_reqs):
    start = time()
    
    try:
        pool.apply_async(get_id)
        #pool.apply_async(get_worker_id)
        #pool.apply_async(get_timestamp)
        #pool.apply_async(get_stats)
    except Exception, e:
        stats['error'] += 1
        pass
    duration = time() - start
    stats['duration'].append(duration)

pool.close()
pool.join()

# Compute and print stats
error = stats['error']
error_per = error * 100 / num_reqs
durations = stats['duration']
durations.sort(reverse=True)

duration = sum(durations)
complete_reqs = num_reqs - stats['error']
req_per_sec = complete_reqs / duration
time_per_req = duration / complete_reqs
transfer_rate = 0
throughput = num_conns * num_reqs / duration
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
print 'Time taken for tests:\t%4.3f seconds' % (duration)
print 'Complete requests:\t', complete_reqs
print 'Failed requests:\t%d (%1.2f%%)' % (error, error_per)
print 'Requests per second:\t%.2f[#/sec] (mean)' % (req_per_sec)
print 'Time per request:\t%.4f [ms] (average)' % (time_per_req)
print 'Total transferred:\t', 0, 'bytes'
print 'Transfer rate:\t', transfer_rate, '[Kbytes/sec]'
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
