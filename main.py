import os
import sys
import soundfile
from dateutil.parser import parse
import csv

import speaker_detector as sd
import subtitle_placement_optimizer as spo

# parameters
theta1 = 20
theta2 = 2.5
theta3 = 2
theta4 = 0.1
theta5 = 2

def main(sample):
    video_file_name = f"assets/{sample}/video.mp4"
    audio_file_name = f"assets/{sample}/audio.wav"
    subtitles_file_name = f"assets/{sample}/subtitles.srt"
    pre_subtitle_position_file_name = f"assets/{sample}/pre_subtitle_position.csv"
    output_file_name = f"assets/{sample}/result.mp4"
    output_wa_file_name = f"assets/{sample}/result_with_audio.mp4"

    audio, sampling_rate = soundfile.read(audio_file_name)
    subtitle_start_time, subtitle_end_time, subtitle = subtitle_parser(subtitles_file_name)
    pre_subtitle_position = read_position(pre_subtitle_position_file_name)

    speaker, faces = speaker_detection(video_file_name, audio, subtitle, subtitle_start_time, subtitle_end_time)
    subtitle_placement(speaker, faces, pre_subtitle_position, video_file_name, subtitle, audio_file_name, output_file_name)
    add_audio_onto_video(output_file_name, audio_file_name, output_wa_file_name)


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

def read_position(path):
    data = []
    with open(path, "r") as f:
        reader = csv.reader(f)
        for row in reader:
            return [int(row[0]), int(row[1])]

# 論文のアルゴリスム1部分
def speaker_detection(video_file_name, audio, subtitle, subtitle_start_time, subtitle_end_time):
    faces = sd.detect_faces(video_file_name)
    all_faces = faces
    msds = sd.calc_msds(video_file_name, faces)
    faces, msds = sd.filter_by_msd(faces, msds, theta1)
    if len(faces) >= 2:
        faces, msds = sd.filter_by_msd(faces, msds, max(msds)/theta2)
        if len(faces) >= 2:
            ccs = sd.calc_ccs(video_file_name, faces)
            faces = sd.filter_by_cc(faces, ccs, max(ccs)/theta3)
            if len(faces) >= 2:
                lcs = sd.calc_lcs(video_file_name, faces, subtitle, subtitle_start_time, subtitle_end_time)
                if max(lcs) - max(filter(lambda x: x != max(lcs), lcs)) > theta4:
                    return faces[lcs.index(max(lcs))]
                else:
                    avs = sd.calc_avs(video_file_name, audio, faces)
                    if max(avs) > theta5:
                        return faces[avs.index(max(avs))]
                    else:
                        return []

    if len(faces) == 1:
        return faces[0], all_faces
    else:
        return [], all_faces

# 論文のアルゴリスム2部分
def subtitle_placement(speaker, faces, pre_subtitle_position, video_file_name, subtitle, audio_file_name, output_file_name):
    candidate_positions = spo.calc_candidate_positions(speaker)
    energies = spo.calc_energy(candidate_positions, speaker, faces, pre_subtitle_position, video_file_name)
    opt_position = spo.min_energy(candidate_positions, energies)
    spo.save_video(video_file_name, subtitle, opt_position, audio_file_name, output_file_name)

def add_audio_onto_video(output_file_name, audio_file_name, output_wa_file_name):
    os.system(f"ffmpeg -i {output_file_name} -i {audio_file_name} {output_wa_file_name} -y")

if __name__ == "__main__":
    args = sys.argv
    main(args[1])