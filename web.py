#!/usr/bin/env python
#
# Copyright 2010 Formspring
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
import sys, os
#sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/lib')
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from flake import FlakeService
from tornado.options import define, options

define("port", default=8000, help="run on the given port", type=int)
define("worker_id", help="globally unique worker-id between 0 and 1023", type=int)

service = FlakeService()

class IdHandler(tornado.web.RequestHandler):
    def get(self):
        try:
            generated_id = service.get_id() 
            
            self.set_header("Content-Type", "text/plain")
            self.write(str(generated_id))
            self.flush() # avoid ETag, etc generation
        except Exception, e:
            raise tornado.web.HTTPError(500, str(e))

class StatsHandler(tornado.web.RequestHandler):
    def get(self):
        stats = service.get_stats()
        self.set_header("Content-Type", "text/plain")
        self.write(stats)

class WorkerIdHandler(tornado.web.RequestHandler):
    def get(self):
        worker_id = service.get_worker_id()
        self.set_header("Content-Type", "text/plain")
        self.write(str(worker_id))
        self.flush()

class TimestampHandler(tornado.web.RequestHandler):
    def get(self):
        timestamp = service.get_timestamp()
        self.set_header("Content-Type", "text/plain")
        self.write(str(timestamp))
        self.flush()

def main():
    tornado.options.parse_command_line()
    
    if 'worker_id' not in options:
        print 'missing --worker_id argument, see %s --help' % sys.argv[0] 
        sys.exit()
    
    if not 0 <= options.worker_id < 1024:
        print 'invalid worker id, must be between 0 and 1023'
        sys.exit()
        
    FlakeService.worker_id = options.worker_id
    
    application = tornado.web.Application([
        (r"/worker-id", WorkerIdHandler),
        (r"/id", IdHandler),
        (r"/stats", StatsHandler),
        (r"/timestamp", TimestampHandler),
    ])

    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
