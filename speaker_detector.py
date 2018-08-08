import cv2
import numpy as np

cascade_file_name = "assets/haarcascade_frontalface_default.xml"
cascade = cv2.CascadeClassifier(cascade_file_name)


def load_video(video_file_name):
    video = cv2.VideoCapture(video_file_name)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    return video, frame_count


def detect_faces(video_file_name):
    avg_img = generate_avg_img(video_file_name)
    faces = detect_faces_from_an_img(avg_img)
    return faces


def generate_avg_img(video_file_name):
    video, frame_count = load_video(video_file_name)
    avg_img = np.zeros((720, 1280, 3))
    for i in range(frame_count):
        _, img = video.read()
        try:
            avg_img += img
        except TypeError:
            pass
    avg_img = avg_img / frame_count
    cv2.imwrite(f'assets/tmp/avg.jpg', avg_img)
    return cv2.imread(f'assets/tmp/avg.jpg')


def detect_faces_from_an_img(avg_img):
    faces = cascade.detectMultiScale(avg_img, minNeighbors=15)
    for (x, y, w, h) in faces:
        cv2.rectangle(avg_img, (x, y), (x + w, y + h), (0, 0, 200), 3)
    cv2.imwrite(f'assets/tmp/faces.jpg', avg_img)
    try:
        return faces.tolist()
    except AttributeError:
        return []


def calc_msds(video_file_name, faces):
    msds = []
    for face in faces:
        msds.append(calc_msd(face, video_file_name))
    return msds


def calc_msd(face, video_file_name):
    video, frame_count = load_video(video_file_name)
    x, y, w, h = estimate_mouse(face)
    mouse_im = []
    msd = 0
    for i in range(frame_count):
        _, img = video.read()
        try:
            mouse_i = img[y:y + h, x:x + w].astype("int16")
            if len(mouse_im) != 0:
                msd += ((mouse_i - mouse_im) ** 2).sum() / h / w
        except TypeError:
            pass
        mouse_im = mouse_i
    msd = msd / (frame_count - 1)
    return msd


def filter_by_msd(faces, msds, threshold):
    faces_, msds_ = [], []
    for face, msd in zip(faces, msds):
        if msd > threshold:
            faces_.append(face)
            msds_.append(msd)
    return faces_, msds_


def calc_ccs(video_file_name, faces):
    ccs = []
    for face in faces:
        ccs.append(calc_cc(face, video_file_name))
    return ccs


def calc_cc(face, video_file_name):
    video, frame_count = load_video(video_file_name)
    width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    x, y, w, h = face
    center = [width/2, height/2]
    cc = 0
    for i in range(frame_count):
        _, img = video.read()
        cc += 100*(1 - (dist([x,y], center)/dist([0,0], center)))
    cc = cc / frame_count
    return cc


def filter_by_cc(faces, ccs, threshold):
    faces_ = []
    for face, cc in zip(faces, ccs):
        if cc > threshold:
            faces_.append(face)
    return faces_


def calc_lcs(video_file_name, faces, subtitle, subtitle_start_time, subtitle_end_time):
    lcs = []
    for face in faces:
        lcs.append(calc_lc(face, video_file_name, subtitle, subtitle_start_time, subtitle_end_time))
    return lcs


def calc_lc(face, video_file_name, subtitle, subtitle_start_time, subtitle_end_time):
    video, frame_count = load_video(video_file_name)
    frame_rate = int(video.get(cv2.CAP_PROP_FPS))
    l = frame_count
    l_std = (subtitle_end_time - subtitle_start_time).total_seconds() * frame_rate
    return 1/(abs(l - l_std))


def calc_avs(video_file_name, audio, faces):
    avs = []
    for face in faces:
        avs.append(calc_av(face, video_file_name, audio))
    return avs


def calc_av(face, video_file_name, audio):
    video, _ = load_video(video_file_name)
    video_feature = calc_video_feature(video)
    audio_feature = calc_audio_feature(audio)
    return np.dot(video_feature, audio_feature)

def calc_video_feature(video):
    return []


def calc_audio_feature(audio):
    return []


def estimate_mouse(face):
    x, y, w, h = face
    return int(x + w / 4), int(y + h * 3 / 4), int(w / 2), int(h / 4)


def dist(p, q):
    return ((p[0] - q[0]) ** 2 + (p[1] - q[1]) ** 2) ** (1 / 2)
