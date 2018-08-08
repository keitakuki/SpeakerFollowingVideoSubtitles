import cv2
import sys
import soundfile
from dateutil.parser import parse

import speaker_detector as sd
import subtitle_placement_optimizer as spo

# parameters
theta1 = 20
theta2 = 2.5
theta3 = 2
theta4 = 0.1
theta5 = 2

pre_subtitle_position = [150, 300]


def main(video_file_name, audio_file_name, subtitles_file_name):
    output_file_name = "assets/result.mp4"
    audio, sampling_rate = soundfile.read(audio_file_name)
    subtitle_start_time, subtitle_end_time, subtitle = subtitle_parser(subtitles_file_name)
    speaker, faces = speaker_detection(video_file_name, audio, subtitle, subtitle_start_time, subtitle_end_time)
    subtitle_placement(speaker, faces, pre_subtitle_position, video_file_name, subtitle, output_file_name)


# 字幕ファイルから時間と字幕を抜き出す関数
def subtitle_parser(subtitles_file_name):
    srt_string = open(subtitles_file_name).read()
    lines = srt_string.splitlines()
    subtitle = []
    preline_status = 0  # 0: blank, 1: number, 2:timestamp, 3:subtitle
    for line in lines:
        if line == "":
            preline_status = 0
            continue
        if preline_status == 0:
            preline_status = 1
        elif preline_status == 1:
            start_time = parse(line.split()[0])
            end_time = parse(line.split()[-1])
            preline_status = 2
        elif preline_status == 2 or preline_status == 3:
            subtitle.append(line)
            preline_status = 3
    return start_time, end_time, subtitle

# 論文のアルゴリスム1部分
def speaker_detection(video_file_name, audio, subtitle, subtitle_start_time, subtitle_end_time):
    faces = sd.detect_faces(video_file_name)
    all_faces = faces
    msds = sd.calc_msds(video_file_name, faces)
    faces, msds = sd.filter_by_msd(faces, msds, theta1)
    if len(faces) >= 2:
        faces, msds = sd.filter_by_msd(faces, msds, max(msds)/theta2)


    if len(faces) == 1:
        return faces[0], all_faces
    else:
        return [], all_faces

def subtitle_placement(speaker, faces, pre_subtitle_position, video_file_name, subtitle, output_file_name):
    candidate_positions = spo.calc_candidate_positions(speaker)
    energies = spo.calc_energy(candidate_positions, speaker, faces, pre_subtitle_position, video_file_name)
    opt_position = spo.min_energy(candidate_positions, energies)
    spo.save_video(video_file_name, subtitle, opt_position, output_file_name)

if __name__ == "__main__":
    args = sys.argv
    main(args[1], args[2], args[3])