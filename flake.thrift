namespace py vng.gpi.flake

exception InvalidSystemClock {
  1: string message
}

exception SequenceOverflow {
  1: string message
}

service Flake {
  i64 get_worker_id()
  i64 get_timestamp()
  i64 get_id()
  string get_stats()
}