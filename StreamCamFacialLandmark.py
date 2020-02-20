#!/usr/bin/python.
'''
	Author: ILGIN DOĞAN -- lgndogan@gmail.com
	Simple Facial Landmark and Stream Server v1.0
'''
import cv2
from PIL import Image
import threading
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import time
import numpy as np
import cv2 as cv
import json
import os
import imutils
import math

capture=None

class OpenCam(BaseHTTPRequestHandler):

    def do_GET(self):
        smilePath = './haarcascade_smile.xml' # if you put xml file on same directory
        eyePath = './haarcascade_eye.xml'# if you put xml file on same directory
        face_path = './haarcascade_frontalface_default.xml'# if you put xml file on same directory

        faceCascade = cv.CascadeClassifier(face_path)
        eyeCascade = cv.CascadeClassifier(eyePath)
        smileCascade = cv.CascadeClassifier(smilePath)
        if self.path.endswith('.mjpg'):
            self.send_response(200)
            self.send_header('Content-type','multipart/x-mixed-replace; boundary=jpgboundary')
            self.end_headers()
            while True:
                try:
                    rc,img = capture.read()
                    img = imutils.resize(img,width=640)
                    if rc:
                        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
                        # Face Detection
                        faces = faceCascade.detectMultiScale(gray,1.3,3)

                        for (x,y,w,h) in faces:
                            cv.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
                            roi_gray = gray[y:y+h, x:x+w]
                            roi_color = img[y:y+h, x:x+w]
                            # Eye Detection
                            eyes = eyeCascade.detectMultiScale(roi_gray,1.3,3)
                            for (ex,ey,ew,eh) in eyes:
                                cv.putText(img,"Face Detected",(x,y),cv.FONT_ITALIC,1,(0,0,255),2)
                                smile = smileCascade.detectMultiScale(roi_gray,1.5,25)
                                # Based on Face and Eye detection smile detection
                                for (ax,ay,aw,ah) in smile:
                                    cv.rectangle(roi_color,(ax,ay),(ax+aw,ay+ah),(255,0,0),1)
                                    cv.putText(img,"You Are Smiling",(ax+100,ay+100),cv.FONT_ITALIC,1,(150,255,255),2)

                    cv.putText(img," FACIAL EMOTION - FACE DETECTION ",(20,50),cv.FONT_ITALIC,0.7,(255,255,255),1,cv.LINE_AA)


                    if not rc:
                        continue
                    imgRGB=cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
                    jpg = Image.fromarray(imgRGB)
                    tmpFile = StringIO.StringIO()
                    jpg.save(tmpFile,'JPEG')
                    self.wfile.write("\r\n--jpgboundary\r\n")
                    self.send_header('Content-type','image/jpeg')
                    self.send_header('Content-length',str(tmpFile.len))
                    self.end_headers()
                    jpg.save(self.wfile,'JPEG')
                except KeyboardInterrupt:
                    break
            return
        if self.path.endswith('.html'):
            self.send_response(200)
            self.send_header('Content-type','text/html')
            self.end_headers()
            self.wfile.write('<html><head></head><body>')
            self.wfile.write('<img src="http://192.168.0.104:8282/camera.mjpg"/>')
            self.wfile.write('</body></html>')
            return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	global capture
	capture = cv2.VideoCapture(0)
	global img
	try:
		server = ThreadedHTTPServer(('0.0.0.0', 8282), OpenCam)
		print ("Server Opened")
		server.serve_forever()
	except KeyboardInterrupt:
		capture.release()
		server.socket.close()

if __name__ == '__main__':
	main()
