import serial
import time
import cv2
import numpy as np

# Init Serial Communication
USB_serial = serial.Serial(port='/dev/ttyACM0',
    baudrate=57600,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=0.5)
print("USB Serial communication enable.")
time.sleep(1)

# Cascade classifier file
face_cascade = cv2.CascadeClassifier('/home/pi/opencv-3.2.0/data/haarcascades/haarcascade_frontalface_default.xml')

def init_global_variables():
    global Flag_serial_available,Flag_serial_answer,Serial_data_out,Serial_data_in
    Flag_serial_available = True
    Flag_serial_answer = True
    Serial_data_out = "E090A090"
    Serial_data_in = "E090A090"

def serial_send_data(Serial_data_out):
    global Flag_serial_available,USB_serial
    if Flag_serial_available == True:
        USB_serial.write(Serial_data_out.encode())
        print('RPi_serial : ' + Serial_data_out)
        Flag_serial_available = False
    else:
        print("/!\ WARNING : Waiting for answer before sending new commands to Arduino ..")

def display(frame_array,AZ,EL,xcam_res,ycam_res):
    global Serial_data_out,Serial_data_in
    # Center cross
    cv2.line(frame_array,(int(xcam_res/2)-10,int(ycam_res/2)),(int(xcam_res/2)+10,int(ycam_res/2)),(139,0,139),2)
    cv2.line(frame_array,(int(xcam_res/2),int(ycam_res/2)-10),(int(xcam_res/2),int(ycam_res/2)+10),(139,0,139),2)
    # AZ & EL
    cv2.line(frame_array,(int(1),int(ycam_res-EL*ycam_res/180)),(int(xcam_res),int(ycam_res-EL*ycam_res/180)),(15,15,15),1)
    cv2.line(frame_array,(int(AZ*xcam_res/180),int(1)),(int(AZ*xcam_res/180),int(ycam_res)),(15,15,15),1)
    font = cv2.FONT_HERSHEY_DUPLEX
    cv2.putText(frame_array,str(Serial_data_in),(5,ycam_res-10), font, 0.5,(15,15,15),1,cv2.LINE_AA)
    #cv2.circle(frame_array,(90,10), 3, (255,255,255), 1)
    #cv2.circle(frame_array,(90,30), 3, (255,255,255), 1)
    # Display
    window_name = 'Full_Screen'
    cv2.namedWindow(window_name, cv2.WND_PROP_FULLSCREEN)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
    cv2.imshow(window_name, frame_array)

def serial_is_available():
    global Flag_serial_answer,Flag_serial_available,Serial_data_in
    if USB_serial.inWaiting()>0:
        Serial_data_in = USB_serial.readline().decode("ascii")
        print('Arduino_serial : ' + Serial_data_in)
        if 'OK' or 'E' in Serial_data_in:
            Flag_serial_available=True
        elif 'ERROR' in Serial_data_in:
            print("/!\ WARNING : Arduino return ERROR !" + Serial_data_out)
            Flag_serial_available=True
        else:
            Flag_serial_available=True
            print("ERROR : Arduino answer is not correct : " + Serial_data_in)
    elif Flag_serial_answer == True:
        Flag_serial_answer = False
        Flag_serial_available = True
    else:
        print("/!\ WARNING : Arduino did not answer ..")
        Flag_serial_available = False

def follow_faces(x_cv2,y_cv2,w_cv2,h_cv2,AZ,EL,xcam_res,ycam_res):
    global Flag_serial_available,Serial_data_out
    x_dif = x_cv2+w_cv2/2-xcam_res/2
    y_dif = y_cv2+h_cv2/2-ycam_res/2
    ax = np.tan(0.036/0.082/14)
    ay = np.tan(0.098/0.105/22)
    dx = 0.25/2/np.arctan(ax)
    dy = 0.28/2/np.arctan(ay)
    xl = x_dif*0.25/w_cv2
    yl = y_dif*0.28/h_cv2
    AZ_target = int(AZ+ 360/2/3.14*np.tan(xl/dx))
    EL_target = int(EL- 360/2/3.14*np.tan(yl/dy))
    if AZ_target > 180:
        AZ_target = 180
    if AZ_target < 0:
        AZ_target = 0
    if EL_target > 180:
        EL_target = 180
    if EL_target < 0:
        EL_target = 0
    print(type(x_dif))
    if np.greater(np.abs(x_dif), w_cv2/2) == True or np.greater(np.abs(y_dif), h_cv2/2) == True:
        Serial_data_out = "E"+str("{0:0=3d}".format(EL_target))+"A"+str("{0:0=3d}".format(AZ_target))
        serial_is_available()
        serial_send_data(Serial_data_out)

def ask_serial_pos():
    global Serial_data_in,Flag_serial_available,Flag_serial_answer,Serial_data_out
    serial_is_available()
    if Flag_serial_available == True:
        Serial_data_out = "R" # Ask arduino position
        serial_send_data(Serial_data_out)
        time.sleep(0.05)
        if USB_serial.inWaiting()>0: # read arduino position
            Serial_data_in = USB_serial.readline().decode("ascii") #decode
            print('Arduino_serial : ' + Serial_data_in)
            Flag_serial_answer = True
        else:
            print("/!\ WARNING : Arduino did not answer position !")
            Flag_serial_answer = False
    else:
        print("/!\ WARNING : Serial is not available for asking position to Arduino !")
        Flag_serial_answer = False
    EL = 100*(int(Serial_data_in[1]))+10*(int(Serial_data_in[2]))+(int(Serial_data_in[3]))
    AZ = 100*(int(Serial_data_in[5]))+10*(int(Serial_data_in[6]))+(int(Serial_data_in[7]))
    return [AZ, EL]

def detection_process(frame_array,xcam_res,ycam_res):
    gray = cv2.cvtColor(frame_array, cv2.COLOR_BGR2GRAY) # Only gray color extraction
    faces = face_cascade.detectMultiScale(gray, 1.3, 5) # Face Detection
    # Face detected
    for (x,y,w,h) in faces:
        cv2.rectangle(frame_array,(x,y),(x+w,y+h),(255,0,0),2)
        return [True,x,y,w,h]
    else:
        return [False,0,0,0,0]

def kill_all_ps():
    # Release the capture:
    cv2.destroyAllWindows()
    # Close Serial
    USB_serial.close()
    print("USB Serial communication closed.")
