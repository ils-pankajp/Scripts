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
import threading
import time
import unicodedata


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Loader(threading.Thread):
    def __init__(self, msg=''):
        self.out = sys.stdout
        self.flag = False
        self.msg = '\r' + msg
        self.string = ''
        self.waittime = 0.1
        if os.name == 'posix':
            self.spinchars = (unicodedata.lookup('FIGURE DASH') + u' ', u'\\ ', u'| ', u'/ ')
        else:
            self.spinchars = (u'-', u'\\ ', u'| ', u'/ ')
        threading.Thread.__init__(self, None, None, "Spin Thread")

    def spin(self):
        for x in self.spinchars:
            self.string = self.msg + " ... " + x
            self.out.write(self.string)
            self.out.flush()
            time.sleep(self.waittime)

    def run(self):
        while not self.flag:
            self.spin()

    def stop(self, status, msg=''):
        self.flag = True
        self.out.flush()
        time.sleep(1)
        result = ''
        if status == 1:
            result = bcolors.FAIL + "Failed!" + bcolors.ENDC
        elif status == 0:
            result = bcolors.OKGREEN + "Done!" + bcolors.ENDC
        elif status == 2:
            result = bcolors.WARNING + 'Skipped!' + bcolors.ENDC
        else:
            result = result
        if msg:
            result = msg
        print(self.msg + " ... " + result)


mail_from = 'techsupport@thesynapses.com'
mail_pass = 'ils_2020'
mail_to = 'p.patel@thesynapses.com'
mp_len = 15
t_chars = string.ascii_letters + string.digits + '!@#$^&*:./?=+-_[]{}()<>'
rnd = random.SystemRandom()
temp_file = '/tmp/automation_script.log'
hostname = socket.gethostname()
default_firewall_allowed_list = {
    '22': ['159.203.178.175', '103.9.13.146'],
    '3306': ['54.0.0.0/8', '52.0.0.0/8', '104.131.177.5', '104.131.177.229', '103.9.13.146'],
    '80': ['ALL'],
    '443': ['ALL'],
}


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
            new_user = raw_input(bcolors.HEADER + '     Please Enter MySQL username to be created: ' + bcolors.ENDC)
        while not new_database:
            new_database = raw_input(bcolors.HEADER + '     Please Enter MySQL Database name to be created: ' + bcolors.ENDC)
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


def send_mail(text='', keys=None):

    to = mail_to
    user = mail_from
    password = mail_pass
    server = "smtp.gmail.com"
    port = 587

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'DO Setup: %s' % hostname
    msg.attach(MIMEText(text))
    try:
        for file in keys:
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
        mail_load.stop(0)
        smtp.close()
    except:
        mail_load.stop(1)


