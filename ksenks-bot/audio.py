import pickle
import struct
from io import BytesIO
from os.path import isfile

import numpy as np
from scipy import signal
from sklearn import svm

import audioread


def get_frames_from_flv_or_mp3(chunk, tail=b''):
    def unpack_uint24_be(x):
        if len(x) != 3:
            return 0
        return 2 ** 16 * x[0] + 2 ** 8 * x[1] + x[2]

    mp3_frames = []
    chunk = tail + chunk

    # mp3 frame start marker (first 11 bit setted to 1)
    if chunk[0] == 0xff and chunk[1] >= 0xe0:
        current_frame_offset = 0
        while current_frame_offset != -1 and len(chunk) - current_frame_offset > 10:
            next_frame_offset = chunk.find(chunk[current_frame_offset: current_frame_offset + 2],
                                           current_frame_offset + 2)
            if next_frame_offset == -1:
                break
            frame = chunk[current_frame_offset: next_frame_offset]
            mp3_frames.append(frame)
            current_frame_offset = next_frame_offset
        tail = chunk[current_frame_offset:]
        return mp3_frames, tail

    # trying detect flv-container
    signature = struct.unpack('3s', chunk[0:3])[0]
    # skip flv header
    if signature == b'FLV':
        start_pos = 9
    else:
        start_pos = 0
    while len(chunk) - start_pos > 15:
        packet_type = chunk[start_pos + 4]
        payload_size = unpack_uint24_be(chunk[start_pos + 5: start_pos + 8])
        if len(chunk) <= start_pos + 15 + payload_size:
            break
        if packet_type == 8:
            frame = chunk[start_pos + 16: start_pos + 15 + payload_size]
            mp3_frames.append(frame)
        start_pos = start_pos + 15 + payload_size
    tail = chunk[start_pos:]
    return mp3_frames, tail


def get_pcm_from_frames(all_frames):
    input_data = BytesIO()
    for frame in all_frames:
        input_data.write(frame)
    input_data.seek(0)
    try:
        f_convert = audioread.decode(input_data, ffmpeg_args='-ac 1')
    except:
        return None
    full_pcm = b''
    for pcm in f_convert:
        full_pcm += pcm
    f_convert.close()
    input_data.close()
    return full_pcm


def probe_ksenks_on_pcm(pcm, svm_model):
    def build_svm():
        svm_filename = 'svm_model.pickle'
        np_data_filenames = ['svm_x.npy', 'svm_y.npy']
        if isfile(svm_filename):
            f_svm = open(svm_filename, 'rb')
            trained_svm = pickle.load(f_svm)
            f_svm.close()
        elif isfile(np_data_filenames[0]) and isfile(np_data_filenames[1]):
            x_array = np.load(np_data_filenames[0])
            y_array = np.load(np_data_filenames[1])
            trained_svm = svm.SVC(class_weight='balanced', probability=True)
            trained_svm.fit(x_array, y_array)
            f_svm = open(svm_filename, 'wb')
            pickle.dump(trained_svm, f_svm)
            f_svm.close()
        else:
            return None
        return trained_svm

    def gen_featutes_from_pcm(pcm_data):
        pcm_array = np.frombuffer(pcm_data, dtype='<i2')
        freqs, _, pxx = signal.spectrogram(pcm_array, fs=44100, nfft=256, window=signal.get_window('hann', 256),
                                           noverlap=128)
        avg_freqs_values = np.zeros(len(freqs))
        min_freqs_values = np.zeros(len(freqs))
        max_freqs_values = np.zeros(len(freqs))
        # loop for each freq (in pxx[i] stored freq's values for each timepoint for freq #i)
        for i, freq in enumerate(pxx):
            avg_freqs_values[i] = np.log10(np.sum(freq) / len(freq)) / np.log10(2 ** 16)
            if np.max(freq):
                max_freqs_values[i] = np.log10(np.max(freq)) / np.log10(2 ** 16)  # scaled = [0,1]
            if np.min(freq):
                min_freqs_values[i] = np.log10(np.min(freq))
            else:
                min_freqs_values[i] = 0
        calculated_features = np.concatenate((avg_freqs_values, min_freqs_values, max_freqs_values))
        return calculated_features

    if svm_model is None:
        svm_model = build_svm()
    if not svm_model:
        return None

    features = gen_featutes_from_pcm(pcm)
    probability = svm_model.predict_proba([features])[0][1]
    return probability, svm_model
