#!/usr/bin/env python
#
# Copyright 2012 VNG
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
from time import time
import json

from vng.gpi.flake.ttypes import *

class Stats:
    generated_ids = 0
    errors = 0
    last_generated_time = 0
    first_started_time = int(time() * 1000)

class FlakeService:
    worker_id = 0
    max_time = int(time() * 1000)
    sequence = 0
    epoch = 1325376000000 # 2012-1-1

    def get_worker_id(self):
        return FlakeService.worker_id
 
    def get_id(self):
        curr_time = int(time() * 1000)
        
        if curr_time < FlakeService.max_time:
            # stop handling requests til we've caught back up
            Stats.errors += 1
            raise InvalidSystemClock('Clock went backwards! %d < %d' % (curr_time, FlakeService.max_time))
        
        if curr_time > FlakeService.max_time:
            FlakeService.sequence = 0
            FlakeService.max_time = curr_time
        
        FlakeService.sequence += 1
        if FlakeService.sequence > 4095:
            # Sequence overflow, bail out 
            Stats.errors += 1
            raise SequenceOverflow('Sequence Overflow: %d' % FlakeService.sequence)
        
        generated_id = ((curr_time - FlakeService.epoch) << 22) + (FlakeService.worker_id << 12) + FlakeService.sequence
       
        Stats.generated_ids += 1
        Stats.last_generated_time = curr_time

        return generated_id
 
    def get_timestamp(self):
        return int(time() * 1000)

    def get_stats(self):
        stats = {
            'timestamp': time(),
            'generated_ids': Stats.generated_ids,
            'errors': Stats.errors,
            'max_time_ms': FlakeService.max_time,
            'worker_id': FlakeService.worker_id,
            'last_generated_time': Stats.last_generated_time,
            'first_started_time': Stats.first_started_time
        }
        return json.dumps(stats)
