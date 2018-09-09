import cv2

cap = cv2.VideoCapture(0)

ret, img = cap.read()
print(ret)
print(img)
