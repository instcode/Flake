Flake is inspired by [FormSpring Flake](https://github.com/formspring/flake) which is then inspired by [Twitter's Snowflake](https://github.com/twitter/snowflake) ^^

### Usage

Flake supports HTTP and Thrift protocol to generate unique ids.

HTTP:

    /worker-id
    /id
    /stats
    /timestamp

Thrift:
    
    service Flake {
      i64 get_worker_id()
      i64 get_timestamp()
      i64 get_id()
      string get_stats()
    }

### Speed

Flake is *really* fast with Thrift protocol.
Benchmarking agaist a Xeon 2.5Ghz from another machine on the same network:

    python benchmark.py -h xeon-server:8000 -n 10000 -c 50

Result:

    Concurrency Level:      50
    Time taken for tests:   0.200 seconds
    Complete requests:      10000
    Failed requests:        0 (0.00%)
    Requests per second:    50067.85[#/sec] (mean)
    Time per request:       0.0000 [ms] (average)
    Total transferred:      0 bytes
    Transfer rate:  0 [Kbytes/sec]
    
    Connection Times (ms)
            min     mean    max
            0.01    0.02    10.75
    
    Percentage of the requests served within a certain time (ms)
            50%     0.013
            60%     0.014
            70%     0.015
            80%     0.019
            90%     0.037
            99%     0.066

