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


def init():
    print bcolors.OKBLUE + "Starting DO Automated installation ... " + bcolors.ENDC
    sys.stdout.write('1. Creating temp file ... ')
    try:
        basedir = os.path.dirname(temp_file)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        with open(temp_file, 'a'):
            os.utime(temp_file, None)
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    except:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
    sys.stdout.write('2. Adding Universe Repository ... ')
    if int(subprocess.check_output('apt-add-repository universe 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write('3. Updating Repository ... ')
    if int(subprocess.check_output('apt-get -y update 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write('4. Installing Software-Property-Common Package ... ')
    if int(subprocess.check_output('apt-get -y install software-properties-common 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write('5. Installing Debconf Utility Package ... ')
    if int(subprocess.check_output('apt-get -y install debconf-utils 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write('6. Installing Python Package Installer ... ')
    if int(subprocess.check_output('apt-get -y install python-pip 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC
    sys.stdout.write('7. Installing Mysql Lib of Python ... ')
    if int(subprocess.check_output('apt-get -y install python-mysqldb 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + ("Failed!") + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN +'Done!' + bcolors.ENDC


def get_initials():
    new_user = ''
    new_database = ''
    while not new_user:
        new_user = raw_input('Please Enter MySQL username to be created: ')
    while not new_database:
        new_database = raw_input('Please Enter MySQL Database name to be created: ')
    return new_user, new_database


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


def add_user():
    sys.stdout.write('14. Adding Admin User ... ')
    if int(subprocess.check_output("useradd -m -s /bin/bash sysadmin 1>%s 2>>%s; echo $?" % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!'
        print get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    sys.stdout.write('15. Creating SSH-Key ... ')
    if int(subprocess.check_output("""su -c 'echo "y" | ssh-keygen -t rsa -N "" -f ~/.ssh/%s-sysadmin' sysadmin 1>%s 2>>%s; echo $?""" % (hostname, temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!'
        print get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    sys.stdout.write('16. Updating SSH-Public-Key ... ')
    if int(subprocess.check_output("su -c 'mv ~/.ssh/%s-sysadmin.pub ~/.ssh/authorized_keys' sysadmin 1>%s 2>>%s; echo $?" % (hostname, temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!'
        print get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
    sys.stdout.write('17. Granting Admin Privileges... ')
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


def setup(new_user, new_database):
    mysql_root_pass = ''.join(rnd.choice(t_chars) for i in range(mp_len))
    sys.stdout.write('8. Installing Mysql ... ')
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
    print ('9. Setting up Mysql Config... ')
    for mconfig_file in mysql_config:
        try:
            sys.stdout.write('9(%s). Assuming Mysql Config Path %s ... ' % (str(mysql_config.index(mconfig_file) + 1), mconfig_file) )
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

    sys.stdout.write('10. Restarting Mysql ... ')
    if int(subprocess.check_output('service mysql restart 1>%s 2>>%s; echo $?' % (temp_file, temp_file), shell=True)) != 0:
        print bcolors.FAIL + 'Failed!' + bcolors.ENDC
        print bcolors.FAIL + get_log() + bcolors.ENDC
    else:
        print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
        try:
            sys.stdout.write('11. Importing Mysql Python Lib ... ')
            import MySQLdb
            print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
            try:
                sys.stdout.write('12. Connecting Mysql Server! ... ')
                dbserver = MySQLdb.connect("localhost", "root", mysql_root_pass, )
                print bcolors.OKGREEN + 'Done!' + bcolors.ENDC
                newpass = ''.join(rnd.choice(t_chars) for i in range(mp_len))
                cursor = dbserver.cursor()
                sys.stdout.write('13(1). Creating database! ... ')
                try:
                    cursor.execute('CREATE DATABASE %s' % new_database)
                    dbserver.commit()
                    print bcolors.OKGREEN + "Done!" + bcolors.ENDC
                except MySQLdb.Error, e:
                    dbserver.rollback()
                    print bcolors.FAIL + "Failed!"
                    print(str(e)) + bcolors.ENDC
                    new_database = 'None'
                sys.stdout.write('13(2). Setting Local Permissions! ... ')
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
                sys.stdout.write('13(3). Setting Remote Permissions! ... ')
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
                sys.stdout.write('13. Setting Mysql Database and user! ... ')
                print bcolors.WARNING + 'Skipped' + bcolors.ENDC
        except:
            print bcolors.FAIL + "Failed!" + bcolors.ENDC

if __name__ == '__main__':
    data = get_initials()
    confirmation = ''
    while confirmation != 'yes':
        confirmation = raw_input("Above information is correct (yes/no): ")
        if confirmation == 'no':
            data = get_initials()
    init()
    mysql_info = setup(data[0], data[1])
    if mysql_info:
        try:
            print bcolors.OKBLUE + 'Mysql Root Password: ' + bcolors.BOLD + mysql_info[0] + bcolors.ENDC
            print bcolors.OKBLUE + 'Mysql Database name: ' + bcolors.BOLD + mysql_info[1] + bcolors.ENDC
            print bcolors.OKBLUE + 'Mysql User name: ' + bcolors.BOLD + mysql_info[2] + bcolors.ENDC
            print bcolors.OKBLUE + 'Mysql User Password: ' + bcolors.BOLD + mysql_info[3] + bcolors.ENDC
        except:
            pass

    ssh_key = add_user()
    mail_head = """Hello,
    You are getting this mail from DO Automated Installation Script.
please find the Details below:
"""
    try:
        mysql_details = """
    MySQL Details:

        Mysql Root Password: %s
        Mysql Database name: %s
        Mysql User name: %s
        Mysql User Password: %s""" % (mysql_info[0], mysql_info[1], mysql_info[2], mysql_info[3])
    except:
        mysql_details = ''
    try:
        ssh_details = """
    SSH Details:
        Admin User: sysadmin
        Password: None
        Ssh-Key: """
        if ssh_key != 'None':
            ssh_details += '<please find in attachment>'
        else:
            ssh_details += 'Unable to Create Due to Error'
    except:
        ssh_details = ''

    mail_message = mail_head + mysql_details + ssh_details

    sys.stdout.write('18. Sending Mail ... ')
    if ssh_key != 'None':
        send_mail(text=str(mail_message), file=ssh_key)
    else:
        send_mail(text=str(mail_message))
