import argparse
import dns.resolver
from email.message import EmailMessage
import smtplib

def SendMail(from_addr, to_addr, subj, mail_body_file, helo, auth_usr, auth_pass, auth_serv, auth_port, auth_tls):

    ip_list = []
    resolver = dns.resolver.Resolver()
    to_addr_split = to_addr.split('@')
    dns_query = resolver.query(to_addr_split[1], 'MX')

    for rdata in dns_query:
        ip_addresses = resolver.query(rdata.exchange, 'A')
        for ip in ip_addresses:
            new_ip = ip.to_text()
            ip_list.append(new_ip)

    msg = EmailMessage()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subj

    with open(mail_body_file) as f:
        msg.set_content(f.read())

    if (auth_usr != '') and (auth_pass != '') and (auth_serv != ''):
        try:
            client = smtplib.SMTP(auth_serv, auth_port)
            print('Connecting to server %s on port %s' % (auth_serv, auth_port))
            if auth_tls:
                client.starttls()
                print('Using TLS')
            client.login(auth_usr, auth_pass)
            print('Logging in to account', auth_usr)
            client.send_message(msg)
            print('Mail sent successfully')
        except BaseException as e:
            print('Failed to send mail:', e)
    else:
        for ip in ip_list:
            try:
                print('Trying to send mail to remote host', ip)
                client = smtplib.SMTP(host=ip,port='25',local_hostname=helo)
                client.send_message(msg)
                print('Mail sent successfully')
                break
            except BaseException as e:
                print('Failed to send mail:', e)

parser = argparse.ArgumentParser(description='Mail sender - A script that sends mails.')

parser.add_argument(
    '-f', '--from', required=True, metavar='from@domain.com', dest='from', help='sender e-mail address')
parser.add_argument(
    '-t', '--to', required=True, metavar='to@domain.com', dest='to', help='recipient e-mail address')
parser.add_argument(
    '-s', '--subject', required=False, metavar='subject', dest='subject', default='', help='e-mail subject')
parser.add_argument(
    '-b', '--body', required=True, metavar='C:\\path\\to\\file.txt', dest='body', help='fullpath to plaintext file containing the body of the e-mail')
parser.add_argument(
    '-o', '--origin', required=False, metavar='smtp.example.com', dest='helo', default='smtp.example.com', help='local hostname, can be fake')
parser.add_argument(
    '-u', '--username', required=False, metavar='user@domain.com', dest='user', default='', help='username, if logging into a remote mail server')
parser.add_argument(
    '-p', '--password', required=False, metavar='password', dest='pass', default='', help='password, if logging into a remote server')
parser.add_argument(
    '--server', required=False, metavar='smtp.domain.com', dest='server', default='', help='remote server to log into')
parser.add_argument(
    '--port', required=False, metavar='xxx', dest='port', default='', help='port to connect to in the remote server')
parser.add_argument(
    '--tls', required=False, metavar='0, 1', type=int, dest='tls', default=0, choices=[0, 1], help='1 for tls on, 0 for off')

args = parser.parse_args()

SendMail(getattr(args, 'from'), getattr(args, 'to'), getattr(args, 'subject'), getattr(args, 'body'), getattr(args, 'helo'),\
    getattr(args, 'user'), getattr(args, 'pass'), getattr(args, 'server'), getattr(args, 'port'), getattr(args, 'tls'))
