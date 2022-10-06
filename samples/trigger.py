

import pypylon.pylon as py
import pypylon.genicam as geni
import matplotlib.pyplot as plt
import numpy as np
import cv2
import time
import pandas as pd

# open the camera
tlf = py.TlFactory.GetInstance()
devices = tlf.EnumerateDevices()
if len(devices) == 0:
    raise py.RuntimeException("No camera present.")

# Create an array of instant cameras for the found devices and avoid exceeding a maximum number of devices.
maxCamerasToUse = 2
cameras = py.InstantCameraArray(min(len(devices), maxCamerasToUse))

l = cameras.GetSize()

# Create and attach all Pylon Devices.
for i, cam in enumerate(cameras):
    cam.Attach(tlf.CreateDevice(devices[i]))

    # Print the model name of the camera.
    print("Using device ", cam.GetDeviceInfo().GetModelName(), cam.GetDeviceInfo().GetUserDefinedName())

cam = cameras[1]
cam.Open()

# sample the io state with max possible framerate and chunks

# enable the chunk that
# samples all IO lines on every FrameStart
cam.ChunkModeActive = True
cam.ChunkSelector = "LineStatusAll"
cam.ChunkEnable = True

cam.ChunkSelector.Symbolics

('Gain',
 'ExposureTime',
 'Timestamp',
 'LineStatusAll',
 'CounterValue',
 'SequencerSetActive',
 'PayloadCRC16')

# set max speed
cam.Height = cam.Height.Min
cam.Width = cam.Width.Min
cam.ExposureTime = cam.ExposureTime.Min

# limit to 1khz
cam.AcquisitionFrameRateEnable = True
cam.AcquisitionFrameRate = 30
"""
print( cam.ResultingFrameRate.Value)
cam.StartGrabbingMax(1000)

io_res = []
while cam.IsGrabbing():
    with cam.RetrieveResult(1000) as res:
        time_stamp = res.TimeStamp
        io_res.append((time_stamp, res.ChunkLineStatusAll.Value))

cam.StopGrabbing()


# list of timestamp + io status
io_res[:10]
# simple logic analyzer :-)

# convert to numpy array
io_array = np.array(io_res)
# extract first column timestamps
x_vals = io_array[:,0]
#  start with first timestamp as '0'
x_vals -= x_vals[0]

# extract second column io values
y_vals = io_array[:,1]
# for each bit plot the graph
for bit in range(8):

    logic_level = ((y_vals & (1<<bit)) != 0)*0.8 +bit
    # plot in seconds
    plt.plot(x_vals / 1e9, logic_level, label = bit)

plt.xlabel("time [s]")
plt.ylabel("IO_LINE [#]")
plt.legend()
plt.show()"""

# get clean powerup state
cam.UserSetSelector = "Default"
cam.UserSetLoad.Execute()

cam.LineSelector = "Line3"
cam.LineMode = "Input"

cam.TriggerSelector = "FrameStart"
cam.TriggerSource = "Line3"
cam.TriggerMode = "On"
cam.TriggerActivation.Value


res = cam.GrabOne(py.waitForever)



# definition of event handler class
class TriggeredImage(py.ImageEventHandler):
    def __init__(self):
        super().__init__()
        self.grab_times = []
        self.converter = py.ImageFormatConverter()
        self.converter.OutputPixelFormat = py.PixelType_BGR8packed
        self.converter.OutputBitAlignment = py.OutputBitAlignment_MsbAligned
    def OnImageGrabbed(self, camera, grabResult):
        self.grab_times.append(grabResult.TimeStamp)
        image = self.converter.Convert(grabResult)
        img = image.GetArray()
        cv2.namedWindow('title', cv2.WINDOW_NORMAL)
        cv2.imshow('title', img)
        cv2.waitKey(1)

# create event handler instance
image_timestamps = TriggeredImage()

# register handler
# remove all other handlers
cam.RegisterImageEventHandler(image_timestamps,
                              py.RegistrationMode_ReplaceAll,
                              py.Cleanup_None)

# start grabbing with background loop
cam.StartGrabbingMax(10000, py.GrabStrategy_LatestImages, py.GrabLoop_ProvidedByInstantCamera)
# wait ... or do something relevant
print("start grabbing")
while cam.IsGrabbing():
    time.sleep(0.1)

# stop grabbing
cam.StopGrabbing()


print(np.diff(image_timestamps.grab_times))


frame_delta_s = np.diff(np.array(image_timestamps.grab_times))/1.e9
plt.plot(frame_delta_s, ".")
plt.axhline(np.mean(frame_delta_s))



plt.hist(frame_delta_s  - np.mean(frame_delta_s) , bins=100)
plt.xticks(rotation=45)
plt.show()



cam.Close()
