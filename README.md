# CongaDrum

This is the companion code for a LEGO REMIX project using parts of the '42112 - Concrete Mixer Truck'
and the '31313 - MINDSTORMS EV3'.

The idea is using the main element as a different kind of drum - a musical instrument drum.

Using a parachute tissue from a LEGO City set it is possible to create a playable drum. Using the EV3
programmable brick (or 'hub') and 2 motors it is possible to create a simple autonomous instrument able
to play two slightly different sounds.

With some extra MINDSTORMS components we get a multifunction instrument. A dial switch allows the user
choose 5 modes:
- Metronome
- Beatbox
- Learn mode
- USB MIDI instrument
- IP MIDI instrument

Using the IR Remote some extra options are available:
- in Metronome or Beatbox modes we can change the 'tempo' (from 30 to 240 BPM or beat per minute)
- in Metronome mode we can choose the pattern (2 are available)
- in Beatbox mode we can choose the beat (2 are available and a third one is possible to define 
in Learn mode)

We can also clap our hands to start or stop the Metronome or the Beatbox.

As a MIDI instrument we can use standard MIDI controllers to control the Conga Drum. It will react
to Mute Conga and Hi Conga events on the standard MIDI Percussion Channel.

IP MIDI (also known as Multicast MIDI) is used by some MIDI software tools so we can use the 
Conga Drum as a wireless MIDI instrument though the Wi-Fi USB dongle. It requires a good Wi-Fi
connection with low latency for fast rhytms so USB MIDI will be a better option if using long and
messy cables aren't a problem.

USB MIDI should work out of the box with most modern USB MIDI controllers that stablish a MIDI
device at port 20 (but I've only tested an Android USB MIDI, 2 USB MIDI keybords and a USB MIDI
adapter).
