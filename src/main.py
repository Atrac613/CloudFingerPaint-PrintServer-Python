# *-# -*- coding: utf-8 -*-

import os
from threading import Timer

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont

import datetime
import simplejson
import urllib2

PRINTER_NAME = '"EPSON TM-T90 Receipt"'

GSPRINT_COMMAND = 'gsprint.exe'
API_URL = 'http://cloud-finger-paint.appspot.com/api/%s'

def checkQueue():
    printLOG('Queue', 'Getting queue list.')

    try:
        json = simplejson.loads(urllib2.urlopen(API_URL % 'get_queue_list').read())
        for row in json:
            createPDF(row['id'], row['image_url'])
            printPDF(row['id'])
            updateQueueFlag(row['id'], False)
        
    except:
        printLOG('Queue', 'Failed.')
        
def updateQueueFlag(queue_id, flag):
    printLOG('Update', 'Setting queue flag.')
    
    API_UPDATE_URL = API_URL % 'update_queue_flag?id=%s&flag=%s'
    
    try:
        json = simplejson.loads(urllib2.urlopen(API_UPDATE_URL % (queue_id, False)).read())
        if json['status']:
            printLOG('Update', 'Success.')
    except:
        printLOG('Update', 'Failed.')

def createPDF(queue_id, image_url):
    printLOG('PDF', 'Creating PDF.')
    os.chdir('pdf')
    
    filename = '%s.pdf' % queue_id
    
    printLOG('PDF', 'Creating ' + filename)
    
    c = canvas.Canvas(filename, pagesize=(220,400))
    msgothic = TTFont('MS Gothic','msgothic.ttc',subfontIndex=0,asciiReadable=0)
    pdfmetrics.registerFont(msgothic)
    
    try:
        c.drawInlineImage(image_url, 0, 0, width=220, preserveAspectRatio=True)
    except:
        pass
        
    c.showPage()
    c.save()
    
    os.chdir('..' + os.sep)
    
def printPDF(queue_id):
    printLOG('PRINT', 'Printing PDF.')
    os.chdir('pdf')
    
    filename = '%s.pdf' % queue_id
    
    printLOG('PRINT', 'Printing %s' % filename)
    
    if (os.path.isfile(filename)):
        os.system(GSPRINT_COMMAND + ' -printer ' + PRINTER_NAME + ' ' + filename)
        
    os.chdir('..' + os.sep)

def printLOG(section, log):
    date = datetime.datetime.today()
    print '[%s - %s] %s' % (date.strftime('%Y-%m-%d %H:%M:%S'), section, log)

if __name__ == "__main__":
    printLOG('SYSTEM', 'Starting CloudFingerPaint ...')
    
    checkQueue()
    
    sec = 30.0
    
    printLOG('SYSTEM', 'Timer Setting. (%d sec)' % sec)
    
    while True:
        t = Timer(sec, checkQueue)
        t.run()