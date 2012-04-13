#!/bin/sh
############################################################
# Simple setup script to deploy id server under supervisor #
###########################################################

function install_flake() {
	destination=$1
	cp -R ./ $destination
}

function add_flake_config() {
	python=$1
	port=$2
	worker_id=$3
	cat >> /etc/supervisord.conf <<EOT

[program:flake-thrift] 
command=$python /usr/local/flake/server.py --worker-id $worker_id --port $port
process_name=%(program_name)s
numprocs=1
autostart=true
stdout_logfile=/var/log/flake_thrift_stdout.log
stderr_logfile=/var/log/flake_thrift_stderr.log
stderr_logfile_maxbyte=10MB
stderr_logfile_backups=10
stdout_logfile_maxbyte=10MB

[program:flake]
command=$python /usr/local/flake/web.py --logging=warning --worker_id=$((worker_id+1)) --port=$((port+1))
process_name=%(program_name)s
numprocs=1
autostart=true
stdout_logfile=/var/log/flake_stdout.log
stderr_logfile=/var/log/flake_stderr.log
stderr_logfile_maxbyte=10MB
stderr_logfile_backups=10
stdout_logfile_maxbyte=10MB
EOT
}

function create_supervisord_script() {
	cat > /etc/init.d/supervisord <<'EOT'
#
# Supervisor is a client/server system that
# allows its users to monitor and control a
# number of processes on UNIX-like operating
# systems.
#
# chkconfig: - 64 36
# description: Supervisor Server
# processname: supervisord

# Source init functions
. /etc/rc.d/init.d/functions

prog="supervisord"

prefix="/usr/"
exec_prefix="${prefix}"
prog_bin="${exec_prefix}/bin/supervisord"
PIDFILE="/var/run/$prog.pid"

start()
{
        echo -n $"Starting $prog: "
        daemon $prog_bin --pidfile $PIDFILE
        [ -f $PIDFILE ] && success $"$prog startup" || failure $"$prog startup"
        echo
}

stop()
{
        echo -n $"Shutting down $prog: "
        [ -f $PIDFILE ] && killproc $prog || success $"$prog shutdown"
        echo
}

case "$1" in

  start)
    start
  ;;

  stop)
    stop
  ;;

  status)
        status $prog
  ;;

  restart)
    stop
    start
  ;;

  *)
    echo "Usage: $0 {start|stop|restart|status}"
  ;;

esac

}
EOT
}

echo "Checking requirements"

python=`which python`
PYTHON_OK=`$python -c 'import sys
print (sys.version_info >= (2, 6) and "yes" or "no")'`

if [ "$PYTHON_OK" = "no" ]; then
	echo "Default Python is old. Try using 2.6 python..."
	python=`which python2.6`
fi

echo "Setting up dependencies"
$python easy_install tornado
$python easy_install supervisor

if [ ! -f /etc/supervisord.conf ]; then
	sudo echo_supervisord_conf > /etc/supervisord.conf
	add_flake_config $python 8000 0
	create_supervisord_script
fi

echo "Deploy flake to /usr/local/flake"
install_flake /usr/local/flake

echo "Restart supervisord"
/etc/init.d/supervisord restart

