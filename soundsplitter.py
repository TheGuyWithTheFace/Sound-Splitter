#!/usr/bin/python3

#
#   soundsplitter: Reads a given audio file and saves individual segments,
#           split by gaps of silence in the input file.
#


import sys
import os
import wave
import time

#
# Magic constants
# TODO: Read these from a config file instead?
#
# NOTE: These are currently not even used, oh well.
SILENCE_LENGTH = .5 # Seconds of silence required to trigger a split
PADDING = .2       # Seconds of silence to add to the beginning/end of new files

def main():

    # Open a .wav file to inspect
    if(len(sys.argv) < 2):
        filename = input("Enter a .wav file name to open: ")
    else:
        filename = sys.argv[1]

    # Establish output directory based on name of input file
    folder_name = filename.split('.')[0]
    os.makedirs(folder_name)

    # Get relevant info about the given file
    input_file = wave.open(filename, "rb")
    num_channels = input_file.getnchannels()
    sample_width = input_file.getsampwidth()
    framerate = input_file.getframerate()

    # Scan file for whitespace
    print(input_file.getnframes())
    print(SILENCE_LENGTH * framerate)
    nextBlankIndex = get_whitespace(input_file, sample_width, SILENCE_LENGTH * framerate)

    print(nextBlankIndex)
    print(nextBlankIndex / framerate)

def get_whitespace(audio, framewidth, frames_of_silence):
    num_frames = audio.getnframes()
    silent_frame_count = 0 # Measures # of frames of silence in a row


    # As long as there's still audio remaining
    while(audio.tell() < num_frames):
        frame = audio.readframes(1)
        print(frame[0])
        # Check for silent place
        if( (frame[0] == 0) or (frame[1] == 0) ):
            silent_frame_count += 1
        else:
            pass
            #silent_frame_count = 0

        if(silent_frame_count == frames_of_silence):
            print("SUCCESS!")
            # For now, just split the silence. TODO use global padding constant
            return audio.tell() - (frames_of_silence / 2)

    print("silence: ",silent_frame_count)
    return -1

main()
