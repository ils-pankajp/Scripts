import os
import psutil
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
import socket
import subprocess
import time
import operator


mail_from = 'techsupport@thesynapses.com'
mail_pass = 'ils_2020'
mail_to = 'p.patel@thesynapses.com'
hostname = socket.gethostname()
service_list = ['apache2', 'mysql']


def send_mail(body='', keys=None):
    to = mail_to
    user = mail_from
    password = mail_pass
    server = "smtp.gmail.com"
    port = 587

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = to
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = 'Health Check Alert: %s' % hostname
    msg.attach(MIMEText(body))
    try:
        for file in keys:
            with open(file, "rb") as fil:
                part = MIMEApplication(fil.read(), Name=os.path.basename(file))
                part['Content-Disposition'] = 'attachment; filename="%s.pem"' % os.path.basename(file)
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
        smtp.close()
    except:
        print("Mail Sending Failed")


def check_disk():
    partitions = psutil.disk_partitions()
    min_disk_size = 1024*5
    disk_alert = ''
    for disk in partitions:
        try:
            ds = disk[1]
            stat = os.stat(disk[0])
            du = stat.st_blocks * stat.st_blksize
            st = os.statvfs(ds)
            free_m = ((st.f_bavail * st.f_frsize) / 1024) / 1024
            total_m = ((st.f_blocks * st.f_frsize) / 1024) / 1024
            used_m = (((st.f_blocks - st.f_bfree) * st.f_frsize)/1024)/1024
            if free_m < min_disk_size:
                if disk_alert:
                    disk_alert += "%s mounted on %s: Memory Low!!!!, %s MB Memory Left of %s MB\n" % (disk[0], ds, free_m, total_m)
                else:
                    disk_alert = "%s mounted on %s: Memory Low!!!!, %s MB Memory Left of %s MB\n" % (disk[0], ds, free_m, total_m)
        except:
            pass
    return disk_alert


def check_services():
    service_alert = ''
    for service in service_list:
        if int(subprocess.check_output('pgrep %s 1>>/dev/null; echo $?' % service, shell=True)) != 0:
            if service_alert:
                service_alert += "Service %s is not running\n" % service.upper()
            else:
                service_alert = "Service %s is not running\n" % service.upper()
    return service_alert


def check_memory():
    info_dict = {}
    highusage = 0
    for x in range(10):
        mem = str(subprocess.check_output("""free -m | grep Mem""", shell=True))
        mem_info = mem.split(' ', -1)
        mem_info = filter(None, mem_info)
        total = int(mem_info[1].lstrip().rstrip())
        free = int(mem_info[3].lstrip().rstrip()) + int(mem_info[5].lstrip().rstrip()) + int(mem_info[6].lstrip().rstrip())
        used = total - free
        used_per = (float(used)/float(total))*100
        info = [total, used, free, used_per]
        info_dict[x] = info
        time.sleep(1)

    for i in info_dict:
        print i, info_dict[i]
        if info_dict[i][3] > 75.0:
            highusage += 1
    if highusage > 5:
        return "RAM USAGE: %s, \nRAM Usage threshold Limit!\n" % max(info_dict.iteritems(), key=operator.itemgetter(1))[1][3]


def check_cpu():
    cpu_usage = psutil.cpu_percent(1, False)
    if cpu_usage > 75.0:
        return "CPU USAGE: %s, \nRAM Usage threshold Limit!\n" % cpu_usage


def health_check():
    msg = ''
    msg += check_disk()
    msg += check_services()
    msg += check_memory()
    msg += check_cpu()
    if msg:
       print msg
    else:
       print 'All is well!'

check_cpu()
