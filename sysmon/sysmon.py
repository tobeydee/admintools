#!/usr/bin/python
# -*- coding: utf-8 -*-

__doc__ = 'Monitors a UNIX based system by a given set of functions.'

import os
import subprocess
import pickle
import smtplib
import datetime
import email.mime.text
import ConfigParser

global_config = ConfigParser.SafeConfigParser()
global_config.read('sysmon.conf')


class FileSystemUsage(object):
    
    def __init__(self, df_minus_h_output):
        self.usage = self.__parse__(df_minus_h_output[1:]) # skip first line (header) in output
    
    def __parse__(self, list_of_strings):

        def helper(line):
            list_of_strings = map(lambda x: x.replace('\n', '').replace('%', ''), line.split(' ')[-2:])
            a,b = tuple(reversed(list_of_strings))
            return (a, int(b)) # convert percentage from string to integer

        return dict(map(lambda line: helper(line), list_of_strings))
    
    def changed(self, last):
        """ Returns the difference of the current usage compared with the prev. usage. """

        usage_items = self.usage.items()

        return list(set(usage_items) - set(last.usage.items()) & set(usage_items))


def __send_mail_wrapper__(subject, content):
    """ Send an email using an external SMTP server """

    smtp_host = global_config.get('mail', 'smtp_host')

    smtp_port = global_config.get('mail', 'smtp_port')

    smtp_user = global_config.get('mail', 'smtp_user')

    smtp_pass = global_config.get('mail', 'smtp_pass')

    mail_from_addr = global_config.get('general', 'mail_from_addr')

    mail_to_addr = global_config.get('general', 'mail_to_addr')    

    msg = email.mime.text.MIMEText(content)

    msg['Subject'] = subject

    msg['From'] = mail_from_addr

    msg['To'] = mail_to_addr

    s = smtplib.SMTP_SSL(smtp_host, int(smtp_port))

    s.login(smtp_user, smtp_pass)

    s.sendmail(mail_from_addr, [mail_to_addr], msg.as_string())

    s.quit()


def send_mail(subject, content):
    """ Send an email with the given subject and content """

    if type(content) is list:
        content = list_to_string_with_newlines(content)

	mail_from_addr = global_config.get('general', 'mail_from_addr')

	mail_to_addr = global_config.get('general', 'mail_to_addr')
	
    __send_mail_wrapper__(subject, content)


def list_to_string_with_newlines(xs):
    return reduce(lambda a,b: a + b + '\n', map(lambda x: str(x), xs))


def qx(cmd):
    """ Does the same as the qx() function in Perl: Execute the given command! """
    return subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE).stdout.readlines()


def check_hdd_usage():
    """ Monitor usage of mounted file systems """

    local_storage_filename = global_config.get('general', 'local_storage')

    if not os.path.exists(local_storage_filename):
        send_mail('Local storage file does not exist!', '')
        pickle.dump(FileSystemUsage(qx('df -h')), file(local_storage_filename, 'w'))
        return -1
    
    curr = FileSystemUsage(qx('df -h'))
    
    last = pickle.load(file(local_storage_filename, 'r'))
    
    diff = curr.changed(last)
    
    if diff:
        overview = ['previous usage: ' + str(last.usage['/']), 'current usage: ' + str(diff)]
        send_mail("File System Usage!", overview)
	
    pickle.dump(curr, file(local_storage_filename, 'w'))
    
    
def check_jetty_log_size():
    """ Monitors the size of the current jetty.log file """
    

def check_jetty_log():
    """ Check for HTTP 40x and 30x errors """
    
    def extract(xs):
        """ Extract data form given list-of-strings """
        def get_url():
            return xs[5]

        def get_http_status():
            return xs[7]

        return get_url() + ' ' + get_http_status().replace(',', '')

    jetty_log = global_config.get('monitoring', 'jetty_log')
	
    errors = qx("cat " + jetty_log + " | egrep '\<returned\> (30.|40.)'")

    errors = map(lambda line: extract(line.split(' ')), errors)
    
    hour = datetime.datetime.now().hour
    
    if errors and (hour > 21):
        errors = sorted(set(errors))
        head_line = ['--- ' + str(len(errors)) + ' errors detected: ---']
        send_mail('HTTP Errors', head_line + errors)
    

def check_bookshop_logins():
    """ Monitor login attemps to /bookshop/user_mgt """
    

def check_dmesg():
    """ Monitor system messages """
    

def check_listening_ports():
    """ Make sure that all (IPv4) required deamons are up and running """


def check_listening_ports_v6():
    """ Make sure that all IPv6 deamons are up and running """
    

def check_auth_log():
    """ Searches auth.log for authentication failures (e.g. SSH) """

    auth_log = global_config.get('monitoring', 'auth_log')

    failures = qx("cat " + auth_log + " | egrep -i fail")

    if failures:
        send_mail("Authentication Failures!", failures)
    

def check_for_reboot():
    """  Searches syslog for 'restart' entries """
    

def check_for_updates():
    """ Check for available updates """
    
    apt_get_cmd = 'apt-get update > /dev/null && apt-get -s upgrade'
    
    grep_cmd = "egrep '^([1-9][0-9]*) aktualisiert, ([0-9]+) neu installiert, ([0-9]+) zu entfernen und ([0-9]+) nicht aktualisiert.$'"
    
    updates = qx(apt_get_cmd + '|' + grep_cmd)
    
    if updates:
        send_mail("Updates Available", qx('apt-get upgrade -s --just-print'))


def check_firewall():
    """ Check that firewall rules are enabled """
	
	current_iptables_rules = qx('iptables -L')

    if current_iptables_rules != open(global_config.get('monitoring', 'iptables_rules')).readlines():
        send_mail("Firewall not configured!", current_iptables_rules)


def check_load_avg():
    """ Monitor the average system load to identify abnormal behaviour """
    
    load_avg = qx("uptime | egrep 'load average: ([1-9]+).(..), ([1-9]+).(..), ([1-9]+).(..)'")
    
    if load_avg:
        send_mail("Load Average High!", load_avg)


def run_checks():
    check_hdd_usage()
    
    check_jetty_log()
    
    check_auth_log()
    
    check_for_updates()
    
    check_load_avg()

	check_firewall()


if __name__ == '__main__':
	run_checks()
