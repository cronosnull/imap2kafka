#!/usr/bin/env python
# -*- coding: utf-8 -*

"""
A simple kafka producer to send email messages to the broker.
It will use the email date as the message timestamp.
"""

import os
import sys
from kafka import KafkaProducer
import imaplib
import email
import logging
import time
import json
from datetime import datetime, timedelta

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
USERNAME = os.environ.get('I2K_USERNAME', None)
PASSWORD = os.environ.get('I2K_PASSWORD', None)
IMAP_SERVER = os.environ.get('I2K_IMAP_SERVER', 'imap.gmail.com')
FOLDER = os.environ.get('I2K_FOLDER', 'INBOX')
TOPIC = os.environ.get('I2K_TOPIC', 'email_alert')

bootstrap_servers = os.environ.get('I2K_KAFKA_SERVERS',
                                   '127.0.0.1:9092').split(',')
producer = KafkaProducer(bootstrap_servers=bootstrap_servers,
                         value_serializer=lambda v:
                             json.dumps(v).encode('utf-8'))


def getLastUpdate():
    _cp = datetime.now() - timedelta(days=60)
    if os.path.isfile('checkpoint'):
        _cp = datetime.fromtimestamp(os.stat('checkpoint').st_atime)
    return _cp


def touch(path):
    with open(path, 'a'):
        os.utime(path, None)

last_checkpoint = getLastUpdate()
# Imap SINCE search only doesn't allow a specific time,
# only date.
f_date = last_checkpoint.strftime('%d-%b-%Y')
imap_cn = imaplib.IMAP4_SSL(IMAP_SERVER)
logging.debug("Last Update %s" % last_checkpoint)

try:
    r, data = imap_cn.login(user=USERNAME, password=PASSWORD)
except imaplib.IMAP4.error as e:
    logging.error('Login error: %s' % e)
    sys.exit(-1)

if r == 'OK':
    r, data = imap_cn.select(FOLDER, readonly=True)
    logging.debug('imap select response %s' % r)
    if r == 'OK':
        r, ms = imap_cn.search(None, '(SINCE "%s")' % f_date)
        touch('checkpoint')
        ids = ms[0].split()
        for num in ids:
            rv, data = imap_cn.fetch(num, '(RFC822)')
            if rv != 'OK':
                logging.error("ERROR getting message", num)
                continue
            msg = email.message_from_bytes(data[0][1])
            hdr = email.header.make_header(
             email.header.decode_header(msg['Subject']))
            date_tuple = email.utils.parsedate(msg['Date'])
            logging.debug((str(hdr), date_tuple))
            body = ''
            if msg.is_multipart():
                body = '\n'.join([x.get_payload() for x in msg.get_payload()])
            else:
                body = str(msg.get_payload())

            logging.debug(body)
            producer.send(TOPIC,
                          {'subject': str(hdr), 'body': body},
                          timestamp_ms=int(time.mktime(date_tuple)*1000))

producer.flush()
