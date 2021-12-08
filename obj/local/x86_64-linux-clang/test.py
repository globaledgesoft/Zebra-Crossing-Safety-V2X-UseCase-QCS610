import qcsnpe as qc
import cv2
import numpy as np



def postprocess(out, video_height, video_width):
    boxes = out["Postprocessor/BatchMultiClassNonMaxSuppression_boxes"]
    scores = out["Postprocessor/BatchMultiClassNonMaxSuppression_scores"]
    classes = out["detection_classes:0"]
    found = []

    for cur in range(len(scores)):
        probability = scores[cur]
        class_index = int(classes[cur])
        if class_index != 1 or probability < 0.6:
            continue

        y1 = int(boxes[4 * cur] * video_height)
        x1 = int(boxes[4 * cur + 1] * video_width)
        y2 = int(boxes[4 * cur + 2] * video_height)
        x2 = int(boxes[4 * cur + 3] * video_width)
        found.append([(x1, y1), (x2, y2)])

    return found

if __name__ == '__main__':
    image = cv2.imread("/home/arunraj/Work/QDN/thundercomm_610/cpp_snpe_human/Human_tracker_old/frame1.jpg")
    out_layers = np.array(["Postprocessor/BatchMultiClassNonMaxSuppression", "add_6"])
    model_path = "/home/arunraj/Work/QDN/thundercomm_610/cpp_snpe_human/qcs610-human-tracker/assets/mobilenet_ssd.dlc"
    dlc = qc.qcsnpe(model_path,out_layers, 0)
    img = cv2.resize(image, (300,300))
    out = dlc.predict(img)
    # print(out)
    res = postprocess(out, image.shape[0], image.shape[1])

    for box in res:
        cv2.rectangle(image, box[0], box[1], (255,0,0), 2)

    cv2.imshow("win", image)
    k = cv2.waitKey(0)

