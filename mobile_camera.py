import cv2

class MobileCamera:
    def getVideo(self,camera):
        self.camera=camera
        cap=cv2.VideoCapture(self.camera)
        while True:
            ret,frame=cap.read()
            #frame=cv2.resize(frame,(0,0),fx=0.50,fy=0.50)
            cv2.imshow("MY MOBILE CAMERA", frame)
            if cv2.waitKey(1)==ord("q"):
                break
        cap.release()
        cv2.destroyAllWindows()

can=MobileCamera()
can.getVideo("http://10.243.105.250:8080/video")