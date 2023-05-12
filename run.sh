#!/bin/zsh

# echo "run query system"
# echo 
# echo "run postgresql in docker"
# echo "----------------"
# # docker run --name some-postgres --env POSTGRES_PASSWORD=mysecretpassword --publish 5432:5432 --detach postgres
# docker start some-postgres
# echo 
# echo "run redis"
# echo "----------------"
# redis-server --daemonize yes
# # redis-server

# echo 
# echo "run server.py"
# echo "----------------"
# # "redis-server --daemonize yes" run in background
# # "ps aux | grep redis-server" to check redis-server
# # "pkill redis-server" to kill redis-server
# # python3 server.py
# python3 server.py &

# echo 
# echo "run processor.py"
# echo "----------------"
# python3 processor.py &



# echo "run query system done"

# # netstat -vanp tcp | grep 3000

# # kill -9 <PID>
# # PLEASE NOTE: -9 kills the process immediately,
# #  and gives it no chance of cleaning up after itself. This may cause problems.
# #  Consider using -15 (TERM) or -3 (QUIT) for a softer termination which allows the process to clean up after itself.


docker start some-postgres
redis-server --daemonize yes
python3 server.py &
python3 processor.py &