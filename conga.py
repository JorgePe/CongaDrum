#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.tools import wait,  StopWatch
from pybricks.ev3devices import Motor, TouchSensor, InfraredSensor
from pybricks.parameters import Port, Stop, Button
from pybricks.nxtdevices import SoundSensor
from pybricks.media.ev3dev import Font
from random import randint
import os
from threading import Thread
import sys
	

ev3 = EV3Brick()
mA  = Motor(Port.A)             # Mute Conga
mB  = Motor(Port.B)             # Hi Conga
mD  = Motor(Port.D)             # Menu Dial
ts1 = TouchSensor(Port.S1)      # Drum
ts2 = TouchSensor(Port.S2)      # Drum
snd = SoundSensor(Port.S3)      # Hand Clap
ir  = InfraredSensor(Port.S4)   # Remote

DEBOUNCE = 275    # time between button presses or hand claps
SND_THRESHOLD = 45

# Notation used on metronome and beatbox beats
MARK_A = 'A'
MARK_B = 'B'
MARK_BEAT = '.'

big_font = Font(size=32, bold=True)
ev3.screen.set_font(big_font)

### control.limits() - Large
### (800, 1600, 100)
### control.pid() - Large
### (400, 1200, 5, 23, 5, 0)

#defaults:
mA.control.limits(800, 1600, 100)
mB.control.limits(800, 1600, 100)
#mA.control.pid(400, 1200, 5, 23, 5, 0)
#mB.control.pid(400, 1200, 5, 23, 5, 0)

# tweak PID for faster response
mA.control.pid(425, 320, 4, 23, 5, 0)
mB.control.pid(425, 320, 4, 23, 5, 0)

# metronome beats
metronome_1 = ['B', '.']
metronome_2 = ['B', '.', 'B', '.', 'B', '.', 'A', 'B', '.']
metronomes = [metronome_1, metronome_2]

# beatbox beats
beat1 = ['A', '.', 'B', '.', 'B', '.']
beat2 = ['B', '.', 'A', '.', 'A', '.']
beats = [beat1, beat2, []]  # last beat is for Learn Mode (editable)

MAX_BPM = 250
DIF_BPM = 30
MIN_BPM = 0 + DIF_BPM

wait(100)
# calibrate

mA.run_until_stalled(-100, then=Stop.COAST, duty_limit=20)
wait(100)
mA.reset_angle(0)

mB.run_until_stalled(-100, then=Stop.COAST, duty_limit=20)
wait(100)
mB.reset_angle(0)

REST_A = 17
REST_B = 22
TARGET_A = 27
TARGET_B = 34

mA.run_target(600, REST_A, then=Stop.HOLD, wait=True)
wait(200)
mA.stop()

mB.run_target(600, REST_B, then=Stop.HOLD, wait=True)
wait(200)
mB.stop()

mD.run_until_stalled(-100, then=Stop.COAST, duty_limit=25)
wait(100)
mD.stop()
mD.reset_angle(0)
wait(100)

ACTIVE = 125  # time each  motor will be active

# Modes:
M_IPMIDI = 1
M_USBMIDI = 2
M_METRONOME = 3
M_BEATBOX = 4
M_LEARN = 5
M_UNUSED = 6

MODE1_MIN = -30  # min is 0, this is to adjust middle
MODE1_MAX = 30
MODE2_MIN = 31
MODE2_MAX = 79
MODE3_MIN = 80
MODE3_MAX = 119
MODE4_MIN = 120
MODE4_MAX = 154
MODE5_MIN = 155
MODE5_MAX = 204
MODE6_MIN = 205
MODE6_MAX = 260  # max is 240, this is to oadjust middle

MODE_SPEAK=["",
    " I.P. Midi",
    "U.S.B. Midi",
    "Metronome",
    "Beatbox",
    "Learn",
    "Not used"]

MIDI_FIFO = '/dev/shm/midipipe'

