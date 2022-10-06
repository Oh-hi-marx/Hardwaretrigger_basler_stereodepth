# Grab_Strategies.cpp
# ===============================================================================
# #    This sample shows the use of the Instant Camera grab strategies.
# ===============================================================================

import sys
import time

from pypylon import pylon

from samples.imageeventprinter import ImageEventPrinter
from samples.configurationeventprinter import ConfigurationEventPrinter

# The exit code of the sample application.
exitCode = 0

# Create an instant camera object for the camera device found first.
camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

# Register the standard configuration event handler for enabling software triggering.
# The software trigger configuration handler replaces the default configuration
# as all currently registered configuration handlers are removed by setting the registration mode to RegistrationMode_ReplaceAll.
camera.RegisterConfiguration(pylon.SoftwareTriggerConfiguration(), pylon.RegistrationMode_ReplaceAll,
                             pylon.Cleanup_Delete)

# For demonstration purposes only, add sample configuration event handlers to print out information
# about camera use and image grabbing.
camera.RegisterConfiguration(ConfigurationEventPrinter(), pylon.RegistrationMode_Append, pylon.Cleanup_Delete)
camera.RegisterImageEventHandler(ImageEventPrinter(), pylon.RegistrationMode_Append, pylon.Cleanup_Delete)

# Print the model name of the camera.
print("Using device ", camera.GetDeviceInfo().GetModelName())

# The parameter MaxNumBuffer can be used to control the count of buffers
# allocated for grabbing. The default value of this parameter is 10.
camera.MaxNumBuffer = 15

# Open the camera.
camera.Open()

###########################################################################
print("Grab using strategy GrabStrategy_LatestImageOnly:")

# The GrabStrategy_LatestImageOnly strategy is used. The images are processed
# in the order of their arrival but only the last received image
# is kept in the output queue.
# This strategy can be useful when the acquired images are only displayed on the screen.
# If the processor has been busy for a while and images could not be displayed automatically
# the latest image is displayed when processing time is available again.
camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

# Execute the software trigger, wait actively until the camera accepts the next frame trigger or until the timeout occurs.
for i in range(3):
    if camera.WaitForFrameTriggerReady(200, pylon.TimeoutHandling_ThrowException):
        camera.ExecuteSoftwareTrigger()

# Wait for all images.
time.sleep(0.2)

# Check whether the grab result is waiting.
if camera.GetGrabResultWaitObject().Wait(0):
    print("A grab result waits in the output queue.")

# Only the last received image is waiting in the internal output queue
# and is now retrieved.
# The grabbing continues in the background, e.g. when using hardware trigger mode.
buffersInQueue = 0

while True:
    grabResult = camera.RetrieveResult(0, pylon.TimeoutHandling_Return)
    if not grabResult.IsValid():
        break
    print("Skipped ", grabResult.GetNumberOfSkippedImages(), " images.")
    buffersInQueue += 1

print("Retrieved ", buffersInQueue, " grab result from output queue.")

# Stop the grabbing.
camera.StopGrabbing()

