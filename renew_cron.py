import smtplib
import datetime
import sys
import os.path
from subprocess import Popen, PIPE

log_text = ""
domain = ""

def send_log():
        global log_text
        global domain

        SERVER = "localhost"
        FROM = "root@intx.cc"
        TO = ["root"]
        SUBJECT = "Certificate Renewal Information for " + domain + " [renew.py]"

        message = "From: %s\nTo: %s\nSubject: %s\n\n%s" % (FROM, ", ".join(TO), SUBJECT, log_text)

        server = smtplib.SMTP(SERVER)
        server.set_debuglevel(0)
        server.sendmail(FROM, TO, message)
        server.quit()

def log(msg):
        global log_text

        log_text += "[%s] " % (datetime.datetime.now()) + msg + "\n"

def end(errn):
        if (errn != 0):
                log("Error [" + str(errn) + "] Abort Programm")

        send_log()
        exit()

def request_cert(req):
        p = Popen(["python", "/home/letsencrypt/letsencrypt/acme_tiny.py", "--account-key", "/home/letsencrypt/letsencrypt/account.key", "--csr", req, "--acme-dir", "/srv/acme-challenge/"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        #p = Popen(["python", "./test.py", "--account-key ./account.key", "--csr " + req, "--acme-dir /srv/acme-challenge/"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode

        log("acme_tiny.py [" + str(rc) + "] says:\n" + err)

        if (rc != 0):
                end(rc)

        #log("Got cert: \n" + output + "\n")

        return output


log("renew.py started")

argv = sys.argv
argc = len(argv)

if (argc < 2):
        log("Missing command line arguments")
        end(-1)

site = sys.argv[1]
log("Get certificate for: " + site)

domain = site

csrpath = "/home/letsencrypt/letsencrypt/requests/" + site + ".csr"
if (os.path.isfile(csrpath)):
        log("CSR found in: " + csrpath)
else:
        log("No CSR found in: " + csrpath)
        end(-1)

crtpath = "/home/letsencrypt/certs/" + site + ".crt"
if (os.path.isfile(crtpath)):
        log("Old cert found in: " + crtpath)
else:
        log("No old cert found in: " + crtpath)
        end(-1)


cert = request_cert(csrpath)

log("Save cert temporarily to /home/letsencrypt/letsencrypt/tmp.crt")

try:
        f = open('/home/letsencrypt/letsencrypt/tmp.crt', 'w')
        f.seek(0)
        f.truncate()
        f.seek(0)
        f.write(cert)
        f.close()
except IOError:
        send_log()
        raise

log("Open intermediate cert")
f = open("/home/letsencrypt/certs/intermediate.crt", "r")
icrt = f.read()
f.close()

#log("Intermediate cert:\n" + icrt)

log("Write both to path of old cert")

try:
        f = open(crtpath, "w")
        f.seek(0)
        f.truncate()
        f.seek(0)
        f.write(cert)
        f.write(icrt)
        f.close
except IOError:
        send_log()
        raise

log("Certificate renewed. Server needs to be restarted now")


end(0)