def get_mode():
    mode = 0
    while True:
        angle = mD.angle()
        if MODE1_MIN <= angle <= MODE1_MAX:
            mode = M_IPMIDI
        elif MODE2_MIN <= angle <= MODE2_MAX:
            mode = M_USBMIDI
        elif MODE3_MIN <= angle <= MODE3_MAX:
            mode = M_METRONOME
        elif MODE4_MIN <= angle <= MODE4_MAX:
            mode = M_BEATBOX
        elif MODE5_MIN <= angle <= MODE5_MAX:
            mode = M_LEARN
        elif MODE6_MIN <= angle <= MODE6_MAX:
            mode = M_UNUSED
        else:
            mode = 0

        return mode


def start_ipmidi():
    # this can be done once at startup
    # even if IP MIDI never being used after
    
    # check if multimidicast is running and start it if not
    if os.popen('pgrep multimidicast').read().strip() == '':
        os.system('./multimidicast -q &')
        print('multimidicast started')
    else:
        print('multidicast was running')

    wait(500)


def start_midipipe():
    # this can be done once at startup
    
    # check if midipipe was created
    if os.popen('ls ' + MIDI_FIFO).read().strip() == MIDI_FIFO:
        print(MIDI_FIFO + ' existed')
    else:
        os.system('mkfifo ' + MIDI_FIFO)
        print(MIDI_FIFO + ' created')



def select_midi(mode):
    # this needs to be done each time we change MIDI mode
    
    global MIDI_PORT
    global MIDI_CHANNEL
    global MUTE_CONGA
    global HIGH_CONGA

    # define MIDI_PORT, MIDI_CHANNEL and notes/instruments
    if mode == 'IP' :
        MIDI_PORT = '128:0'
        MIDI_CHANNEL = '9'
        MUTE_CONGA = '62'
        HIGH_CONGA = '63'
    elif mode == 'USB' :
        MIDI_PORT = '20:0'
        MIDI_CHANNEL = '9'
        MUTE_CONGA = '62'
        HIGH_CONGA = '63'
    elif mode == 'PLAYTRON' :
        MIDI_PORT = '20:0'
        MIDI_CHANNEL = '0'
        MUTE_CONGA = '43'
        HIGH_CONGA = '46'

    # check if aseqdump is running and start it if not or restart if it is
    if os.popen('pgrep aseqdump').read().strip() == '':
        os.system('aseqdump -p ' + MIDI_PORT + ' > ' + MIDI_FIFO + ' &')
        print('aseqdump started')
    else:
        os.system('pkill aseqdump')
        wait(50)
        os.system('aseqdump -p ' + MIDI_PORT + ' > ' + MIDI_FIFO + ' &')
        print('aseqdump was running, restarted')
    wait(250)


def midi():
    # this only reads from pipe, does not depend on
    # IP MIDI or USB MIDI being already defined
    # as long as it is paused when no MIDI is being used
    
    global activeA
    global activeB
    global MIDI_CHANNEL
    global MUTE_CONGA
    global HIGH_CONGA
    global pauseMIDI

    pipe = open(MIDI_FIFO, 'r')
    while True:
        if pauseMIDI == False :
            line = pipe.readline()
            # should check for correct line input
            
#            print(line)
#128:0       Note on                 9, note 63, velocity 86
# 20:0       Note on                 0, note 46, velocity 127
#            print(line[32+INDEX], line[13+INDEX:15+INDEX], line[40+INDEX:42+INDEX])

            if len(line) > 40 :
                if line[32] == MIDI_CHANNEL:
                    cmd = line[13:16]
                    if cmd == 'on ':
                        note = line[40:42]
                        if note == MUTE_CONGA:
                            activeA = True
                        elif note == HIGH_CONGA:
                            activeB = True
                    elif cmd == 'off':
                        note = line[40:42]
                        if note == MUTE_CONGA:
                            activeA = False
                        elif note == HIGH_CONGA:
                            activeB = False


def playA():
    global activeA
    while True:
        if activeA:
            activeA = False
            mA.track_target(TARGET_A)
            wait(ACTIVE)
            mA.track_target(REST_A)
            wait(ACTIVE)
        mA.track_target(REST_A)


def playB():
    global activeB
    while True:
        if activeB:
            activeB = False
            mB.track_target(TARGET_B)
            wait(ACTIVE)
            mB.track_target(REST_B)
            wait(ACTIVE)
        mB.track_target(REST_B)


