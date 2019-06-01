##############
#MIT License
#
#Copyright (c) 2018 vizeet srivastava
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:
#
#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.
#
#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.
##############

import random
import time
import hashlib
import binascii
import pygame
import pygame.camera
#import sounddevice as sd
import queue
import time

q = queue.Queue()

#def getRandomNumber():
#        return random.SystemRandomo().getrandbits(256)

def getRawCameraOutput():
        pygame.init()
        pygame.camera.init()
        camera_list = pygame.camera.list_cameras()
        if len(camera_list) == 0:
                pygame.camera.quit()
                return None
        cam = pygame.camera.Camera(camera_list[0])
        cam.start()
        raw = cam.get_raw()
        cam.stop()
        pygame.camera.quit()
        return raw

def callback(indata, frames, time, status):
        if status:
                print(status)
        q.put(indata.copy())

#def getRawMicOutput():
#        duration = 1  # seconds
#        out = b''
#        rec_start = int(time.time())
#
#        with sd.InputStream(samplerate=48000, channels=2, callback=callback):
#                rec_time = int(time.time()) - rec_start
#                while rec_time <= duration:
#                        rec_time = int(time.time()) - rec_start
#                out = q.get()
#
#        print('outdata = %s' % out)
#        return out

def getRandomNumberBits(bit_count: int):
        h = hashlib.sha256()

        # update with raw camera output
        raw_photo = getRawCameraOutput()
        if raw_photo != None:
                h.update(raw_photo)

        # update with raw mic output
#        raw_sound = getRawMicOutput()
#        print('raw sound = %s' % bytes.decode(binascii.hexlify(raw_sound)))
#        h.update(raw_sound)

        # update with system random number
        sys_rand = '%x' % random.SystemRandom().randrange(0, 1 << 32)
        if sys_rand.__len__() % 2 == 1:
                sys_rand = "0{}".format(sys_rand)
#        print('sys_rand = %s' % sys_rand)
        sys_rand_b = binascii.unhexlify(sys_rand)
        h.update(sys_rand_b)

        h_b = h.digest()
        byte_count = bit_count // 8
        rand_num_b = h_b[0:byte_count]
        return rand_num_b

if __name__ == '__main__':
        print('random number = %s' % bytes.decode(binascii.hexlify(getRandomNumberBits(256))))

