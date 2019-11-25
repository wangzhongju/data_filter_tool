#=====================================
#  calculate bbox between v2 and v3
#  choose the images that hard scene
#        just for test
#=====================================


import os
import cv2
import sys
import glob
import math
import shutil
import colorsys


class Compare_Bbox:
    """
    this is class for compare two bboxes
    """
    def __init__(self, v2_label_path, v3_label_path, img_path, a, b, c, d):
        # Focus on the recognition effect of "DontCare" & "Cyclist"
        self.threshold_focus  = 1
        # iou compare
        self.threshold_iou    = 2
        # all the number between v2 and v3 diff
        self.threshold_number = 2   # replced by num_v3*scale
        self.iou              = 0.8
        self.v2_label_path    = v2_label_path
        self.v3_label_path    = v3_label_path
        self.img_path         = img_path
        self.label_name_v2    = ["Pedestrian", "Cyclist", "Car", "DontCare", "Car_gr"]
        self.label_name_v3    = ["person","bicycle","motorbike","car","truck","bus","bench",
                                 "babycar","roadblock","dog","wheelchair","trash","car_gr"]
        self.bbox_dict_v2     = self.init_dict_data("v2")
        self.bbox_dict_v3     = self.init_dict_data("v3")
        self.label_v3_to_v2   = {"Pedestrian":["person"],"Cyclist":["bicycle","motorbike"],"Car":["car","bus","truck"],
                            "DontCare":["trash","bench","roadblock","babycar","dog","wheelchair"],"Car_gr":["car_gr"]}
        find_file_name        = img_path.split("/")[-2]
        self.file_name        = find_file_name
        self.dirpath          = os.path.dirname(img_path)
        self.save_path        = img_path.replace(self.dirpath, "./res/{}/imgorg/".format(self.file_name))
        self.save_2dimg_path  = img_path.replace(self.dirpath, "./res/{}/img2d/".format(self.file_name))
        self.save_txtfile     = img_path.replace(self.dirpath, "./res/{}/label2d/".format(self.file_name)).replace(".jpg", ".txt")
        self.simi_v2_v3       = img_path.replace(self.dirpath, "./res/{}/other/".format(self.file_name))
        self.a = a
        self.b = b
        self.c = c
        self.d = d
        
    def init_dict_data(self, net="v2"):
        bbox_dict = {}
        label_name = self.label_name_v2 if net=="v2" else self.label_name_v3
        for key in label_name:
            bbox_dict[key] = []
        return bbox_dict
        
    def read_coor(self):
        with open(self.v2_label_path, 'r') as fp1:
            for line in fp1.readlines():
                name = line.split(' ')[0]
                [x1,y1,x2,y2] = [line.split(' ')[4],line.split(' ')[5],line.split(' ')[6],line.split(' ')[7]]
                data_v2 = [int(a) for a in [x1,y1,x2,y2]]
                data_v2.append(line.strip('\n').split(' ')[15]) # append score
                self.bbox_dict_v2[name].append(data_v2)
        with open(self.v3_label_path, 'r') as fp2:
            for line_ in fp2.readlines():
                name = line_.split(' ')[0]
                [x1,y1,x2,y2] = [line_.split(' ')[4],line_.split(' ')[5],line_.split(' ')[6],line_.split(' ')[7]]
                data_v3 = [int(a) for a in [x1,y1,x2,y2]]
                data_v3.append(line_.strip('\n').split(' ')[15])
                self.bbox_dict_v3[name].append(data_v3)

    def compare_number(self):
        """
        """
        num_v2 = 0
        num_v3 = 0
        for k,v in self.bbox_dict_v2.items():
            num_v2 += len(v)
        for k,v in self.bbox_dict_v3.items():
            num_v3 += len(v)
        return num_v2, num_v3

    def get_label_v3_to_v2(self, labelname):
        for k,v in self.label_v3_to_v2.items():
            if labelname in v:
                return k
        else:
            print("this %s labelname do not in label_list, please check it!"%labelname)
            return None

    def calculate_iou(self, labelname, bbox_v3):
        """
        """
        bbox_v2 = self.bbox_dict_v2[labelname]
        # Focus on the recognition effect of "DontCare" & "Cyclist"
        if labelname in ["DontCare", "Cyclist"]:
            # if math.fabs(len(bbox_v3) - len(bbox_v2)) >= self.threshold_focus:
            if (len(bbox_v3) - len(bbox_v2)) >= self.threshold_focus:
                return -1
        # Keep pictures containing car_gr
        if labelname == "Car_gr":
            return True
        # Now cal IOU
        else:
            threshold = 0
            for b3 in bbox_v3:
                iou_list = []
                for b2 in bbox_v2:
                    v3_x1, v3_y1, v3_x2, v3_y2 = b3[0], b3[1], b3[2], b3[3]
                    v2_x1, v2_y1, v2_x2, v2_y2 = b2[0], b2[1], b2[2], b2[3]
                    inter_rect_x1 = max(v3_x1, v2_x1)
                    inter_rect_y1 = max(v3_y1, v2_y1)
                    inter_rect_x2 = min(v3_x2, v2_x2)
                    inter_rect_y2 = min(v3_y2, v2_y2)
                    v3_area       = (v3_x2 - v3_x1 + 1) * (v3_y2 - v3_y1 + 1)
                    v2_area       = (v2_x2 - v2_x1 + 1) * (v2_y2 - v2_y1 + 1)
                    inter_area    = max(inter_rect_x2-inter_rect_x1+1, 0) * max(inter_rect_y2-inter_rect_y1+1, 0)
                    iou           = inter_area / (v3_area + v2_area - inter_area + 1e-16)
                    iou_list.append(iou)
                if iou_list != []:
                    # print(max(iou_list))
                    if max(iou_list) < self.iou:
                        threshold += 1
            return threshold

    def draw_bbox(self):
        img = cv2.imread(self.img_path)
        for k2,v2 in self.bbox_dict_v2.items():
            classname = k2
            for coor in v2:
                c1 = (coor[0], coor[1])
                c2 = (coor[2], coor[3])
                score = coor[4]
                bbox_mess = '%s: %s' % (classname, score)
                t_size = cv2.getTextSize(bbox_mess, 0, fontScale=0.5, thickness=2)[0]
                cv2.rectangle(img, c1, c2, (0,0,255), 2)
                cv2.rectangle(img, c1, (c1[0] + t_size[0], c1[1] - t_size[1] - 3), (255,0,0), -1)
                cv2.putText(img, bbox_mess, (c1[0], c1[1]-2), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0,0,0), 2, lineType=cv2.LINE_AA)
        for k3,v3 in self.bbox_dict_v3.items():
            classname = k3
            for coor in v3:
                c1 = (coor[0], coor[1])
                c2 = (coor[2], coor[3])
                score = coor[4]
                bbox_mess = '%s: %s' % (classname, score)
                t_size = cv2.getTextSize(bbox_mess, 0, fontScale=0.5, thickness=2)[0]
                cv2.rectangle(img, c1, c2, (255,0,0), 2)
                cv2.rectangle(img, c1, (c1[0] + t_size[0], c1[1] - t_size[1] - 3), (255,0,0), -1)
                cv2.putText(img, bbox_mess, (c1[0], c1[1]-2), cv2.FONT_HERSHEY_SIMPLEX,
                            0.5, (0,0,0), 2, lineType=cv2.LINE_AA)
        # cv2.imwrite(self.save_2dimg_path, img)
        return img
        # cv2.imshow("test", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
                
                

    def compare(self):
        """
        """
        self.read_coor()
        # print(self.bbox_dict_v2)
        # print(self.bbox_dict_v3)
    
        # first compare the number between v2 and v3
        num_v2, num_v3 = self.compare_number()
        # if (num_v3 - num_v2) > self.threshold_number:
        if num_v3 > 5 and (num_v3 - num_v2) > round(num_v3*0.2):
            shutil.copy(self.img_path, self.save_path)
            shutil.copy(self.v3_label_path, self.save_txtfile)
            img = self.draw_bbox()
            cv2.imwrite(self.save_2dimg_path, img)
            self.a += 1
        elif num_v3 == 0:
            img = self.draw_bbox()
            cv2.imwrite(self.simi_v2_v3, img)            
        # second calculate each bboxs that contained in v2 & v3 iou
        else:
            for k3,v3 in self.bbox_dict_v3.items():
                if v3 != []:
                    k3_new = self.get_label_v3_to_v2(k3)
                    # if v3 != []:
                    res = self.calculate_iou(k3_new, v3)
                    # if res == True:
                    #     shutil.copy(self.img_path, self.save_path)
                    #     shutil.copy(self.v3_label_path, self.save_txtfile)
                    #     img = self.draw_bbox()
                    #     cv2.imwrite(self.save_2dimg_path, img)
                    #     print("DontCare & Cyclist compare finding")
            if res == -1:
                shutil.copy(self.img_path, self.save_path)
                shutil.copy(self.v3_label_path, self.save_txtfile)
                img = self.draw_bbox()
                cv2.imwrite(self.save_2dimg_path, img)
                # print("DontCare & Cyclist compare finding")
                self.b += 1
            elif res > self.threshold_iou:
                shutil.copy(self.img_path, self.save_path)
                shutil.copy(self.v3_label_path, self.save_txtfile)
                img = self.draw_bbox()
                cv2.imwrite(self.save_2dimg_path, img)
                self.c += 1
            # Keep pictures containing car_gr
            elif res == True:
                shutil.copy(self.img_path, self.save_path)
                shutil.copy(self.v3_label_path, self.save_txtfile)
                img = self.draw_bbox()
                cv2.imwrite(self.save_2dimg_path, img)
                self.d += 1
            else:
                img = self.draw_bbox()
                cv2.imwrite(self.simi_v2_v3, img)
        return self.a, self.b, self.c, self.d
        
            


if __name__ == "__main__":
    path = sys.argv[1]
    filename = os.path.basename(path)
    for a in ["./res/{}/imgorg/".format(filename), "./res/{}/img2d/".format(filename), \
            "./res/{}/label2d/".format(filename), "./res/{}/other/".format(filename)]:
        if os.path.exists(a):
            shutil.rmtree(a)
        os.makedirs(a)
    res = path.split('/')[-1]
    v2_label_path = "./labels/{}/v2".format(res)
    txts = glob.glob(v2_label_path+"/*")
    txts.sort()
    cout = 0
    total_n = len(txts)
    a,b,c,d = [0 for i in range(4)]
    for txt in txts:
        v2_label_path = txt
        v3_label_path = txt.replace("/v2", "/v3")
        name = os.path.basename(v2_label_path)
        imgname = os.path.splitext(name)[0] + ".jpg"
        img_path = os.path.join(path, imgname)
        compare = Compare_Bbox(v2_label_path, v3_label_path, img_path, a, b, c, d)
        a,b,c,d = compare.compare()
        cout += 1
        if cout % 500 == 0:
            print("Remaining {} images!".format(total_n - cout))
    print("a b c d: {} {} {} {}".format(a,b,c,d))
    
    