def metronome():
    global pauseMETRONOME
    global activeA
    global activeB
    global bpm
    global beatActive
    global metronomes
    global metro

    while True:
        if pauseMETRONOME == False and beatActive == True :
            for m in metronomes[metro] :
                # should check for flag inside the beat loop to stop faster
                if m == MARK_A :
                    activeA = True
                if m == MARK_B :
                    activeB = True
                if m == MARK_BEAT :            
                    wait(60000/bpm)    # T=1/f = 1 minute / beats per minute

def beatbox():
    global pauseBEATBOX
    global bpm
    global activeA
    global activeB
    global beatActive
    global beat
    global beats

    while True:
        if pauseBEATBOX == False and beatActive == True :
            for b in beats[beat] :
                if beatActive :
                # should check for flag inside the beat loop to stop faster
                    if b == MARK_A :
                        activeA = True
                    if b == MARK_B :
                        activeB = True
                    if b == MARK_BEAT :
                        wait(60000/bpm)    # T=1/f = 1 minute / beats per minute


def controls():
    global bpm
    global current_mode
    global activeA
    global activeB
    global beat
    global beats
    global metronomes
    global metro
    global beatActive

    while True:
        ts1_state = ts1.pressed()
        ts2_state = ts2.pressed()
        snd_state = snd.intensity(audible_only = True) > SND_THRESHOLD
        ir_state  = ir.buttons(1)
        btn_state = ev3.buttons.pressed()

        if ts1_state :
            if current_mode == M_LEARN :
                activeA = True
                beats[beat].append(MARK_A)

        if ts2_state :
            if current_mode == M_LEARN :
                activeB = True
                beats[beat].append(MARK_B)

        if snd_state :
            if current_mode == M_LEARN :
                activeB = True
                beats[beat].append(MARK_B)
            elif current_mode == M_METRONOME or \
                    current_mode == M_BEATBOX :
                beatActive = not beatActive


        if ir_state :
            if ir_state[0] == Button.LEFT_UP :
                if current_mode == M_METRONOME or \
                        current_mode == M_BEATBOX :
                    if bpm < MAX_BPM :
                        bpm = bpm + DIF_BPM
                    ev3.screen.clear()
                    ev3.screen.draw_text(20, 50, '{:>3} BPM'.format(bpm))                    
            elif ir_state[0] == Button.LEFT_DOWN :
                if current_mode == M_METRONOME or \
                        current_mode == M_BEATBOX :
                    if bpm > MIN_BPM :
                        bpm = bpm - DIF_BPM
                    ev3.screen.clear()
                    ev3.screen.draw_text(20, 50, '{:>3} BPM'.format(bpm))
            elif ir_state[0] == Button.RIGHT_UP :
                if current_mode == M_METRONOME :
                    if metro < 1 :
                        metro = metro + 1
                    ev3.speaker.say('Beat ' + str(metro + 1) )
                elif current_mode == M_BEATBOX :
                    if beat < 2 :
                        beat = beat + 1
                    if beat < 2 :
                        ev3.speaker.say('Beat ' + str(beat + 1) )
                    else :
                        ev3.speaker.say('Learn Beat')
            elif ir_state[0] == Button.RIGHT_DOWN :
                if current_mode == M_METRONOME :
                    if metro > 0 :
                        metro = metro - 1
                    ev3.speaker.say('Beat ' + str(metro + 1 ) )
                elif current_mode == M_BEATBOX :
                    if beat > 0 :
                        beat = beat - 1
                    if beat < 2 : 
                        ev3.speaker.say('Beat ' + str(beat + 1) )
                    else :
                        ev3.speak.say('Learn Beat')

        if btn_state :
            if btn_state[0] == Button.CENTER :
                if current_mode == M_METRONOME or \
                        current_mode == M_BEATBOX :
                    beatActive = not beatActive            
        
        if ts1_state or ts2_state or snd_state or ir_state or btn_state:
            wait(DEBOUNCE)   
            if ts1_state or ts2_state or snd_state:
                if current_mode == M_LEARN :
                    beats[beat].append(MARK_BEAT)



def main_thread():
    global activeA
    global activeB
