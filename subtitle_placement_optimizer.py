import cv2

def calc_candidate_positions(speaker):
    x, y, w, h = speaker
    candidate_positions = [
        [x, y],
        [x, y + 2 / h],
        [x, y + h],
        [x + w / 2, y],
        [x + w / 2, y + h],
        [x + w, y],
        [x + w, y + 2 / h],
        [x + w, y + h]
    ]
    candidate_positions = [[int(x[0]), int(x[1])] for x in candidate_positions]
    return candidate_positions


def calc_energy(candidate_positions, speaker, faces, pre_subtitle_position, video_file_name):
    display_size = get_display_size(video_file_name)
    e = []
    for p in candidate_positions:
        e.append(e_local(p, speaker, faces) + e_global(p, pre_subtitle_position) - e_layout(p, display_size))
    return e


def min_energy(candidate_positions, energies):
    return candidate_positions[energies.index(min(energies))]


def e_local(p, speaker, faces):
    speaker_p = center_position_of(speaker)
    sigma = 0
    for face in faces:
        non_speaker_p = center_position_of(face)
        if non_speaker_p != speaker_p:
            sigma += dist(p, non_speaker_p)
    return dist(p, speaker_p) - sigma


def e_global(p, pre_subtitle_position):
    return dist(p, pre_subtitle_position)


def e_layout(p, display_size):
    width, height = display_size
    d = []
    d.append(dist(p, [p[0], 0]))
    d.append(dist(p, [p[0], height]))
    d.append(dist(p, [0, p[1]]))
    d.append(dist(p, [width, p[1]]))
    return min(d)


def dist(p, q):
    return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** (1 / 2)


def center_position_of(face):
    x, y, w, h = face
    return x + w / 2, y + h / 2


def get_display_size(video_file_name):
    video = cv2.VideoCapture(video_file_name)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    return width, height


def save_video(video_file_name, subtitle, position, audio_file_name, output_file_name):
    cap = cv2.VideoCapture(video_file_name)
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    fourcc = cv2.VideoWriter_fourcc(*'H264')
    vw = cv2.VideoWriter(output_file_name, fourcc, fps, (width, height))

    print('Making a video...')
    while(cap.isOpened()):
        isRead, img = cap.read()
        if isRead:
            vw.write(overlay_subtitle(img, subtitle, position))
        else:
            break
    cap.release()


def overlay_subtitle(img, subtitle, position):
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_size = 0.7
    thickness = 1
    for text in subtitle:
        size, baseline = cv2.getTextSize(text, font, font_size, thickness)
        p = (position[0], position[1])
        cv2.putText(img, text, p, font, font_size, (255,255,255), thickness, cv2.LINE_AA)
        position = [position[0], position[1] + size[1] + baseline]
    return img

