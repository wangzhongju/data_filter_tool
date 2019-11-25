
#! /usr/bin/env/ python
# coding=utf-8
#===================================================
#  Copyright (c) 2019 * Ltd. All rights reserved.
#  Editor          : VScode
#  Autor           : config.py
#  Created date    : 2019-10-28
#  Description
#===================================================


from easydict import EasyDict as edict



__C                             = edict()
cfg                             = __C


__C.YOLOV3                      = edict()

__C.YOLOV3.INPUT_SIZE           = 416
__C.YOLOV3.CLASS_PATH           = "./core/v3/classes.names"
__C.YOLOV3.PB_FILE              = "./weights/v3.pb"
__C.YOLOV3.SCORE_THRESHOLD      = 0.35
__C.YOLOV3.IOU_THRESHOLD        = 0.35

