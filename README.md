# CongaDrum

This is the companion code for a LEGO REMIX project using parts of the '42112 - Concrete Mixer Truck'
and the '31313 - MINDSTORMS EV3'.

The idea is using the main element as a different kind of drum - a musical instrument drum.

With a parachute tissue from a LEGO City set it is possible to create a playable drum (the fabric needs
to be stretched a bit so non-conventional ways of using the parachute were applied).

Using the EV3 programmable brick (or 'hub') and 2 motors it is possible to create a simple autonomous
instrument able to play two slightly different sounds.

With some extra MINDSTORMS components we get a multifunction instrument. A dial switch allows the user
to choose 5 modes ( a sixth mode, 'Rest', is used as a placeholder at start but can be easily assigned
another purpose):
- Metronome
- Beatbox
- Learn mode
- USB MIDI instrument
- IP MIDI instrument

The IR Remote offers some extra options:
- in Metronome or Beatbox modes we can change the 'tempo' (from 30 to 240 BPM or beat per minute)
- in Metronome mode we can choose the pattern (2 are available)
- in Beatbox mode we can choose the beat (2 are available and a third one is possible to define 
in Learn mode)

We can also clap our hands to start or stop the Metronome or the Beatbox. This makes use of a NXT
sound sensor.

As a MIDI instrument we can use standard MIDI controllers to control the Conga Drum. It will react
to Mute Conga and Hi Conga events on the standard MIDI Percussion Channel.

IP MIDI (also known as Multicast MIDI) is used by some MIDI software tools like 'TouchDAW' and
'qmidinet' so we can use them with the Conga Drum as a wireless MIDI instrument (trough a Wi-Fi
USB dongle). It requires a good Wi-Fi connection with low latency for fast rhythms so USB MIDI
will be a better option if using long and messy cables aren't a problem.
It requires an extra tool, 'multimidicast'.

USB MIDI should work out of the box with most modern USB MIDI controllers that stablish a MIDI
device at port 20 (I've only tested an Android USB MIDI, 2 USB MIDI keybords, a USB MIDI
adapter and a PLAYTRON controller). It requires the MIDI controller to be attached to the EV3
USB 1.1 port so if using Wi-Fi a small USB hub is also needed.

The code is written in micropython for MINDSTORMS EV3. It uses the great 'pybricks' library to
glue all the different LEGO actuators and sensors and makes some system calls to the operating
system (ev3dev, a great version of Debian Linux for the MINDSTORMS EV3) to interact with the
Linux ALSA subsystem for the MIDI operations:
- a FIFO is created to be used as a pipe between the micropython script and the USB devices
- 'multimidicast' is started in background (this assignes 128:0 to Multicast/IP MIDI as long
as there is already a network interface present)
- each time a USB mode (IP or USB) is selected a connection between the FIFO and the MIDI device
(20:0 for USB, 128:0 for IP) is recreated through 'aseqdump' (an ALSA tool that captures 
the data stream from a MIDI device)
