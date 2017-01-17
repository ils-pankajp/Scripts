# This is Python Script to Setup DO server.
import random
import string
import subprocess
import sys
import socket
import os
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import fcntl
import struct
import array


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

mp_len = 15
t_chars = string.ascii_letters + string.digits + '!@#$^&*:./?=+-_[]{}()<>'
rnd = random.SystemRandom()
temp_file = '/tmp/automation_script.log'
mysql_config = ['/etc/mysql/mysql.conf.d/mysqld.cnf', '/etc/mysql/my.cnf']
hostname = socket.gethostname()


def get_initials():
    setup_mysql = ''
    new_user = ''
    new_database = ''
    setup_admin_user = ''
    setup_firewall = ''
    while setup_mysql != 'yes' and setup_mysql != 'no':
        setup_mysql = raw_input(bcolors.ENDC + bcolors.HEADER + '\nDo you want to Newly setup Mysql (yes/no): ' + bcolors.ENDC)
    if setup_mysql == 'yes':
        while not new_user:
            new_user = raw_input(bcolors.HEADER + 'Please Enter MySQL username to be created: ' + bcolors.ENDC)
        while not new_database:
            new_database = raw_input(bcolors.HEADER + 'Please Enter MySQL Database name to be created: ' + bcolors.ENDC)
    while setup_admin_user != 'yes' and setup_admin_user != 'no':
        setup_admin_user = raw_input(bcolors.HEADER + 'Do you want to setup Admin User(yes/no): ' + bcolors.ENDC)
    while setup_firewall != 'yes' and setup_firewall != 'no':
        setup_firewall = raw_input(bcolors.HEADER + 'Do you want to setup firewall (yes/no): ' + bcolors.ENDC)
    return new_user, new_database, setup_mysql, setup_admin_user, setup_firewall


def get_log():
    logs = None
    with open(temp_file, 'r') as file:
        logs = file.read()
    return logs


def send_mail(text='', file=None):

    to = 'p.patel@thesynapses.com'
    user = 'developerthesynapses@gmail.com'
    password = '123qwe,./'
    server = "smtp.gmail.com"
    port = 587

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'DO Setup: %s' % hostname
    try:
        msg.attach(MIMEText(text))
        with open(file, "rb") as fil:
            part = MIMEApplication(fil.read(), Name=basename(file))
            part['Content-Disposition'] = 'attachment; filename="%s.pem"' % basename(file)
            msg.attach(part)
    except:
        pass

    smtp = smtplib.SMTP(server, port)
    try:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(user, password)
        smtp.sendmail(user, to, msg.as_string())
        print bcolors.OKGREEN + "Done!" + bcolors.ENDC
        smtp.close()
    except:
        print bcolors.FAIL + "Failed!" + bcolors.ENDC


