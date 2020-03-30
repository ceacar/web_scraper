1.install needed environment:
make install

2.run web api server
make run

#if you want to run in a differe port or a different ip, edit makefile, change the service_port to other port and change the service_ip to other ip


3.run utest
make utest

4.run flask itest
make itest

5.want to try the curl cmd, please refer to file named "example_cmd_for_sanity_test.py",
it provides two curl cmd for two end points

6.load testing using apache ab
make benchmark

7.run in uwsgi mode
make uwsgi
