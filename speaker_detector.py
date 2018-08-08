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
    cv2.imwrite(f'assets/avg.jpg', avg_img)
    return cv2.imread(f'assets/avg.jpg')


def detect_faces_from_an_img(avg_img):
    faces = cascade.detectMultiScale(avg_img, minNeighbors=15)
    # for (x, y, w, h) in faces:
    #     cv2.rectangle(avg_img, (x, y), (x + w, y + h), (0, 0, 200), 3)
    # cv2.imwrite(f'../assets/test_avg.jpg', avg_img)
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


def estimate_mouse(face):
    x, y, w, h = face
    return int(x + w / 4), int(y + h * 3 / 4), int(x + w * 3 / 4), int(y + h)


def filter_by_msd(faces, msds, threshold):
    faces_, msds_ = [], []
    for face, msd in zip(faces, msds):
        if msd > threshold:
            faces_.append(face)
            msds_.append(msd)
    return faces_, msds_
