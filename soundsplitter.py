#!/usr/bin/python3

#
#   soundsplitter: Reads a given audio file and saves individual segments,
#           split by gaps of silence in the input file.
#

import sys
import os
import wave
import time
import struct
import subprocess

#
# Magic constants
# TODO: Read these from a config file instead?
#
SILENCE_THRESHOLD = 40
SILENCE_LENGTH = .30 # Minimum seconds of total silence before splitting

# NOTE: this is currently not even used. oh well.
PADDING = .2       # Seconds of silence to add to the beginning/end of new files
MAX_NUM_STRIKES = 3 # Just an idea, not implemented yet either

def main():

    # Open a .wav file to inspect
    if(len(sys.argv) < 2):
        filename = input("Enter a .wav file name to open: ")
    else:
        filename = sys.argv[1]

    if(len(sys.argv) >= 3):
        output_mp3 = sys.argv[2]
    else:
        output_mp3 = False

    # Establish output directory based on name of input file
    folder_name = filename.split('.')[0]
    os.makedirs(folder_name)

    # Get relevant info about the given file
    input_file = wave.open(filename, "rb")
    num_channels = input_file.getnchannels()
    sample_width = input_file.getsampwidth()
    framerate = input_file.getframerate()

    # Scan file for whitespace
    print("Input has " + str(input_file.getnframes()) + " frames.")
    print("Input has " + str(input_file.getnchannels()) + " channels.")
    print("Input framerate: " + str(framerate))
    print("Whitespace Cutoff Length (in seconds): "
            + str(SILENCE_LENGTH))
    print("In frames: " + str(SILENCE_LENGTH * framerate))

    num_silent_frames = SILENCE_LENGTH * framerate
    audio_remaining = True
    previous_frame = 0
    num_output_files = 0
    while(audio_remaining):
        # Find the next split point
        num_frames_to_copy = get_whitespace(input_file,
                sample_width, num_silent_frames)

        # If no split point fount, we're done.
        if(num_frames_to_copy == -1):
            audio_remaining = False
            break

        # Copy between split points to a new file.
        filename = folder_name + "/" + folder_name + "_" + str(num_output_files)
        filename += ".wav"

        print(filename)
        output_file = create_output_file(filename, input_file)
        copy_audio(input_file, output_file, previous_frame, num_frames_to_copy)
        output_file.close()

        # Convert to mp3 if user asked for it
        if(output_mp3):
            cmd = 'lame --preset insane %s' % filename
            subprocess.call(cmd, shell=True)

        previous_frame += num_frames_to_copy
        num_output_files += 1


# Finds a "split point" in the given audio after a given number of silent
# frames, returns the number of frames between the original location of audio
# and the newly-found split point.
def get_whitespace(audio, framewidth, frames_of_silence):
    num_frames = audio.getnframes()
    silent_frame_count = 0 # Measures # of frames of silence in a row
    num_frames_examined = 0

    # As long as there's still audio remaining
    while(audio.tell() < num_frames):
        frame = audio.readframes(1)
        num_frames_examined += 1

        # Check for silent place
        if(is_silent(frame)):
            silent_frame_count += 1
        else:
            silent_frame_count = 0

        if(silent_frame_count >= frames_of_silence):
            # Proceed to end of silence
            while(is_silent(audio.readframes(1))):
                num_frames_examined += 1
            return num_frames_examined

    print("silence: ",silent_frame_count)
    return -1

def is_silent(frame):
    if(frame == b''):
        return False
    data = struct.unpack("<h", frame)
    volume = data[0] # Would probably have to do something more for stereo
    return (volume <= SILENCE_THRESHOLD and volume >= SILENCE_THRESHOLD * -1)

# copies num_frames from input to output, starting with start_frame
def copy_audio(input_file, output_file, start_frame, num_frames):

    output_file.setnframes(num_frames)
    input_file.setpos(start_frame)
    output_file.writeframes(input_file.readframes(num_frames))

# creates and returns a wave write object with similar settings to input file
def create_output_file(filename, input_file):
    output_file = wave.open(filename, "w")
    output_file.setnchannels(1);
    output_file.setsampwidth(input_file.getsampwidth());
    output_file.setframerate(input_file.getframerate());

    return output_file


main()
