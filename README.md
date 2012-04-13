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

Flake is quite fast with Thrift protocol. You may want to run the benchmark.py to measure the performance of Flake.

