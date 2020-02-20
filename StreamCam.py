#!/usr/bin/python.
'''
	Author: ILGIN DOĞAN -- lgndogan@gmail.com
	A Simple mjpg stream http server v1.0
'''
import cv2
from PIL import Image
import threading
from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
from SocketServer import ThreadingMixIn
import StringIO
import imutils
from imutils.video import VideoStream
capture=None

class OpenCam(BaseHTTPRequestHandler):
	def do_GET(self):
		if self.path.endswith('.mjpg'):
			self.send_response(200)
			self.send_header('Content-type','multipart/x-mixed-replace; boundary=jpgboundary')
			self.end_headers()
			while True:
				try:
					img = capture.read() # if you use VideoStream
					# rc,img = capture.read()
					#if not rc:  if you use VideoCapture rc is needed
						#continue
					#img = capture.read()
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
			self.wfile.write('<img src="http://127.0.0.1:8081/camera.mjpg"/>') # ThreadedHTTPServer(('0.0.0.0', 8081) change port two directory
			self.wfile.write('</body></html>')
			return


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
	"""Handle requests in a separate thread."""

def main():
	global capture
	#capture = cv2.VideoCapture(0) # VideoCapture mode for webcam
	capture = VideoStream(src=0).start() # Webcam Camera
	capture = VideoStream(usePiCamera=True).start() # Picamera
	global img
	try:
		server = ThreadedHTTPServer(('0.0.0.0', 8081), OpenCam) # if you want to change your port status like 8081 convert to 5001
		print ("Server Opened")
		server.serve_forever()
	except KeyboardInterrupt:
		capture.release()
		server.socket.close()

if __name__ == '__main__':
	main()
