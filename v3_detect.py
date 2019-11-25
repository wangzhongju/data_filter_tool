import tensorflow as tf
import cv2
import os
import sys
from core.config import cfg
import numpy as np
import time
import colorsys
import random
from PIL import Image
import glob


os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"

class Detect_v3:
    def __init__(self, image_path):
        self.return_elements = ["input/input_data:0", "pred_sbbox/concat_2:0", "pred_mbbox/concat_2:0", "pred_lbbox/concat_2:0"]
        self.pb_file         = cfg.YOLOV3.PB_FILE
        self.image_path      = image_path
        res_                 = image_path.split("/")[-1]
        self.res             = image_path.split(res_)[0]
        self.input_size      = cfg.YOLOV3.INPUT_SIZE
        self.graph           = tf.Graph()
        self.class_path      = cfg.YOLOV3.CLASS_PATH
        self.classes         = self.read_class_names(self.class_path)
        self.num_classes     = len(self.classes)
        self.save_path       = image_path.replace(self.res, "./labels/") + "/v3/"
        self.score_threshold = cfg.YOLOV3.SCORE_THRESHOLD
        self.iou_threshold   = cfg.YOLOV3.IOU_THRESHOLD
        self.save_2dimg      = self.image_path.replace(self.res, "./img2d/") + "/v3/"
        if not os.path.exists(self.save_path):os.makedirs(self.save_path)
        if not os.path.exists(self.save_2dimg):os.makedirs(self.save_2dimg)

    def image_preporcess(self, image, target_size, gt_boxes=None):
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32)
        ih, iw    = target_size
        h,  w, _  = image.shape
        scale = min(iw/w, ih/h)
        nw, nh  = int(scale * w), int(scale * h)
        image_resized = cv2.resize(image, (nw, nh))
        image_paded = np.full(shape=[ih, iw, 3], fill_value=128.0)
        dw, dh = (iw - nw) // 2, (ih-nh) // 2
        image_paded[dh:nh+dh, dw:nw+dw, :] = image_resized
        image_paded = image_paded / 255.
        if gt_boxes is None:
            return image_paded
        else:
            gt_boxes[:, [0, 2]] = gt_boxes[:, [0, 2]] * scale + dw
            gt_boxes[:, [1, 3]] = gt_boxes[:, [1, 3]] * scale + dh
            return image_paded, gt_boxes
    def read_class_names(self, class_file_name):
        '''loads class name from a file'''
        '''{0: 'bicycle', 1: 'motorbike', 2: 'car', 3: 'wheelchair', 4: 'dog', 5: 'bench', 6: 'roadblock',
            7: 'person', 8: 'truck', 9: 'bus', 10: 'babycar', 11: 'trash'}'''
        names = {}
        with open(class_file_name, 'r') as data:
            for ID, name in enumerate(data):
                names[ID] = name.strip('\n')
        return names
    def read_pb_return_tensors(self, graph, pb_file, return_elements):

        # with tf.gfile.FastGFile(pb_file, 'rb') as f:
        with tf.io.gfile.GFile(pb_file, 'rb') as f:
            # frozen_graph_def = tf.GraphDef()
            frozen_graph_def = tf.compat.v1.GraphDef()
            frozen_graph_def.ParseFromString(f.read())

        with graph.as_default():
            return_elements = tf.import_graph_def(frozen_graph_def,
                                                return_elements=return_elements)
        return return_elements
    def draw_bbox(self, image, bboxes, classes, show_label=True):
        """
        bboxes: [x_min, y_min, x_max, y_max, probability, cls_id] format coordinates.
        """

        num_classes = len(classes)
        image_h, image_w, _ = image.shape
        hsv_tuples = [(1.0 * x / num_classes, 1., 1.) for x in range(num_classes)]
        colors = list(map(lambda x: colorsys.hsv_to_rgb(*x), hsv_tuples))
        colors = list(map(lambda x: (int(x[0] * 255), int(x[1] * 255), int(x[2] * 255)), colors))

        random.seed(0)
        random.shuffle(colors)
        random.seed(None)

        for i, bbox in enumerate(bboxes):
            coor = np.array(bbox[:4], dtype=np.int32)
            fontScale = 0.5
            score = bbox[4]
            class_ind = int(bbox[5])
            bbox_color = colors[class_ind]
            bbox_thick = int(0.6 * (image_h + image_w) / 1200)
            c1, c2 = (coor[0], coor[1]), (coor[2], coor[3])
            # cv2.rectangle(image, c1, c2, bbox_color, bbox_thick)
            cv2.rectangle(image, c1, c2, (0,0,255), bbox_thick)

            if show_label:
                bbox_mess = '%s: %.2f' % (classes[class_ind], score)
                t_size = cv2.getTextSize(bbox_mess, 0, fontScale, thickness=bbox_thick//2)[0]
                cv2.rectangle(image, c1, (c1[0] + t_size[0], c1[1] - t_size[1] - 3), bbox_color, -1)  # filled

                cv2.putText(image, bbox_mess, (c1[0], c1[1]-2), cv2.FONT_HERSHEY_SIMPLEX,
                            fontScale, (0, 0, 0), bbox_thick//2, lineType=cv2.LINE_AA)

        return image
    def postprocess_boxes(self, pred_bbox, org_img_shape, input_size, score_threshold):

        valid_scale=[0, np.inf]
        pred_bbox = np.array(pred_bbox)

        pred_xywh = pred_bbox[:, 0:4]
        pred_conf = pred_bbox[:, 4]
        pred_prob = pred_bbox[:, 5:]

        # # (1) (x, y, w, h) --> (xmin, ymin, xmax, ymax)
        pred_coor = np.concatenate([pred_xywh[:, :2] - pred_xywh[:, 2:] * 0.5,
                                    pred_xywh[:, :2] + pred_xywh[:, 2:] * 0.5], axis=-1)
        # # (2) (xmin, ymin, xmax, ymax) -> (xmin_org, ymin_org, xmax_org, ymax_org)
        org_h, org_w = org_img_shape
        resize_ratio = min(input_size / org_w, input_size / org_h)

        dw = (input_size - resize_ratio * org_w) / 2
        dh = (input_size - resize_ratio * org_h) / 2

        pred_coor[:, 0::2] = 1.0 * (pred_coor[:, 0::2] - dw) / resize_ratio
        pred_coor[:, 1::2] = 1.0 * (pred_coor[:, 1::2] - dh) / resize_ratio

        # # (3) clip some boxes those are out of range
        pred_coor = np.concatenate([np.maximum(pred_coor[:, :2], [0, 0]),
                                    np.minimum(pred_coor[:, 2:], [org_w - 1, org_h - 1])], axis=-1)
        invalid_mask = np.logical_or((pred_coor[:, 0] > pred_coor[:, 2]), (pred_coor[:, 1] > pred_coor[:, 3]))
        pred_coor[invalid_mask] = 0

        # # (4) discard some invalid boxes
        bboxes_scale = np.sqrt(np.multiply.reduce(pred_coor[:, 2:4] - pred_coor[:, 0:2], axis=-1))
        scale_mask = np.logical_and((valid_scale[0] < bboxes_scale), (bboxes_scale < valid_scale[1]))

        # # (5) discard some boxes with low scores
        classes = np.argmax(pred_prob, axis=-1)
        scores = pred_conf * pred_prob[np.arange(len(pred_coor)), classes]
        score_mask = scores > score_threshold
        mask = np.logical_and(scale_mask, score_mask)
        coors, scores, classes = pred_coor[mask], scores[mask], classes[mask]
        # print(np.concatenate([coors, scores[:, np.newaxis], classes[:, np.newaxis]], axis=-1))

        return np.concatenate([coors, scores[:, np.newaxis], classes[:, np.newaxis]], axis=-1)
    def bboxes_iou(self, boxes1, boxes2):

        boxes1 = np.array(boxes1)
        boxes2 = np.array(boxes2)

        boxes1_area = (boxes1[..., 2] - boxes1[..., 0]) * (boxes1[..., 3] - boxes1[..., 1])
        boxes2_area = (boxes2[..., 2] - boxes2[..., 0]) * (boxes2[..., 3] - boxes2[..., 1])

        left_up       = np.maximum(boxes1[..., :2], boxes2[..., :2])
        right_down    = np.minimum(boxes1[..., 2:], boxes2[..., 2:])

        inter_section = np.maximum(right_down - left_up, 0.0)
        inter_area    = inter_section[..., 0] * inter_section[..., 1]
        union_area    = boxes1_area + boxes2_area - inter_area
        ious          = np.maximum(1.0 * inter_area / union_area, np.finfo(np.float32).eps)

        return ious
    def nms(self, bboxes, iou_threshold, sigma=0.3, method='nms'):
        """
        :param bboxes: (xmin, ymin, xmax, ymax, score, class)

        Note: soft-nms, https://arxiv.org/pdf/1704.04503.pdf
            https://github.com/bharatsingh430/soft-nms
        """
        classes_in_img = list(set(bboxes[:, 5]))
        best_bboxes = []

        for cls in classes_in_img:
            cls_mask = (bboxes[:, 5] == cls)
            cls_bboxes = bboxes[cls_mask]

            while len(cls_bboxes) > 0:
                max_ind = np.argmax(cls_bboxes[:, 4])
                best_bbox = cls_bboxes[max_ind]
                best_bboxes.append(best_bbox)
                cls_bboxes = np.concatenate([cls_bboxes[: max_ind], cls_bboxes[max_ind + 1:]])
                iou = self.bboxes_iou(best_bbox[np.newaxis, :4], cls_bboxes[:, :4])
                weight = np.ones((len(iou),), dtype=np.float32)

                assert method in ['nms', 'soft-nms']

                if method == 'nms':
                    iou_mask = iou > iou_threshold
                    weight[iou_mask] = 0.0

                if method == 'soft-nms':
                    weight = np.exp(-(1.0 * iou ** 2 / sigma))

                cls_bboxes[:, 4] = cls_bboxes[:, 4] * weight
                score_mask = cls_bboxes[:, 4] > 0.
                cls_bboxes = cls_bboxes[score_mask]
        return best_bboxes

    def detect(self, delay=1):
        # start = time.clock()
        start = time.perf_counter()
        return_tensors = self.read_pb_return_tensors(self.graph, self.pb_file, self.return_elements)
        end_of_load = time.perf_counter()
        print("load v3 network use time {}".format(end_of_load - start))
        imgs = glob.glob(self.image_path+"/*")
        imgs.sort()
        for img in imgs:
            t1 = time.perf_counter()
            imgname = os.path.basename(img)
            txtname = os.path.splitext(imgname)[0] + ".txt"
            original_image = cv2.imread(img)
            original_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB)
            original_image_size = original_image.shape[:2]
            image_data = self.image_preporcess(np.copy(original_image), [self.input_size, self.input_size])
            image_data = image_data[np.newaxis, ...]
            
            # with tf.Session(graph=self.graph) as sess:
            with tf.compat.v1.Session(graph=self.graph) as sess:
                pred_sbbox, pred_mbbox, pred_lbbox = sess.run(
                    [return_tensors[1], return_tensors[2], return_tensors[3]],
                            feed_dict={ return_tensors[0]: image_data})

            pred_bbox = np.concatenate([np.reshape(pred_sbbox, (-1, 5 + self.num_classes)),
                                        np.reshape(pred_mbbox, (-1, 5 + self.num_classes)),
                                        np.reshape(pred_lbbox, (-1, 5 + self.num_classes))], axis=0)

            bboxes = self.postprocess_boxes(pred_bbox, original_image_size, self.input_size, self.score_threshold)
            bboxes = self.nms(bboxes, self.iou_threshold, method='nms')

            with open(self.save_path+txtname, "w") as fp:
                for bbox in bboxes:
                    min_x, min_y, max_x, max_y = [str(int(bbox[i])) for i in range(4)]
                    score = str(round(bbox[4], 2))
                    label_name = self.classes[int(bbox[5])]
                    fp.writelines(label_name+" 0 0 0 "+min_x+" "+min_y+" "+max_x+" "+max_y+" 0 0 0 0 0 0 0 "+score)
                    fp.writelines("\n")

            # end = time.clock()
            t2 = time.perf_counter()
            print("Total time: %f", t2 - t1)

            image = self.draw_bbox(original_image, bboxes, self.classes)
            image_ = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            cv2.imwrite(self.save_2dimg+imgname, image_)
            # image = Image.fromarray(image)
            # image.show()
        
if __name__ == "__main__":
    imgpath = sys.argv[1]
    detect = Detect_v3(imgpath)
    detect.detect()