def init(data):
    print bcolors.UNDERLINE + bcolors.HEADER + bcolors.BOLD + "\nStarting DO Automated installation ... \n" + bcolors.ENDC

    load = Loader(msg=bcolors.OKBLUE + 'Creating temp file' + bcolors.ENDC)
    load.start()
    try:
        basedir = os.path.dirname(temp_file)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        with open(temp_file, 'a'):
            os.utime(temp_file, None)
        load.stop(0)
    except:
        load.stop(1)

    load = Loader(msg=bcolors.OKBLUE + 'Adding Universe Repository' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output('apt-add-repository universe 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Updating Repository' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output('apt-get -y update 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Installing Python Package Installer' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output('apt-get -y install python-pip 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    if data[2] == 'yes':

        load = Loader(msg=bcolors.OKBLUE + 'Installing Software-Property-Common Package' + bcolors.ENDC)
        load.start()
        if int(subprocess.check_output('apt-get -y install software-properties-common 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
            load.stop(1)
            print bcolors.FAIL + get_log() + bcolors.ENDC
        else:
            load.stop(0)

        load = Loader(msg=bcolors.OKBLUE + 'Installing Debconf Utility Package' + bcolors.ENDC)
        load.start()
        if int(subprocess.check_output('apt-get -y install debconf-utils 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
            load.stop(1)
            print bcolors.FAIL + get_log() + bcolors.ENDC
        else:
            load.stop(0)

        load = Loader(msg=bcolors.OKBLUE + 'Installing Mysql Lib of Python' + bcolors.ENDC)
        load.start()
        if int(subprocess.check_output('apt-get -y install python-mysqldb 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
            load.stop(1)
            print bcolors.FAIL + get_log() + bcolors.ENDC
        else:
            load.stop(0)

    if data[4] == 'yes':

        load = Loader(msg=bcolors.OKBLUE + 'Installing Python Package for Firewall' + bcolors.ENDC)
        load.start()
        if int(subprocess.check_output('pip install -U IPy 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
            load.stop(1)
            print bcolors.FAIL + get_log() + bcolors.ENDC
        else:
            load.stop(0)


def setup(new_user, new_database):
    mysql_root_pass = ''.join(rnd.choice(t_chars) for i in range(mp_len))
    load = Loader(msg=bcolors.OKBLUE + 'Installing Mysql' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("echo 'mysql-server mysql-server/root_password password %s' | debconf-set-selections 1>%s 2>>%s; echo $?" % (mysql_root_pass, temp_file, temp_file), shell=True)) != 0:
        load.stop(1, msg=bcolors.FAIL + 'Error in settings prerequisites')
        print get_log() + bcolors.ENDC
    elif int(subprocess.check_output("echo 'mysql-server mysql-server/root_password_again password %s' | debconf-set-selections 1>%s 2>>%s; echo $?" % (mysql_root_pass, temp_file, temp_file), shell=True)) != 0:
        load.stop(1, msg=bcolors.FAIL + 'Error in settings prerequisites' + bcolors.ENDC)
        print get_log() + bcolors.ENDC
    elif int(subprocess.check_output('apt-get -y install mysql-server 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Backing up Mysql Config' + bcolors.ENDC)
    load.start()
    try:
        filedata = None
        with open('/etc/mysql/my.cnf', 'r') as file:
            filedata = file.read()

        # Write the file out again
        with open('/etc/mysql/my.cnf_orig', 'w') as file:
            file.write(filedata)
        load.stop(0)

        load2 = Loader(msg=bcolors.OKBLUE + 'Setting up Mysql Config' + bcolors.ENDC)
        load2.start()
        try:
            connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            connection.connect(("8.8.8.8", 80))
            address = (connection.getsockname()[0])
            connection.close()
            if int(subprocess.check_output("""echo '[mysqld]' >> %s;echo 'bind-address = %s' >> %s; echo $?""" % ('/etc/mysql/my.cnf', address, '/etc/mysql/my.cnf'), shell=True)) != 0:
                load2.stop(1)
            else:
                load2.stop(0)
        except:
            load2.stop(1)
    except:
        load.stop(1)

    load = Loader(msg=bcolors.OKBLUE + 'Restarting Mysql' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output('service mysql restart 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)
        try:
            load = Loader(msg=bcolors.OKBLUE + 'Importing Mysql Python Lib' + bcolors.ENDC)
            load.start()
            import MySQLdb
            load.stop(0)
            try:
                load = Loader(msg=bcolors.OKBLUE + 'Connecting Mysql Server!' + bcolors.ENDC)
                load.start()
                dbserver = MySQLdb.connect("localhost", "root", mysql_root_pass, )
                load.stop(0)
                newpass = ''.join(rnd.choice(t_chars) for i in range(mp_len))
                cursor = dbserver.cursor()
                load = Loader(msg=bcolors.OKBLUE + '   [+] Creating database!' + bcolors.ENDC)
                load.start()
                try:
                    cursor.execute('CREATE DATABASE %s' % new_database)
                    dbserver.commit()
                    load.stop(0)
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    load.stop(1)
                    print(str(e)) + bcolors.ENDC
                    new_database = 'None'
                load = Loader(msg=bcolors.OKBLUE + '   [+] Setting Local Permissions!' + bcolors.ENDC)
                load.start()
                try:
                    cursor.execute('GRANT ALL on %s.* to "%s"@"localhost" identified by "%s"' % (new_database, new_user, newpass))
                    dbserver.commit()
                    load.stop(0)
                    m_l_u = True
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    load.stop(1)
                    print(str(e)) + bcolors.ENDC
                    m_l_u = False
                load = Loader(msg=bcolors.OKBLUE + '   [+] Setting Remote Permissions!' + bcolors.ENDC)
                load.start()
                try:
                    cursor.execute('GRANT ALL on %s.* to "%s"@"' % (new_database, new_user) + '%"' + ' identified by "%s"' % newpass)
                    dbserver.commit()
                    load.stop(0)
                    m_r_u = True
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    load.stop(1)
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
                load.stop(1)
                print (bcolors.FAIL + 'ERROR: ' + str(e) + bcolors.ENDC)
                sys.stdout.write(bcolors.OKBLUE + 'Setting Mysql Database and user! ... ' + bcolors.ENDC)
                print bcolors.WARNING + 'Skipped' + bcolors.ENDC
        except:
            load.stop(1)


def add_user():
    load = Loader(msg=bcolors.OKBLUE + 'Adding Admin User' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("useradd -m -s /bin/bash sysadmin 1>%s 2>>%s; echo $?" % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Creating SSH-Key' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("""su -c 'echo "y" | ssh-keygen -t rsa -N "" -f ~/.ssh/%s-sysadmin' sysadmin 1>%s 2>>%s; echo $?""" % (hostname, temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Updating SSH-Public-Key' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("su -c 'mv ~/.ssh/%s-sysadmin.pub ~/.ssh/authorized_keys' sysadmin 1>%s 2>>%s; echo $?" % (hostname, temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Adding Putty Liberary' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("apt-get install -y putty 1>%s 2>>%s; echo $?" % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

        load = Loader(msg=bcolors.OKBLUE + 'Converting SSH Private Key' + bcolors.ENDC)
        load.start()
        if int(subprocess.check_output("su -c 'puttygen ~/.ssh/%s-sysadmin -O private -o ~/.ssh/%s-sysadmin.ppk' sysadmin 1>%s 2>>%s; echo $?" % (hostname, hostname, temp_file, temp_file), shell=True)) != 0:
            load.stop(1)
            print bcolors.FAIL + get_log() + bcolors.ENDC
        else:
            load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Granting Admin Privileges' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("echo 'sysadmin ALL=(ALL)       NOPASSWD: ALL' >> /etc/sudoers; echo $?", shell=True)) != 0:
        load.stop(1)
    else:
        load.stop(0)
    ssh_key = subprocess.check_output("su -c 'echo $HOME' sysadmin", shell=True) + '/.ssh/%s-sysadmin' % hostname
    ssh_key = str(ssh_key).replace('\n', '')
    ssh_key2 = ssh_key + '.ppk'
    keys = []
    if os.path.exists(ssh_key):
        keys.append(ssh_key)
    if os.path.exists(ssh_key2):
        keys.append(ssh_key2)
    if keys:
        return keys
    else:
        return 'None'


def all_interfaces():
    load = Loader(msg=bcolors.OKBLUE + '   [+] Getting Interfaces list' + bcolors.ENDC)
    load.start()
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
    load.stop(0)
    return lst


def format_ip(addr):
    return str(ord(addr[0])) + '.' + \
           str(ord(addr[1])) + '.' + \
           str(ord(addr[2])) + '.' + \
           str(ord(addr[3]))


def get_sockets():
    ifs = all_interfaces()
    socket_container = []
    load = Loader(msg=bcolors.OKBLUE + '   [+] Getting Sockets list' + bcolors.ENDC)
    load.start()
    for i in ifs:
        interface = i[0]
        src = format_ip(i[1])
        src_type = IP(src).iptype()
        if src_type == 'PUBLIC':
            for port in range(1, 35565):
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                result = sock.connect_ex((src, int(port)))
                if result == 0:
                    s_socket = {'interface': interface, 'source': src, 'port': port, 'allow': [], 'deny': ['ALL']}
                    socket_container.append(s_socket)
                sock.close()
    load.stop(0)
    socket_container = add_ssh_connection(socket_container)
    socket_container = add_default_rules(socket_container)
    return socket_container


def get_ssh_connection():
    load = Loader(msg=bcolors.OKBLUE + '   [+] Getting SSH Connection' + bcolors.ENDC)
    load.start()
    ssh_client_ip = subprocess.check_output("echo $SSH_CONNECTION| awk '{print $1}'", shell=True)
    ssh_server_ip = subprocess.check_output("echo $SSH_CONNECTION| awk '{print $3}'", shell=True)
    ssh_port = subprocess.check_output("echo $SSH_CONNECTION| awk '{print $4}'", shell=True)
    ssh_connection = {'ssh_server_ip': ssh_server_ip.replace('\n', ''), 'ssh_client_ip': ssh_client_ip.replace('\n', ''), 'ssh_port': ssh_port.replace('\n', '')}
    load.stop(0)
    return ssh_connection


def add_ssh_connection(socket_container):
    load = Loader(msg=bcolors.OKBLUE + '   [+] Adding SSH Connection String' + bcolors.ENDC)
    load.start()
    new_socket_container = socket_container
    ssh_connection = get_ssh_connection()
    for sock in new_socket_container:
        if sock['source'] == ssh_connection['ssh_server_ip'] and sock['port'] == int(ssh_connection['ssh_port']):
            sock['allow'].append(ssh_connection['ssh_client_ip'])
    load.stop(0)
    return new_socket_container


def add_default_rules(socket_container):
    new_socket_container = socket_container
    for port in default_firewall_allowed_list:
        for sock in new_socket_container:
            if sock['port'] == int(port):
                for ip in default_firewall_allowed_list[port]:
                    if ip not in sock['allow']:
                        sock['allow'].append(ip)
    for sock in new_socket_container:
        if sock['port'] == 80 or sock['port'] == 443:
            sock['deny'].remove('ALL')

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
                    load = Loader(msg=bcolors.OKBLUE + 'Appling Rules' + bcolors.ENDC)
                    load.start()
                    if int(subprocess.check_output('iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j ACCEPT 1>%s 2>>%s; echo $?' % (inf, ip, src, port, temp_file, temp_file), shell=True)) != 0:
                        load.stop(1)
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[+]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, ip, src, port) + '   Failed!'
                    else:
                        load.stop(0)
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Allowed from ' + ip
                        rules += '\n        ----[+]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, ip, src, port) + '   Done!'
        if rule['deny']:
            for ip in rule['deny']:
                if ip != 'ALL':
                    load = Loader(msg=bcolors.OKBLUE + 'Appling Rules' + bcolors.ENDC)
                    load.start()
                    if int(subprocess.check_output('iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j REJECT 1>%s 2>>%s; echo $?' % (inf, ip, src, port, temp_file, temp_file), shell=True)) != 0:
                        load.stop(1)
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[-]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j REJECT' % (inf, ip, src, port,) + '   Failed!'
                    else:
                        load.stop(0)
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Restricted to ' + ip
                        rules += '\n        ----[-]-iptables -I INPUT -i %s -s %s -d %s -p tcp --dport %s -j REJECT' % (inf, ip, src, port,) + '   Done!'
    for rule in socket_container:
        inf = rule['interface']
        src = rule['source']
        port = rule['port']
        if rule['allow']:
            for ip in rule['allow']:
                if ip == 'ALL':
                    load = Loader(msg=bcolors.OKBLUE + 'Appling Rules' + bcolors.ENDC)
                    load.start()
                    if int(subprocess.check_output('iptables -A INPUT -i %s -d %s -p tcp --dport %s -j ACCEPT 1>%s 2>>%s; echo $?' % (inf, src, port, temp_file, temp_file), shell=True)) != 0:
                        load.stop(1)
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[+]-iptables -A INPUT -i %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, src, port) + '   Failed!'
                    else:
                        load.stop(0)
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Allowed from All'
                        rules += '\n        ----[+]-iptables -A INPUT -i %s -d %s -p tcp --dport %s -j ACCEPT' % (inf, src, port) + '   Done!'
        if rule['deny']:
            for ip in rule['deny']:
                if ip == 'ALL':
                    load = Loader(msg=bcolors.OKBLUE + 'Appling Rules' + bcolors.ENDC)
                    load.start()
                    if int(subprocess.check_output('iptables -A INPUT -i %s -d %s -p tcp --dport %s -j REJECT 1>%s 2>>%s; echo $?' % (inf, src, port, temp_file, temp_file), shell=True)) != 0:
                        load.stop(1)
                        print bcolors.FAIL + get_log() + bcolors.ENDC
                        rules += '\n        ----[-]-iptables -A INPUT -i %s -d %s -p tcp --dport %s -j REJECT' % (inf, src, port) + '   Failed!'
                    else:
                        load.stop(0)
                        print '   [+]' + inf + ' ' + src + ':' + str(port) + ' Restricted to All'
                        rules += '\n        ----[-]-iptables -A INPUT -i %s -d %s -p tcp --dport %s -j REJECT' % (inf, src, port) + '   Done!'
    save_applied_rules()
    return rules


def save_applied_rules():
    load = Loader(msg=bcolors.OKBLUE + 'Installing Iptables Persistent' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output("echo 'iptables-persistent iptables-persistent/autosave_v4 boolean true' | debconf-set-selections 1>%s 2>>%s; echo $?" % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1, msg=bcolors.FAIL + 'Error in settings prerequisites')
        print get_log() + bcolors.ENDC
    elif int(subprocess.check_output("echo 'iptables-persistent iptables-persistent/autosave_v6 boolean true' | debconf-set-selections 1>%s 2>>%s; echo $?" % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1, msg=bcolors.FAIL + 'Error in settings prerequisites' + bcolors.ENDC)
        print get_log() + bcolors.ENDC
    elif int(subprocess.check_output('apt-get -y install iptables-persistent 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

    load = Loader(msg=bcolors.OKBLUE + 'Setting Iptables Persistent' + bcolors.ENDC)
    load.start()
    if int(subprocess.check_output('invoke-rc.d iptables-persistent save 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        load.stop(1)
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        load.stop(0)

# --------------------------------------------------
if __name__ == '__main__':
    print bcolors.UNDERLINE + bcolors.HEADER + bcolors.BOLD + "Welcome to Synapse DO Automated installation" + bcolors.ENDC
    data = get_initials()
    confirmation = ''
    while confirmation != 'yes':
        confirmation = raw_input(bcolors.HEADER + bcolors.BOLD + "Above information is correct (yes/no): " + bcolors.ENDC)
        if confirmation == 'no':
            data = get_initials()
    init(data)

    # Mysql Setup
    if data[2] == 'yes':
        mysql_info = setup(data[0], data[1])
        if mysql_info:
            try:
                print bcolors.BOLD + 'Mysql Root Password: ' + bcolors.BOLD + mysql_info[0] + bcolors.ENDC
                print bcolors.BOLD + 'Mysql Database name: ' + bcolors.BOLD + mysql_info[1] + bcolors.ENDC
                print bcolors.BOLD + 'Mysql User name: ' + bcolors.BOLD + mysql_info[2] + bcolors.ENDC
                print bcolors.BOLD + 'Mysql User Password: ' + bcolors.BOLD + mysql_info[3] + bcolors.ENDC
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
        load = Loader(msg=bcolors.OKBLUE + 'Importing IP Python Lib' + bcolors.ENDC)
        load.start()
        try:
            from IPy import IP
            load.stop(0)
        except:
            load.stop(1)
        sys.stdout.write(bcolors.OKBLUE + 'Setting Firewall! ... ' + bcolors.ENDC)
        print bcolors.OKGREEN + 'Started!' + bcolors.ENDC
        rules = apply_firewall_rules()
        if rules:
            firewall_details = """
            Firewall Details:
            %s
            """ % rules
        else:
            firewall_details = ""
    else:
        firewall_details = ""

    mail_head = """Hello,
        You are getting this mail from DO Automated Installation Script.
    please find the Details below:
    """

    mail_message = mail_head + mysql_details + ssh_details + firewall_details

    mail_load = Loader(msg=bcolors.OKBLUE + 'Sending Information over Mail' + bcolors.ENDC)
    mail_load.start()
    if ssh_key != 'None':
        send_mail(text=str(mail_message), keys=ssh_key)
    else:
        send_mail(text=str(mail_message))

    load = Loader(msg=bcolors.OKBLUE + 'Exiting Script' + bcolors.ENDC)
    load.start()
    try:
        os.remove(temp_file)
    except:
        print(bcolors.FAIL + 'Unable to remove Temp File' + bcolors.ENDC)
    try:
        os.remove(sys.argv[0])
    except:
        print(bcolors.FAIL + 'Unable to Clean script' + bcolors.ENDC)
    load.stop(0)

