import matplotlib.pyplot as plt
import sys
import os


txtfile = sys.argv[1]
name = os.path.basename(txtfile).split(".")[0]
imgpath = os.path.dirname(txtfile).split("/")[-1]
print("name:", name)
point_list = []
with open(txtfile,'r') as fp:
    points = fp.readlines()
    for point in points:
        point = point.strip('\n')
        point_list.append(float(point))
fig = plt.figure(figsize=(20,10),dpi=50)
x = range(1,len(point_list)+1)
plt.title('similarity between two pictures',fontsize=20,fontweight='black',
           fontstyle='italic')
plt.xlabel("image number",fontsize=16,fontweight='black',
           fontstyle='italic')
plt.ylabel("similarity",fontsize=16,fontweight='black',
           fontstyle='italic')
#    plt.tight_layout(pad=1.0,w_pad=0.5,h_pad=1.0)
plt.tight_layout()
plt.plot(x,point_list,label="similarity")
plt.plot(x,[0.9 for i in range(len(point_list))],color='red',label="Line of threshold value")
plt.legend(loc='lower right', fontsize=16)
plt.savefig("./data/result/{0}/{1}".format(imgpath, name))
# plt.xticks(x,x[::1])
# plt.show()
