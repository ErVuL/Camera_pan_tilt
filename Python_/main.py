from cv2 import waitKey,destroyAllWindows
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import myLib as mL
from numpy import random

# Init Camera:
xcam_res = 480
ycam_res = 320
camera = PiCamera()
camera.resolution = (xcam_res, ycam_res)
camera.framerate = 32
camera.vflip = True
rawCapture = PiRGBArray(camera, size=(xcam_res, ycam_res))

mL.init_global_variables()
mL.serial_send_data("E090A090") # Robot position_0

time.sleep(0.1)
t_0 = time.time()
t_1 = time.time()
# Capture frames from the camera:
for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):

    face_detected = False
    frame_array = frame.array # Format to numpy array

    [face_detected,x,y,w,h] = mL.detection_process(frame_array,xcam_res,ycam_res) # Face Detection
    [AZ,EL] = mL.ask_serial_pos() # Asking arduino's motors positions
    
    if face_detected == True:
        mL.follow_faces(x,y,w,h,AZ,EL,xcam_res,ycam_res) # follow face
        t_0 = time.time() # time without detection
    if (time.time() - t_0) > 5:
            if (time.time() - t_1) > 3.5:
                EL_target = int(80 + 40*random.rand(1,1))
                AZ_target = int(45+ 90*random.rand(1,1))
                t_1 = time.time()
                Serial_data_out = "E"+str("{0:0=3d}".format(EL_target))+"A"+str("{0:0=3d}".format(AZ_target))
                mL.serial_is_available()
                mL.serial_send_data(Serial_data_out)

    mL.display(frame_array,AZ,EL,xcam_res,ycam_res) # HUD & Display

    rawCapture.truncate(0) # Clean for next frame

    if waitKey(1) & 0xFF == ord('q'): # exit typing 'q'
        break

mL.serial_send_data("E090A090") # Robot position_0
mL.kill_all_ps()
