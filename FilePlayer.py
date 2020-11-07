#! /usr/bin/env python3
from threading import Thread, Semaphore, Lock
import cv2, time

class produceConsumeQueue():
    def __init__(self, queueCapacity):
        self.queue = []
        self.fullCount = Semaphore(0)
        self.emptyCount = Semaphore(24)
        self.lock = Lock()
        self.queueCapacity = queueCapacity
    def putFrame(self, frame):
        self.emptyCount.acquire()
        self.lock.acquire()
        self.queue.append(frame)
        self.lock.release()
        self.fullCount.release()
        return
    def getFrame(self):
        self.fullCount.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.emptyCount.release()
        return frame
    
class ExtractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture('clip.mp4')
        self.totalFrames = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.count = 0

    def run(self):
        global frameQueue
        success, image = self.videoCapture.read()

        while True:
            if success and len(frameQueue.queue) <= frameQueue.queueCapacity:
                frameQueue.putFrame(image)
                success,image = self.videoCapture.read()
                print(f'Reading frame {self.count}')
                self.count += 1

            if self.count == self.totalFrames:
                frameQueue.putFrame(-1)
                break
        return
class ConverttoGrayScale(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.count = 0

    def run(self):
        global frameQueue
        global grayScaleQueue

        while True:
            if frameQueue.queue and len(grayScaleQueue.queue) <= grayScaleQueue.queueCapacity:
                frame = frameQueue.getFrame()

                if type(frame) == int and frame == -1:
                    grayScaleQueue.insertFrame(-1)
                    break
                print(f'Converting Frame {self.count}')
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                grayScaleQueue.putFrame(grayscaleFrame)
                self.count += 1
        return

class DisplayFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0

    def run(self):
        global grayScaleQueue

        while True:
            if grayScaleQueue.queue:
                frame = grayScaleQueue.getFrame()

                if type(frame) == int and frame == -1:
                    break
                
                print(f'Displaying Frame{self.count}')
                cv2.imshow('Video', frame)
                self.count += 1

                if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                    break

        cv2.destroyAllWindows()
        return

frameQueue = produceConsumeQueue(9)
grayScaleQueue = produceConsumeQueue(9)

extractFrames = ExtractFrames()
extractFrames.start()
convertFrames = ConverttoGrayScale()
convertFrames.start()
displayFrames = DisplayFrames()
displayFrames.start()
