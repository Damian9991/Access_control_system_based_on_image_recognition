import cv2
import sys
import time

cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)


def capture_video(video_source):
    video_capture = cv2.VideoCapture(video_source)

    img_counter = 0
    while True:
        # Capture frame-by-frame

        ret, frame = video_capture.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30),
            flags=cv2.cv.CV_HAAR_SCALE_IMAGE
        )

        # Draw a rectangle around the faces
#        for (x, y, w, h) in faces:
#            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        if len(faces) > 0:
            img_name = "opencv_frame_{}.png".format(img_counter)
            resize = cv2.resize(frame, (600, 400))
            cv2.imwrite(img_name, resize)
            print("{} written!".format(img_name))
            img_counter += 1
            time.sleep(5) 


        # Display the resulting frame
        cv2.imshow('Video', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            video_capture.release()
            cv2.destroyAllWindows()
            break


#        if cv2.waitKey(1)%256 == 32:
#            # SPACE pressed
#            img_name = "opencv_frame_{}.png".format(img_counter)
#            resize = cv2.resize(frame, (600, 400))
#            cv2.imwrite(img_name, resize)
#            print("{} written!".format(img_name))
#            img_counter += 1



if __name__ == "__main__":
    try:
        capture_video("http://" + str(sys.argv[1]) + ":8160")     
    except IndexError as err:
        capture_video(0)

