#!/bin/sh
############################################################
# Simple setup script to deploy id server under supervisor #
###########################################################
function look_for_python_26() {
	python=`which python`
	PYTHON_OK=`$python -c 'import sys
	print (sys.version_info >= (2, 6) and "yes" or "no")'`

	if [ "$PYTHON_OK" = "no" ]; then
		echo "Default Python is old. Try using 2.6 python..."
		python=`which python2.6`
		if [ -n $python ]; then
			echo "Plz install Python >2.6 first"
			exit
		fi
	fi
	return $python
}

function install_flake() {
	destination=$1
	cp -R  $destination
}

function create_supervisord_conf() {
	if [ ! -f /etc/supervisord.conf ]; then
		echo_supervisord_conf > /etc/supervisord.conf
	fi
}

function add_flake_config() {
	python=$1
	port=$2
	worker_id=$3
	flake_program=`grep 'program:flake-thrift' /etc/supervisord.conf`
	if [ -z "$flake_program" ]; then
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
	fi
}

function create_supervisord_script() {
	if [ ! -f /etc/init.d/supervisord ]; then
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
EOT
	chmod 755 /etc/init.d/supervisord
	fi
}

echo "====================="
echo "Checking requirements"
echo "====================="
#rpm -Uvh http://dl.fedoraproject.org/pub/epel/5/x86_64/epel-release-5-4.noarch.rpm
#yum install python26-distribute
echo "Locate Python 2.6..."
python=`which python`
easy_install=`which easy_install`
PYTHON_OK=`$python -c 'import sys
print (sys.version_info >= (2, 6) and "yes" or "no")'`

if [ "$PYTHON_OK" = "no" ]; then
	python=`which python2.6 2>/dev/null`
	easy_install=`which easy_install-2.6 2>/dev/null`
	if [ -z "$python" ]; then
		echo "No python 2.6 available. Plz install Python and try again."
		exit
	fi
fi
echo "Found at $python"

echo "======================="
echo "Setting up dependencies"
echo "======================="
$easy_install tornado
$easy_install supervisor

echo "================================"
echo "Deploy flake to /usr/local/flake"
echo "================================"
script_abs_path=`readlink -f $0`
script_dir=`dirname $script_abs_path`
flake_dir=${script_dir%/*}
cp -R $flake_dir /usr/local/flake
echo "Done."

echo "======================"
echo "Setting up supervisord"
echo "======================"
create_supervisord_conf
add_flake_config $python 8000 0
create_supervisord_script
/etc/init.d/supervisord restart
echo "Done."
