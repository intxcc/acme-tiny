import time
import smtplib
from subprocess import Popen, PIPE

logg = ""

svcs = ["nginx", "postfix", "dovecot"]

for s in svcs:
        logg += "restarted " + s + "\n"

        p = Popen(["/usr/sbin/service", s, "restart"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode

        logg += output + err

time.sleep(10)


SERVER = "localhost"
FROM = "root@intx.cc"
TO = ["root"]
SUBJECT = "Services restarted for cert renewal"
MSG = "Services restarted for certificate renewal\n" + logg

message = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (FROM, ", ".join(TO), SUBJECT, MSG)

server = smtplib.SMTP(SERVER)
server.set_debuglevel(0)
server.sendmail(FROM, TO, message)
server.quit()

