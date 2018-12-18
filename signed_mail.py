### Written by Mark Bregman

####################
#
# Copyright (c) 2018 Fox-IT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISNG FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
####################

#thx: https://m2crypto.readthedocs.io/en/latest/howto.smime.html#m2crypto-smime

import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from M2Crypto import BIO, Rand, SMIME


def makebuf(text):
    return BIO.MemoryBuffer(text)

mail_server = "127.0.0.1"
mail_port = 25
fromaddr = "john.doe@fox-it.cm"
toaddr = "target@fox-it.com"
subject = "Example Subject"
_sign = True

msg = MIMEMultipart()

msg['From'] = fromaddr
msg['To'] = toaddr
msg['Subject'] = subject
body = "Example Text"

msg.attach(MIMEText(body, 'plain'))

if _sign:
    msg_str = msg.as_string()

    # Make a MemoryBuffer of the message.
    buf = makebuf(msg_str)

    # Seed the PRNG.
    Rand.load_file('randpool.dat', -1)

    # Instantiate an SMIME object; set it up; sign the buffer.
    # Make sure the certicate and key are in the same folder where the script is run from
    s = SMIME.SMIME()
    s.load_key('key.pem', 'cert.pem')
    p7 = s.sign(buf, SMIME.PKCS7_DETACHED)

    # Recreate buf.
    buf = makebuf(msg_str)

    # Output p7 in mail-friendly format.
    out = BIO.MemoryBuffer()
    out.write('From: %s\n' % fromaddr)
    out.write('To: %s\n' % toaddr)
    out.write('Subject: %s\n' % subject)

    s.write(out, p7, buf)
    text = out.read()

    # Save the PRNG's state.
    Rand.save_file('randpool.dat')
else:
    text = msg.as_string()

server = smtplib.SMTP(mail_server, mail_port)
server.sendmail(fromaddr, toaddr, text)
server.quit()
