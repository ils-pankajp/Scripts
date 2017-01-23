 DO Automated Installation
 ---------------------------
 script file name: do_setup_unstable.py
 command to execute: python DO_setup_unstable.py
 last update time: 4:30 AM, 2017-01-21
 tested on: Ubuntu 14.05.4 / 15.10

 summary:
 This script have 33 steps of execution.
 before starting, script will ask user to input database name and user
 name to be created.


 Tasks:
 install/configure mysql,
 create mysql user and database,
 create system admin user,
 create admin users key,
 send ssh-key from mail.
 Apply Firewall Rules
 
 Update:
 1. Added Default Synapses Firewall Rules
 2. Added Mysql config backup
 3. Added PPK Creation
 