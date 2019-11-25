import os
import cv2
import sys
import torch
import time
import numpy as np
import glob
import core.config as cfg
import core.v2.apollo_yolo_2d as NET



os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "0"

class Detect_Test:
    # def __init__(self, model, pics_path, save_path):
    def __init__(self, model, img_path):
        # self.weight_file = "./core/v2/lg_895.pkl"
        self.anchor_file = "./core/v2/anchor_apollo.txt"
        # self.pics_path = pics_path
        # self.save_path = save_path
        self.img_path = img_path
        res_ = img_path.split("/")[-1]
        self.res = img_path.split(res_)[0]
        self.save_path = img_path.replace(self.res, "./labels/") + "/v2/"
        self.save_2dimg = img_path.replace(self.res, "./img2d/") + "/v2/"
        self.anchor = self.get_anchors()
        # self.weight = torch.load(self.weight_file)
        # self.net = model.cuda()
        self.net = model
        # self.net.load_state_dict(self.weight)
        self.net_height = 24
        self.net_width = 42
        self.color_map = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0),(0, 255, 255)]
        self.cls_map = ['Car','Cyclist', 'Pedestrian','DontCare', 'Car_gr']
        if not os.path.exists(self.save_path):os.makedirs(self.save_path)
        if not os.path.exists(self.save_2dimg):os.makedirs(self.save_2dimg)
    def get_anchors(self):
        anchors = []
        with open(self.anchor_file) as f:
            line = f.readline()
            while line:
                line = line.strip().split()
                anchors.append([float(line[0]), float(line[1])])
                line = f.readline()
        anchors = torch.Tensor(np.array(anchors)).cuda()
        return anchors
    def pred2box(self, net_out, conf_thresh=.7):
        
        obj_out, cls_out, loc_out = net_out
        obj_out = obj_out.detach().squeeze()
        cls_out = cls_out.detach().squeeze()
        loc_out = loc_out.detach().squeeze()
        height, width, anchor_num = obj_out.shape
        self.cls_num = int(cls_out.numel()/height/width/anchor_num)
        self.net_height = height
        self.net_width = width
        
        cls_out = cls_out.reshape(height, width, anchor_num, -1).softmax(-1)
        loc_out = loc_out.reshape(height, width, anchor_num, -1)
        
        #careful with the low confthresh
        
        confs = cls_out * obj_out.sigmoid().unsqueeze(-1).expand(height, width, anchor_num, self.cls_num)
        mask = confs.ge(conf_thresh)
        box_h, box_w, box_c, box_cls = mask.nonzero().t().float()
        
        boxes = loc_out[box_h.long(), box_w.long(), box_c.long()]
        boxes = boxes.view(-1, 4)
        
        boxes[..., 0] = box_w + boxes[..., 0].sigmoid()
        boxes[..., 1] = box_h + boxes[..., 1].sigmoid()
        boxes[..., 2] = boxes[..., 2].exp() * self.anchor[:, 0][box_c.long()] / 2
        boxes[..., 3] = boxes[..., 3].exp() * self.anchor[:, 1][box_c.long()] / 2
        boxes[..., 0] = boxes[..., 0] - boxes[..., 2]
        boxes[..., 1] = boxes[..., 1] - boxes[..., 3]
        boxes[..., 2] = 2 * boxes[..., 2] + boxes[..., 0]
        boxes[..., 3] = 2 * boxes[..., 3] + boxes[..., 1]
        box_cls = box_cls.unsqueeze(-1)
        boxes_conf = confs[mask].unsqueeze(-1)
        return torch.cat((boxes, box_cls, boxes_conf), -1)
        
    def iou_cal(self, box1, box2):
        """IOU calculation between box1 and box2, box could be any shape"""
        if len(box1.shape) == 1:
            box1 = box1.view(1, box1.shape[0])
        if len(box2.shape) == 1:
            box2 = box2.view(1, box2.shape[0])
        ious = torch.zeros((box2.shape[0],) + box1.shape[:-1]).cuda()
        for i in range(box2.shape[0]):
            box2_ = box2[i]
            box_tmp = {}
            area1 = (box1[..., 2] - box1[..., 0]) * (box1[..., 3] - box1[..., 1])
            area2 = (box2_[..., 2] - box2_[..., 0]) * (box2_[..., 3] - box2_[..., 1])
            #
            box_tmp['x1'] = torch.max(box1[..., 0], box2_[..., 0])
            box_tmp['y1'] = torch.max(box1[..., 1], box2_[..., 1])
            box_tmp['x2'] = torch.min(box1[..., 2], box2_[..., 2])
            box_tmp['y2'] = torch.min(box1[..., 3], box2_[..., 3])
            box_w = torch.max(torch.zeros(1).cuda(), box_tmp['x2'] - box_tmp['x1'])
            box_h = torch.max(torch.zeros(1).cuda(), box_tmp['y2'] - box_tmp['y1'])
            intersection = box_w * box_h
            ious[i] = intersection / (area1 + area2 - intersection)
        return ious
    def nms(self, boxes, iou_thresh = .5):
        sort_idxs = boxes[..., -1].sort(descending=True)[1]
        boxes = boxes[sort_idxs]
        box_idx = 0
        while True:
            if boxes[box_idx+1:].numel() == 0: break
            ious = self.iou_cal(boxes[box_idx], boxes[box_idx+1:])
            mask = ious.le(iou_thresh).squeeze(-1)
            boxes = torch.cat((boxes[:box_idx+1], boxes[box_idx+1:][mask]), )
            box_idx += 1 
        return boxes
    def boxes_cls(self, boxes):
        re = {}
        for i in range(self.cls_num):
            mask = boxes[..., -2] == i
            re[i] = boxes[mask]
        return re
            
    def detect(self, delay=1):
        # pics_file = os.listdir(self.pics_path)
        # for pic_f in pics_file:
        #     im = cv2.imread(self.pics_path+pic_f)
        imgs = glob.glob(self.img_path+"/*")
        imgs.sort()
        for img in imgs:
            t1 = time.time()
            imgname = os.path.basename(img)
            txtname = os.path.splitext(imgname)[0] + ".txt"
            im_old = cv2.imread(img)
            ori_h, ori_w = im_old.shape[:2]
            im = cv2.resize(im_old, (672, 376))
            # im = cv2.resize(im_old , (960, 540))
            pic_height, pic_width = im.shape[:2]
            scale_h = float("%.4f"%(ori_h / pic_height))
            scale_w = float("%.4f"%(ori_w / pic_width))

            pic = torch.Tensor(im).cuda()
            pic = pic.unsqueeze(0).float()
            net_out = self.net(pic)
            boxes = self.pred2box(net_out, 0.6)

            scale_height = pic_height / self.net_height
            scale_width = pic_width / self.net_width
        
            
            boxes = self.boxes_cls(boxes)
            #print(boxes)
            for i in range(self.cls_num):
                boxes[i] = self.nms(boxes[i])
                boxes[i][..., [0, 2]] *= (scale_h * scale_width)
                boxes[i][..., [1, 3]] *= (scale_w * scale_height)
                boxes[i] = boxes[i].cpu().numpy()
                boxes[i] = np.maximum(boxes[i], 0)  # or np.where(boxes[i] > 0, boxes[i], 0)
            with open(self.save_path+txtname, 'w+') as f:
                for cls_id in boxes:
                    for box in boxes[cls_id]:
                        p1 = (int(box[0]), int(box[1]))
                        p2 = (int(box[2]), int(box[3]))
                        cv2.rectangle(im_old, p1, p2, (0,0,255), 2)
                        cv2.putText(im_old, self.cls_map[cls_id]+': %.2f'%box[-1], p1, 
                                    cv2.FONT_HERSHEY_SIMPLEX, .5, self.color_map[cls_id] )
                        f.writelines(str(self.cls_map[cls_id])+" 0 0 0 %d"%(p1[0])+" %d"%(p1[1])+ 
                                        " %d"%(p2[0])+" %d 0 0 0 0 0 0 0 "%(p2[1])+ "%.4f\n"%box[-1])                        
            t2 = time.time()
            print("Total time with one pic: ", t2 - t1)
            cv2.imwrite(self.save_2dimg+imgname, im_old)
            # cv2.imshow('image', im_old)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
     
if __name__ == '__main__':
    ##path to net.py
    ##path to weight file
    ##path to anchor file
    start = time.time()
    net = NET.MyNet()
    net = net.cuda()
    weight_file = "./weights/v2.pkl"
    weight = torch.load(weight_file)
    net.load_state_dict(weight)
    end = time.time()
    print("load v2 use time:", end-start)
    # net = load_v2()
    detect = Detect_Test(net, sys.argv[1])
    detect.detect()

            
            
            
        
        
        
