from math import trunc

import cv2
import numpy as np
import torch
import imutils

from utils.augmentations import letterbox
from utils.datasets import LoadImages
from utils.general import (check_img_size, non_max_suppression, scale_coords)
from utils.plots import Annotator, colors

@torch.no_grad()
def run(model,
        names,
        imgFront,
        device,
        aracKordinat,
        aracSayisi,
        conf_thres,
        iou_thres,
        max_det,
        classes,
        line_thickness,
        detectionLine,
        cs,ROAD_ID,db,thickness
        ):

    img0 = imgFront
    img = letterbox(img0, 640, stride=32, auto=True)[0]
    # Convert
    img = img.transpose((2, 0, 1))[::-1]  # HWC to CHW, BGR to RGB
    img = np.ascontiguousarray(img)
    im0s = img0
    im = img
    im = torch.from_numpy(im).to(device)
    im = im.float()  # uint8 to fp16/32
    im /= 255  # 0 - 255 to 0.0 - 1.0
    if len(im.shape) == 3:
        im = im[None]  # expand for batch dim
    pred = model(im, augment=False, visualize=False)

    # NMS
    pred = non_max_suppression(pred, conf_thres, iou_thres, classes, None, max_det=max_det)

    for i, det in enumerate(pred):  # per image
        im0 = im0s.copy()
        height, width = im0.shape[:2]
        annotator = Annotator(im0, line_width=line_thickness, example=str(names))

        height = trunc(height / detectionLine)
        color = (0, 0, 255)

        if len(det):
            # Rescale boxes from img_size to im0 size
            det[:, :4] = scale_coords(im.shape[2:], det[:, :4], im0.shape).round()

            # Write results
            for *xyxy, conf, cls in reversed(det):
                c = int(cls)  # integer class
                aracKordinat[c][1] = xyxy[1]
                aracKordinat[c][3] = xyxy[3]
                merkez=(aracKordinat[c][1]+aracKordinat[c][3])/2
                if (merkez > height and merkez < height + thickness):
                    aracSayisi[c] += 1
                    color = (0, 255, 0)
                    cs.execute('insert into road_car (road_id,car_id,quantity) values (?,?,?) ', [ROAD_ID, c, 1])
                    db.commit()
                label = f'{names[c]}'
                annotator.box_label(xyxy, label, color=colors(c, True))
        # Stream results
        im0 = annotator.result()
        im0 = cv2.line(im0, (0, height), (width, height), color, thickness)
        im0T = imutils.resize(im0, width=640)
        return im0T