def init():
    print bcolors.UNDERLINE + bcolors.HEADER + bcolors.BOLD + "\nStarting DO Automated installation ... \n" + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '1. Creating temp file ... ' + bcolors.ENDC)
    try:
        basedir = os.path.dirname(temp_file)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        with open(temp_file, 'a'):
            os.utime(temp_file, None)
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    except:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '2. Adding Universe Repository ... ' + bcolors.ENDC)
    if int(subprocess.check_output('apt-add-repository universe 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '3. Updating Repository ... ' + bcolors.ENDC)
    if int(subprocess.check_output('apt-get -y update 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '4. Installing Software-Property-Common Package ... ' + bcolors.ENDC)
    if int(subprocess.check_output('apt-get -y install software-properties-common 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '5. Installing Debconf Utility Package ... ' + bcolors.ENDC)
    if int(subprocess.check_output('apt-get -y install debconf-utils 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '6. Installing Python Package Installer ... ' + bcolors.ENDC)
    if int(subprocess.check_output('apt-get -y install python-pip 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '7. Installing Mysql Lib of Python ... ' + bcolors.ENDC)
    if int(subprocess.check_output('apt-get -y install python-mysqldb 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '8. Installing Python Package for Firewall ... ' + bcolors.ENDC)
    if int(subprocess.check_output('pip install -U IPy 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC


def setup(new_user, new_database):
    mysql_root_pass = ''.join(rnd.choice(t_chars) for i in range(mp_len))
    sys.stdout.write(bcolors.OKBLUE + '9. Installing Mysql ... ' + bcolors.ENDC)
    if int(subprocess.check_output("echo 'mysql-server mysql-server/root_password password %s' | debconf-set-selections 1>%s 2>>%s; echo $?" % (mysql_root_pass, temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Error in settings prerequisites'
        print get_log() + bcolors.ENDC
    if int(subprocess.check_output("echo 'mysql-server mysql-server/root_password_again password %s' | debconf-set-selections 1>%s 2>>%s; echo $?" % (mysql_root_pass, temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Error in settings prerequisites' + bcolors.ENDC
        print get_log() + bcolors.ENDC
    if int(subprocess.check_output('apt-get -y install mysql-server 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    print ('10. Setting up Mysql Config... ')
    for mconfig_file in mysql_config:
        try:
            sys.stdout.write(bcolors.OKBLUE + '10(%s). Assuming Mysql Config Path %s ... ' % (str(mysql_config.index(mconfig_file) + 1), mconfig_file) + bcolors.ENDC)
            connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            connection.connect(("8.8.8.8", 80))
            address = (connection.getsockname()[0])
            connection.close()
            config = None
            with open(mconfig_file, 'r') as file:
                config = file.read()
            config = config.replace('127.0.0.1', address)
            with open(mconfig_file, 'w') as file:
                file.write(config)
            print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
            break
        except:
            print bcolors.FAIL + 'Failed!' + bcolors.ENDC

    sys.stdout.write(bcolors.OKBLUE + '11. Restarting Mysql ... ' + bcolors.ENDC)
    if int(subprocess.check_output('service mysql restart 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
        try:
            sys.stdout.write(bcolors.OKBLUE + '12. Importing Mysql Python Lib ... ' + bcolors.ENDC)
            import MySQLdb
            print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
            try:
                sys.stdout.write(bcolors.OKBLUE + '13. Connecting Mysql Server! ... ' + bcolors.ENDC)
                dbserver = MySQLdb.connect("localhost", "root", mysql_root_pass, )
                print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
                newpass = ''.join(rnd.choice(t_chars) for i in range(mp_len))
                cursor = dbserver.cursor()
                sys.stdout.write(bcolors.OKBLUE + '14(1). Creating database! ... ' + bcolors.ENDC)
                try:
                    cursor.execute('CREATE DATABASE %s' % new_database)
                    dbserver.commit()
                    print bcolors.OKGREEN + "Done!" + bcolors.ENDC
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    print bcolors.FAIL + "Failed!"
                    print(str(e)) + bcolors.ENDC
                    new_database = 'None'
                sys.stdout.write(bcolors.OKBLUE + '14(2). Setting Local Permissions! ... ' + bcolors.ENDC)
                try:
                    cursor.execute('GRANT ALL on %s.* to "%s"@"localhost" identified by "%s"' % (new_database, new_user, newpass))
                    dbserver.commit()
                    print bcolors.OKGREEN + "Done!" + bcolors.ENDC
                    m_l_u = True
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    print bcolors.FAIL + "Failed!"
                    print(str(e)) + bcolors.ENDC
                    m_l_u = False
                sys.stdout.write(bcolors.OKBLUE + '14(3). Setting Remote Permissions! ... ' + bcolors.ENDC)
                try:
                    cursor.execute('GRANT ALL on %s.* to "%s"@"' % (new_database, new_user) + '%"' + ' identified by "%s"' % newpass)
                    dbserver.commit()
                    print bcolors.OKGREEN + "Done!" + bcolors.ENDC
                    m_r_u = True
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    print bcolors.FAIL + "Failed!"
                    print(str(e)) + bcolors.ENDC
                    m_r_u = False
                if m_l_u is False and m_r_u is False:
                    new_user = 'None'
                    newpass = 'None'
                elif m_l_u is True and m_r_u is False:
                    new_user += ' (Unable to Config Remote Permission)'
                elif m_l_u is False and m_r_u is True:
                    new_user += ' (Unable to Config Local Permission)'
                dbserver.close()
                return mysql_root_pass, new_database, new_user, newpass
            except MySQLdb.Error, e:
                print bcolors.FAIL + 'Failed!' + bcolors.ENDC
                print (bcolors.FAIL + 'ERROR: ' + str(e) + bcolors.ENDC)
                sys.stdout.write(bcolors.OKBLUE + '14. Setting Mysql Database and user! ... ' + bcolors.ENDC)
                print bcolors.WARNING + 'Skipped' + bcolors.ENDC
        except:
            print bcolors.FAIL + "Failed!" + bcolors.ENDC


def add_user():
    sys.stdout.write(bcolors.OKBLUE + '15. Adding Admin User ... ' + bcolors.ENDC)
    if int(subprocess.check_output("useradd -m -s /bin/bash sysadmin 1>%s 2>>%s; echo $?" % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!'
        print get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '16. Creating SSH-Key ... ' + bcolors.ENDC)
    if int(subprocess.check_output("""su -c 'echo "y" | ssh-keygen -t rsa -N "" -f ~/.ssh/%s-sysadmin' sysadmin 1>%s 2>>%s; echo $?""" % (hostname, temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!'
        print get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '17. Updating SSH-Public-Key ... ' + bcolors.ENDC)
    if int(subprocess.check_output("su -c 'mv ~/.ssh/%s-sysadmin.pub ~/.ssh/authorized_keys' sysadmin 1>%s 2>>%s; echo $?" % (hostname, temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!'
        print get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    sys.stdout.write(bcolors.OKBLUE + '18. Granting Admin Privileges... ' + bcolors.ENDC)
    if int(subprocess.check_output("echo 'sysadmin ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers; echo $?", shell=True)) != 0:
        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    ssh_key = subprocess.check_output("su -c 'echo $HOME' sysadmin", shell=True) + '/.ssh/%s-sysadmin' % hostname
    ssh_key = str(ssh_key).replace('\n', '')
    if os.path.exists(ssh_key):
        return ssh_key
    else:
        return 'None'


def all_interfaces():
    sys.stdout.write(bcolors.OKBLUE + '   [+] Getting Interfaces list ... ' + bcolors.ENDC)
    max_possible = 128
    bytes = max_possible * 32
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    names = array.array('B', '\0' * bytes)
    outbytes = struct.unpack('iL', fcntl.ioctl(
        s.fileno(),
        0x8912,
        struct.pack('iL', bytes, names.buffer_info()[0])
    ))[0]
    namestr = names.tostring()
    lst = []
    for i in range(0, outbytes, 40):
        name = namestr[i:i + 16].split('\0', 1)[0]
        ip = namestr[i + 20:i + 24]
        lst.append((name, ip))
    print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    return lst


def format_ip(addr):
    return str(ord(addr[0])) + '.' + \
           str(ord(addr[1])) + '.' + \
           str(ord(addr[2])) + '.' + \
           str(ord(addr[3]))


def get_sockets():
    print ''
    ifs = all_interfaces()
    socket_container = []
    sys.stdout.write(bcolors.OKBLUE + '   [+] Getting Sockets list ... ' + bcolors.ENDC)
    for i in ifs:
        interface = i[0]
        src = format_ip(i[1])
        for port in range(1, 35565):
            if interface != 'lo':
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((src, int(port)))
                if result == 0:
                    s_socket = {'interface': interface, 'source': src, 'port': port, 'allow': [], 'deny': ['ALL']}
                    socket_container.append(s_socket)
                sock.close()
    print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    socket_container = add_ssh_connection(socket_container)
    return socket_container


def get_ssh_connection():
    sys.stdout.write(bcolors.OKBLUE + '   [+] Getting SSH Connection ... ' + bcolors.ENDC)
    ssh_client_ip = subprocess.check_output("echo $SSH_CONNECTION| awk '{print $1}'", shell=True)
    ssh_server_ip = subprocess.check_output("echo $SSH_CONNECTION| awk '{print $3}'", shell=True)
    ssh_port = subprocess.check_output("echo $SSH_CONNECTION| awk '{print $4}'", shell=True)
    ssh_connection = {'ssh_server_ip': ssh_server_ip.replace('\n', ''), 'ssh_client_ip': ssh_client_ip.replace('\n', ''), 'ssh_port': ssh_port.replace('\n', '')}
    return ssh_connection


def add_ssh_connection(socket_container):
    new_socket_container = socket_container
    ssh_connection = get_ssh_connection()
    for sock in new_socket_container:
        if sock['source'] == ssh_connection['ssh_server_ip'] and sock['port'] == int(ssh_connection['ssh_port']):
            sock['allow'].append(ssh_connection['ssh_client_ip'])
            print socket
    print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    return new_socket_container


def select_socket():
    socket_container = get_sockets()
    socket_select = ''
    while socket_select != 'done':
        subprocess.call('clear', shell=True)
        print bcolors.UNDERLINE + 'Currently open Socket List: ' + bcolors.ENDC
        print bcolors.UNDERLINE + bcolors.BOLD + 'Index | Intf | Socket(IP:PORT) | ' + bcolors.UNDERLINE + bcolors.OKGREEN + 'ACCEPT' + bcolors.UNDERLINE + bcolors.BOLD + ' | ' + bcolors.FAIL + bcolors.UNDERLINE + 'Deny (REJECT/DROP)' + bcolors.ENDC
        for i in socket_container:
            print bcolors.BOLD + '   ' + str(socket_container.index(i)) + '. ' + i['interface'] + ' - ' + i['source'] + ':' + str(i['port']) + ' ' + bcolors.OKGREEN + str(i['allow']) + ' ' + bcolors.FAIL + str(i['deny']) + bcolors.ENDC
        print bcolors.OKBLUE + "Write 'done' to complete Process!" + bcolors.ENDC
        socket_select = raw_input(bcolors.HEADER + 'Please select socket index to Apply Rules: ' + bcolors.ENDC)
        try:
            socket_select = int(socket_select)
            selected = socket_container[int(socket_select)]
            print bcolors.OKBLUE + bcolors.BOLD + 'Interface: %s, IP: %s, PORT: %s, Allowed IP: %s, Denied IP: %s' % (selected['interface'], selected['source'], selected['port'], selected['allow'], selected['deny']) + bcolors.ENDC
            socket_container = select_target(socket_container, socket_select)
        except:
            if socket_select == 'done':
                return socket_container
            else:
                print 'Invalid Socket Selection!'


def select_target(socket_container, socket_select):
    new_socket_container = socket_container
    target_select = None
    while target_select != 'done':
        try:
            print bcolors.HEADER + ''
            print bcolors.BOLD + str('1. Add to ACCEPT list.')
            print '2. Remove from ACCEPT list.'
            print '3. Add to REJECT list.'
            print '4. Remove from REJECT list.' + bcolors.ENDC
            print bcolors.OKBLUE + "Write 'done' to go Back!" + bcolors.ENDC
            target_select = raw_input(bcolors.HEADER + 'Please select to modify Targets: ' + bcolors.ENDC)
            check_selection = 20 / int(target_select)
            if int(target_select) == 1:
                allow_update = add_allow(socket_container, socket_select)
                new_socket_container = allow_update
            if int(target_select) == 2:
                allow_update = remove_allow(socket_container, socket_select)
                new_socket_container = allow_update
            elif int(target_select) == 3:
                deny_update = add_deny(socket_container, socket_select)
                new_socket_container = deny_update
            elif int(target_select) == 4:
                deny_update = remove_deny(socket_container, socket_select)
                new_socket_container = deny_update
            else:
                pass
        except:
            if target_select == 'done':
                return new_socket_container
            else:
                print 'Invalid Target Selection'


def add_allow(socket_container, socket_select):
    new_socket_container = socket_container
    ip = ''
    while ip != 'done':
        for ip in socket_container[socket_select]['allow']:
            print bcolors.BOLD + str(socket_container[socket_select]['allow'].index(ip)) + '. ' + ip
        print bcolors.OKBLUE + "Write 'done' to go Back!" + bcolors.ENDC
        ip = raw_input(bcolors.HEADER + 'Please Enter IP Address to Add in Allow List: ' + bcolors.ENDC)
        try:
            ip_check = IP(ip)
            socket_container[socket_select]['allow'].append(ip)
        except:
            if ip == 'ALL':
                socket_container[socket_select]['allow'].append(ip)
            if ip == 'done':
                return new_socket_container
            else:
                print 'Invalid IP Address'


def remove_allow(socket_container, socket_select):
    new_socket_container = socket_container
    ip = ''
    while ip != 'done':
        for ip in socket_container[socket_select]['allow']:
            print bcolors.BOLD + str(socket_container[socket_select]['allow'].index(ip)) + '. ' + ip
        print bcolors.OKBLUE + "Write 'done' to go Back!" + bcolors.ENDC
        ip = raw_input(bcolors.HEADER + 'Please Enter index of IP Address to remove from Allow List: ' + bcolors.ENDC)
        try:
            data = socket_container[socket_select]['allow'][int(ip)]
            socket_container[socket_select]['allow'].remove(data)
        except:
            if ip == 'done':
                return new_socket_container
            else:
                print 'Invalid IP Address'


def add_deny(socket_container, socket_select):
    new_socket_container = socket_container
    ip = ''
    while ip != 'done':
        for ip in socket_container[socket_select]['deny']:
            print bcolors.BOLD + str(socket_container[socket_select]['deny'].index(ip)) + '. ' + ip
        print bcolors.OKBLUE + "Write 'done' to go Back!" + bcolors.ENDC
        ip = raw_input(bcolors.HEADER + 'Please Enter IP Address to Add in Deny List: ' + bcolors.ENDC)
        try:
            ip_check = IP(ip)
            socket_container[socket_select]['deny'].append(ip)
        except:
            if ip == 'ALL':
                socket_container[socket_select]['deny'].append(ip)
            if ip == 'done':
                return new_socket_container
            else:
                print 'Invalid IP Address'


def remove_deny(socket_container, socket_select):
    new_socket_container = socket_container
    ip = ''
    while ip != 'done':
        for ip in socket_container[socket_select]['deny']:
            print bcolors.BOLD + str(socket_container[socket_select]['deny'].index(ip)) + '. ' + ip
        print bcolors.OKBLUE + "Write 'done' to go Back!" + bcolors.ENDC
        ip = raw_input(bcolors.HEADER + 'Please Enter index of IP Address to remove from REJECT List: ' + bcolors.ENDC)
        try:
            data = socket_container[socket_select]['deny'][int(ip)]
            socket_container[socket_select]['deny'].remove(data)
        except:
            if ip == 'done':
                return new_socket_container
            else:
                print 'Invalid IP Address'


def apply_firewall_rules():
    rules = ''
    socket_container = select_socket()
    print bcolors.UNDERLINE + 'Rules to be apply: ' + bcolors.ENDC
    if socket_container == get_sockets():
        print bcolors.UNDERLINE + bcolors.BOLD + 'Index | Intf | Socket(IP:PORT) | ' + bcolors.UNDERLINE + bcolors.OKGREEN + 'ACCEPT' + bcolors.UNDERLINE + bcolors.BOLD + ' | ' + bcolors.FAIL + bcolors.UNDERLINE + 'Deny (REJECT/DROP)' + bcolors.ENDC
        for i in socket_container:
            print bcolors.BOLD + '   ' + str(socket_container.index(i)) + '. ' + i['interface'] + ' - ' + i['source'] + ':' + str(i['port']) + bcolors.OKGREEN + str(i['allow']) + bcolors.FAIL + str(i['deny']) + bcolors.ENDC

        print bcolors.OKBLUE + 'No Changes!' + bcolors.ENDC
    else:
        print bcolors.UNDERLINE + bcolors.BOLD + 'Index | Intf | Socket(IP:PORT) | ' + bcolors.UNDERLINE + bcolors.OKGREEN + 'ACCEPT' + bcolors.UNDERLINE + bcolors.BOLD + ' | ' + bcolors.FAIL + bcolors.UNDERLINE + 'Deny (REJECT/DROP)' + bcolors.ENDC
        for i in socket_container:
            print bcolors.BOLD + '   ' + str(socket_container.index(i)) + '. ' + i['interface'] + ' - ' + i['source'] + ':' + str(i['port']) + bcolors.OKGREEN + str(i['allow']) + bcolors.FAIL + str(i['deny']) + bcolors.ENDC

    # Write Rules
    for rule in socket_container:
        inf = rule['interface']
        src = rule['source']
        port = rule['port']
        if rule['allow']:
            for ip in rule['allow']:
                if ip != 'ALL':
                    sys.stdout.write(bcolors.OKBLUE + 'Applying Rules ... ' + bcolors.ENDC)
                    if int(subprocess.check_output('iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j ACCEPT 1>%s 2>>%s; echo $?' % (inf, ip, src, port, temp_file, temp_file), shell=True)) != 0:
                        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[+]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, ip, src, port) + '   Failed!'
                    else:
                        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Allowed from ' + ip
                        rules += '\n        ----[+]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, ip, src, port) + '   Done!'
        if rule['deny']:
            for ip in rule['deny']:
                if ip != 'ALL':
                    sys.stdout.write(bcolors.OKBLUE + 'Applying Rules ... ' + bcolors.ENDC)
                    if int(subprocess.check_output('iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j REJECT 1>%s 2>>%s; echo $?' % (inf, ip, src, port, temp_file, temp_file), shell=True)) != 0:
                        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[-]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j REJECT' % (inf, ip, src, port,) + '   Failed!'
                    else:
                        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Restricted to ' + ip
                        rules += '\n        ----[-]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j REJECT' % (inf, ip, src, port,) + '   Done!'
    for rule in socket_container:
        inf = rule['interface']
        src = rule['source']
        port = rule['port']
        if rule['allow']:
            for ip in rule['allow']:
                if ip == 'ALL':
                    sys.stdout.write(bcolors.OKBLUE + 'Applying Rules ... ' + bcolors.ENDC)
                    if int(subprocess.check_output('iptables -A INPUT -i %s -d %s -p tcp --dport %s -j ACCEPT 1>%s 2>>%s; echo $?' % (inf, src, port, temp_file, temp_file), shell=True)) != 0:
                        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[+]iptables -A INPUT -i %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, src, port) + '   Failed!'
                    else:
                        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Allowed from All'
                        rules += '\n        ----[+]iptables -A INPUT -i %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, src, port) + '   Done!'
        if rule['deny']:
            for ip in rule['deny']:
                if ip == 'ALL':
                    sys.stdout.write(bcolors.OKBLUE + 'Applying Rules ... ' + bcolors.ENDC)
                    if int(subprocess.check_output('iptables -A INPUT -i %s -d %s -p tcp --dport %s -j REJECT 1>%s 2>>%s; echo $?' % (inf, src, port, temp_file, temp_file), shell=True)) != 0:
                        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[-]iptables -A INPUT -i %s -d %s -p tcp --dport %s -j REJECT' % (inf, src, port) + '   Failed!'
                    else:
                        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Restricted to All'
                        rules += '\n        ----[-]iptables -A INPUT -i %s -d %s -p tcp --dport %s -j REJECT' % (inf, src, port) + '   Done!'
    return rules

# --------------------------------------------------
if __name__ == '__main__':
    print bcolors.UNDERLINE + bcolors.HEADER + bcolors.BOLD + "Welcome to Synapse DO Automated installation" + bcolors.ENDC
    data = get_initials()
    confirmation = ''
    while confirmation != 'yes':
        confirmation = raw_input(bcolors.HEADER + bcolors.BOLD + "Above information is correct (yes/no): " + bcolors.ENDC)
        if confirmation == 'no':
            data = get_initials()
    init()

    # Mysql Setup
    if data[2] == 'yes':
        mysql_info = setup(data[0], data[1])
        if mysql_info:
            try:
                print bcolors.OKBLUE + 'Mysql Root Password: ' + bcolors.BOLD + mysql_info[0] + bcolors.ENDC
                print bcolors.OKBLUE + 'Mysql Database name: ' + bcolors.BOLD + mysql_info[1] + bcolors.ENDC
                print bcolors.OKBLUE + 'Mysql User name: ' + bcolors.BOLD + mysql_info[2] + bcolors.ENDC
                print bcolors.OKBLUE + 'Mysql User Password: ' + bcolors.BOLD + mysql_info[3] + bcolors.ENDC
            except:
                pass
        try:
            mysql_details = """
        MySQL Details:

            Mysql Root Password: %s
            Mysql Database name: %s
            Mysql User name: %s
            Mysql User Password: %s \n""" % (mysql_info[0], mysql_info[1], mysql_info[2], mysql_info[3])
        except:
            mysql_details = ''
    else:
        mysql_details = ''

    # User Setup
    if data[3] == 'yes':
        ssh_key = add_user()
        try:
            ssh_details = """
        SSH Details:

            Admin User: sysadmin
            Password: None
            Ssh-Key: """
            if ssh_key != 'None':
                ssh_details += '<please find attachment> \n'
            else:
                ssh_details += 'Unable to Create Due to Error \n'
        except:
            ssh_details = '\n'
    else:
        ssh_details = ''
        ssh_key = 'None'

    # Firewall Setup
    if data[4] == 'yes':
        sys.stdout.write(bcolors.OKBLUE + '19. Importing IP Python Lib ... ' + bcolors.ENDC)
        try:
            from IPy import IP
            print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
        except:
            print bcolors.FAIL + 'Failed!' + bcolors.ENDC
        sys.stdout.write(bcolors.OKBLUE + '20. Setting Firewall! ... ' + bcolors.ENDC)
        print bcolors.OKGREEN + 'Started!' + bcolors.ENDC
        rules = apply_firewall_rules()
        firewall_details = """
        Firewall Details:%s
        """ % rules
    else:
        firewall_details = ""

    mail_head = """Hello,
        You are getting this mail from DO Automated Installation Script.
    please find the Details below:
    """

    mail_message = mail_head + mysql_details + ssh_details + firewall_details

    sys.stdout.write('21. Sending Mail ... ')
    if ssh_key != 'None':
        send_mail(text=str(mail_message), file=ssh_key)
    else:
        send_mail(text=str(mail_message))
