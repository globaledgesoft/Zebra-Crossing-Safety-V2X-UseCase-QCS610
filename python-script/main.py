import qcsnpe as qc
import cv2
import numpy as np
from mqtt_utils import Mqtt_Class
import json
from datetime import datetime
import argparse

def postprocess(out, video_height, video_width):
    boxes = out["Postprocessor/BatchMultiClassNonMaxSuppression_boxes"]
    scores = out["Postprocessor/BatchMultiClassNonMaxSuppression_scores"]
    classes = out["detection_classes:0"]
    found = []

    for cur in range(len(scores)):
        probability = scores[cur]
        class_index = int(classes[cur])
        if class_index != 1 or probability < 0.5:
            continue

        y1 = int(boxes[4 * cur] * video_height)
        x1 = int(boxes[4 * cur + 1] * video_width)
        y2 = int(boxes[4 * cur + 2] * video_height)
        x2 = int(boxes[4 * cur + 3] * video_width)
        found.append([(x1, y1), (x2, y2)])

    return found

def find_point(poly_cord, pt) :
    (x1, y1), (x2, y2), (x3, y3), (x4, y4) = poly_cord
    x, y = pt
    
    p21 = (x2 - x1, y2 - y1)
    p41 = (x4 - x1, y4 - y1)

    p21magnitude_squared = p21[0]**2 + p21[1]**2
    p41magnitude_squared = p41[0]**2 + p41[1]**2

    p = (x - x1, y - y1)

    if 0 <= p[0] * p21[0] + p[1] * p21[1] <= p21magnitude_squared:
        if 0 <= p[0] * p41[0] + p[1] * p41[1] <= p41magnitude_squared:
            return True
        else:
            return False
    else:
        return False

def argsParser():
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("-c", "--capture" ,action="store_true", default=False, help="path to image file")
    arg_parse.add_argument("-p", "--path",type=str, help="path to image file")
    args = vars(arg_parse.parse_args())
    return args

def main_stream():
    config_file = open('config.json')
    config = json.load(config_file)
    cap = cv2.VideoCapture(config['camera_pipeline'], cv2.CAP_GSTREAMER)
    out_layers = np.array(["Postprocessor/BatchMultiClassNonMaxSuppression", "add_6"])
    model_path = config['model_path']
    cl = Mqtt_Class(config['camera_id'], config['ip'])
    dlc = qc.qcsnpe(model_path,out_layers, 0)

    roi_file = open(config['roi_file_path'])
    roi = json.load(roi_file)
    polygon = [(roi['ix'], roi['iy']), (roi['fx'], roi['iy']), (roi['fx'], roi['fy']), (roi['ix'], roi['fy'])]

    while(cap.isOpened()):
        ret, image = cap.read()
        img = cv2.resize(image, (300,300))
        out = dlc.predict(img)
        people_cord = []
        res = postprocess(out, config['width'], config['height'])
        cv2.rectangle(image, (roi['ix'], roi['iy']), (roi['fx'], roi['fy']), (0, 255,0), 2)
        for i in polygon:
            image = cv2.circle(image, i, radius=2, color=(0, 0, 255), thickness=-1)
        for box in res:
            cv2.rectangle(image, box[0], box[1], (255,0,0), 2)
            tracking_point = (int(box[0][0] + ((box[1][0] - box[0][0])/2)), int(box[1][1]))
            image = cv2.circle(image, tracking_point, radius=4, color=(255, 0, 255), thickness=-1)
            if find_point(polygon, tracking_point):
                people_cord.append(tracking_point)
    
        if people_cord:
            payload = json.dumps({"time": str(datetime.now()), "camera_id": cl.client_id, "is_safe": str(not bool(people_cord)),"people_count": str(len(people_cord)), "cordinates": people_cord})
        else:
            payload = json.dumps({"time": str(datetime.now()), "camera_id": cl.client_id, "is_safe": str(not bool(people_cord)),"people_count": str(len(people_cord))})
        cl.publish_topic("human_detected", payload)
    cap.release()

def main_capture():
    config_file = open('config.json')
    config = json.load(config_file)
    cap = cv2.VideoCapture(config['camera_pipeline'], cv2.CAP_GSTREAMER)
    if cap.isOpened():
        ret, image = cap.read()
        image = cv2.resize(image, (300,300))
        print("saving frame.jpg")
        cv2.imwrite('frame.jpg', image)
    cap.release()

def main_test(path):
    config_file = open('config.json')
    config = json.load(config_file)
    out_layers = np.array(["Postprocessor/BatchMultiClassNonMaxSuppression", "add_6"])
    model_path = config['model_path']

    roi_file = open(config['roi_file_path'])
    roi = json.load(roi_file)

    cl = Mqtt_Class(config['camera_id'], config['ip'])
    
    image = cv2.imread(path)
    image = cv2.resize(image, (768, 576))
    img = cv2.resize(image, (300,300))
    dlc = qc.qcsnpe(model_path,out_layers, 0)
    out = dlc.predict(img)
    people_cord = []
    res = postprocess(out, config['height'], config['width'])
    polygon = [(roi['ix'], roi['iy']), (roi['fx'], roi['iy']), (roi['fx'], roi['fy']), (roi['ix'], roi['fy'])]

    cv2.rectangle(image, (roi['ix'], roi['iy']), (roi['fx'], roi['fy']), (0, 255,0), 2)
    for i in polygon:
        image = cv2.circle(image, i, radius=2, color=(0, 0, 255), thickness=-1)
    for box in res:
        cv2.rectangle(image, box[0], box[1], (255,0,0), 2)
        tracking_point = (int(box[0][0] + ((box[1][0] - box[0][0])/2)), int(box[1][1]))
        image = cv2.circle(image, tracking_point, radius=4, color=(255, 0, 255), thickness=-1)
        if find_point(polygon, tracking_point):
            people_cord.append(tracking_point)

    if people_cord:
        payload = json.dumps({"time": str(datetime.now()), "camera_id": cl.client_id, "is_safe": str(not bool(people_cord)),"people_count": str(len(people_cord)), "cordinates": people_cord})
    else:
        payload = json.dumps({"time": str(datetime.now()), "camera_id": cl.client_id, "is_safe": str(not bool(people_cord)),"people_count": str(len(people_cord))})
    cl.publish_topic("human_detected", payload)
    cv2.imwrite('output.jpg', image)

if __name__ == '__main__':
    args = argsParser()
    if args['capture']:
        main_capture()
    elif args['path']:
        main_test(args['path'])
    else:
        main_stream()
