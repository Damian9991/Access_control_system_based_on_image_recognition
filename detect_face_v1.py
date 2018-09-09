# -*- coding: utf-8 -*-
import cv2
import sys
x=0
y=0

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)
font=cv2.FONT_HERSHEY_SIMPLEX
video_capture = cv2.VideoCapture(0)

while True:
    # CAPTURE FRAME-BY-FRAME
    ret, frame = video_capture.read()

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    faces = faceCascade.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(50, 50),
        #when the values are smallers, the face to detect can be smaller
        flags=cv2.cv.CV_HAAR_SCALE_IMAGE

    )
    # DRAW A RECTANGLE AROUND THE FACES FOUND
    for (x, y, w, h) in faces:
        # ---To draw a rectangle this are the parameters
        # cv2.rectangle(img,(x1,y1),(x2,y2),(255,0,0),2)
        # img is the image variable, it can be "frame" like in this example
        # x1,y1 ---------
        # |              |
        # |              |
        # |              |
        # -------------x2,y2
        # (255,0,0) are (R,G,B)
        # the last 2 is the thickness of the line 1 to 3 thin to gross
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 100), 1)

        #---To write the x,y on the middle of the rectangle.
        stringxy="+%s,%s"%(x,y) # To prepare the string with the xy values to be used with the cv2.putText function
        #In the case we want to put Xxvalue,Yyvalue we can use the following line removing #.
        #stringaxy="X%s,Y%s"%(x,y) 
        cv2.putText(frame,stringxy,(x+w/2,y+h/2),font, 1,(0,0,255),1)


    # DISPLAY THE RESULTING FRAME
    cv2.imshow('Video', frame)
    print x,y,
    print"\n"
    #font=cv2.FONT_HERSHEY_SIMPLEX
    #cv2.putText(faces,'x,y',(x,y),font, 2,(255,255,255),1)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
