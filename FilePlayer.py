#! /usr/bin/env python3
from threading import Thread, Semaphore
import cv2, time

semaphore = Semaphore(2)
queue1 = []
queue2 = []

class ExtractFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.videoCapture = cv2.VideoCapture('clip.mp4')
        self.totalFrames = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))
        self.queueCapacity = 50
        self.count = 0

    def run(self):
        global queue1
        global semaphore
        success, image = self.videoCapture.read()

        while True:
            if success and len(queue1) <= self.queueCapacity:
                semaphore.acquire()
                queue1.append(image)
                semaphore.release()

                success,image = self.videoCapture.read()
                print(f'Reading frame {self.count}')
                self.count += 1

            if self.count == self.totalFrames:
                semaphore.acquire()
                queue1.append(-1)
                semaphore.release()
                break
        return
class ConverttoGrayScale(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.queueCapacity = 50
        self.count = 0

    def run(self):
        global queue1
        global queue2
        global semaphore

        while True:
            if queue1 and len(queue2) <= self.queueCapacity:
                semaphore.acquire()
                frame = queue1.pop(0)
                semaphore.release()

                if type(frame) == int and frame == -1:
                    semaphore.acquire()
                    queue2.append(-1)
                    semaphore.release()
                    break
                print(f'Converting Frame {self.count}')
                grayscaleFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                semaphore.acquire()
                queue2.append(grayscaleFrame)
                semaphore.release()
                self.count += 1
        return

class DisplayFrames(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.delay = 42
        self.count = 0

    def run(self):
        global queue2
        global semaphore

        while True:
            if queue2:
                semaphore.acquire()
                frame = queue2.pop(0)
                semaphore.release()

                if type(frame) == int and frame == -1:
                    break
                print(f'Displaying Frame{self.count}')
                cv2.imshow('Video', frame)
                self.count += 1

                if cv2.waitKey(self.delay) and 0xFF == ord('q'):
                    break

        cv2.destroyAllWindows()
        return

extractFrames = ExtractFrames()
extractFrames.start()
convertFrames = ConverttoGrayScale()
convertFrames.start()
displayFrames = DisplayFrames()
displayFrames.start()