#    global MIDI_PORT
#    global MIDI_CHANNEL
    global pauseMIDI
    global pauseMETRONOME
    global pauseBEATBOX
    global bpm
    global current_mode
    global beats
    global beat
    global beatActive
    global metronomes
    global metro

    # trabalhar melhor a inicialização
    
    # threads:
    t_controls = Thread(target = controls)
    t_midi = Thread(target = midi)
    t_playA = Thread(target = playA)
    t_playB = Thread(target = playB)
    t_metronome = Thread(target = metronome)
    t_beatbox = Thread(target = beatbox)
    
    t_controls.start()
    t_playA.start()
    t_playB.start()  
    t_metronome.start()
    t_beatbox.start()
    t_midi.start()

    first_run = True
    while True:
        mode = get_mode()
        if mode != current_mode:
            # wait for user option to settle
            wait(750)
            mode = get_mode()

        if mode != current_mode or first_run == True :

            if mode == 0:
                ev3.speaker.say('Invalid mode')
                wait(100)
            else:
                # actions to be done when leaving a mode
                activeA = False
                activeB = False
                if current_mode == M_IPMIDI :
                    pauseMIDI = True
                elif current_mode == M_USBMIDI :
                    pauseMIDI = True
                elif current_mode == M_METRONOME :
                    pauseMETRONOME = True
                elif current_mode == M_BEATBOX :
                    pauseBEATBOX = True
                elif current_mode == M_LEARN :
                    pass

#                wait(250)

                if first_run :
                    ev3.speaker.say('Current mode is ' + MODE_SPEAK[current_mode])
                    first_run = False
                else :
                    ev3.speaker.say(MODE_SPEAK[mode])
                    current_mode = mode

                if current_mode == M_IPMIDI :                             
                    pauseMIDI = True
                    select_midi('IP')
                    pauseMIDI = False
                elif current_mode == M_USBMIDI :
                    pauseMIDI = True
                    select_midi('USB')
                    pauseMIDI = False
                elif current_mode == M_METRONOME :
                    pauseMETRONOME = False
                    ev3.speaker.say('Beat ' + str(metro + 1) )
                    ev3.screen.clear()
                    ev3.screen.draw_text(20, 50, '{:>3} BPM'.format(bpm))
                elif current_mode == M_BEATBOX :
                    pauseBEATBOX = False
                    if beat < 2 :
                        ev3.speaker.say('Beat ' + str(beat + 1) )
                    else:
                        ev3.speaker.say('Learn Beat')
                    ev3.screen.clear()
                    ev3.screen.draw_text(20, 50, '{:>3} BPM'.format(bpm))
                elif current_mode == M_LEARN :
                    # clear Learn Beat
                    beat = 2
                    beats[beat].clear()
                elif current_mode == M_UNUSED :
                   # not used yet
                    pass
        wait(100)

# Prepare
activeA = False
activeB = False
pauseMIDI = True
pauseMETRONOME = True
pauseBEATBOX = True
bpm = 90
#current_mode = M_IPMIDI
#current_mode = M_USBMIDI
#current_mode = M_METRONOME
#current_mode = M_BEATBOX
#current_mode = M_LEARN
current_mode = M_UNUSED

metro = 0 # default metronome
beat = 0 # default beat
beatActive = False
ev3.screen.clear()

# position in current mode
if current_mode == M_IPMIDI :
    pos = MODE1_MIN + (MODE1_MAX - MODE1_MIN)/2
elif current_mode == M_USBMIDI :
    pos = MODE2_MIN + (MODE2_MAX - MODE2_MIN)/2
elif current_mode == M_METRONOME :
    pos = MODE3_MIN + (MODE3_MAX - MODE3_MIN)/2
elif current_mode == M_BEATBOX :
    pos = MODE4_MIN + (MODE4_MAX - MODE4_MIN)/2
elif current_mode == M_LEARN :
    pos = MODE5_MIN + (MODE5_MAX - MODE5_MIN)/2
elif current_mode == M_UNUSED :
    pos = MODE6_MIN + (MODE6_MAX - MODE6_MIN)/2
mD.run_target(180, pos, then=Stop.COAST, wait=True)

start_ipmidi()
start_midipipe()

# Run
main_thread()
