						ubuntu


每10秒显示一次显存的情况：$ watch -n 10 nvidia-smi

查看内存、cpu、进程：$ top htop

nvcc warning : The 'compute_20', 'sm_20', and 'sm_21' architectures are deprecated, and may be removed in a future release (Use -Wno-deprecated-gpu-targets to suppress warning).
	查阅了一些资料，发现这只是提示build target 2.0, 2.1被弃用了。如果不想让这些提示出现，只需要在编译时加上一个参数，表示基于自己显卡的计算能力选择build target即可。
	Tesla K80支持CUDA compute ability 3.7, 因此在编译时使用如下命令：
		nvcc -arch=sm_35 cudaPrintDeviceInfo.cu -o cudaPrintDeviceInfo
	即可解决问题。

查看内存：$ df -h
         $ free -m/top

进入含有空格的文件夹： eg: </path/test file/> cd /path/test\ file (转意符)
删除文件或者文件夹：$ rm  -rf
	
统计文件夹下的文件数目：$ ls -l | grep "^-" | wc -l

提示程序输入结束：另起一行，然后 Ctrl+d   (windows系统为 Ctrl+c)

查看文件夹下所有文件的大小总和： du -sh

.7z解压压缩：sudo apt-get install p7zip-full
	     7z x ***.7z -r -o/{...}/

***ubuntu下设置环境变量的三种方法
一种用于当前终端，一种用于当前用户，一种用于所有用户：
	1、用于当前终端：在当前终端中输入：export PATH=$PATH:<需要加入的路径>
	2、用于当前用户：$ sudo gedit ~/.bashrc		//打开.bashrc文件
	   加入：export PATH=<路径>:$PATH
	   加入多个路径：export PATH=<路径1>:<路径2>:......:$PATH
	   添加PYTHONPATH路近：export PYTHONPATH=/home/.../...:$PYTHONPATH
	   保存后在终端输入$ source ~/.bashrc使环境变量立即生效
	3、用于所有用户：$sudo gedit /etc/profile
	   加入：export PATH=<路径>:$PATH
	   $ source ~/.bashrc生效
	   终端输入：echo $PATH可以查看环境变量


***安装了ROS Kinetic之后Python3不能import Opencv
	这个问题是由ROS添加/opt/ros/kinetic/lib/python2.7/dist-packages到python路径引起的，
	当使用命令激活ROS时，实际上会发生这种情况source /opt/ros/kinetic/setup.bash。这行通常
	会添加到bashrc文件的末尾/home/username/.bashrc。解决方法是从bashrc文件中删除此行，无法
	在同一环境中使用ROS和python3。



***查看opencv安装版本和路径
	pkg-config --modversion opencv	//查看版本
	//搜索带有关键字opencv的所有文件及文件夹并输出到.txt文件中
	sudo find / -iname "*opencv*" > /home/wangzhongju/桌面/opencv_find.txt


***ubuntu安装了anaconda后安装opencv报错Makefile:160: recipe for target 'all' failed
	安装opencv后，很多默认的编译器都变成了anaconda自带的了，比如python和gcc，系统中python
	安装的东西自然是用不了的
	解决：1、增加   -D WITH-OPENMP=ON
	      2、从系统变量中删除Anaconda路径
		sudo gedit ~/.bashrc



***ubuntu查看cuda和cudnn版本
	cuda 版本：cat /usr/local/cuda/version.txt
	cudnn 版本：cat /usr/local/cuda/include/cudnn.h | grep CUDNN_MAJOR -A 2


***ubuntu系统CPU
	温度查看：
	$ sudo apt-get install lm-sensors
	$ sudo sensors-detect
	$ sudo service kmod start
	$ sensors
	信息查看：
	$ lscpu	//信息概要
	$ cat /proc/cpuinfo | grep name | cut -f2 -d: | uniq -c //型号
	$ cat /proc/cpuinfo | grep physical | uniq -c //物理cpu颗数


***Ubuntu添加全新硬盘步骤

	- 安装硬盘

 	- 查看系统硬盘分区
 		$ sudo fdisk -l 
	> **找到新硬盘路径，如/dev/sdb**
	- 格式化硬盘
		$ sudo mkfs.ext4 /dev/sdb
	- 查看硬盘分区
		$ sudo blkid![](/home/wangzhongju/下载/1.png) 
	- 在已有的user目录下新建一个挂载点
		$ sudo mkdir /home/wangzhongju/workspace
	- 编辑系统挂载配置文件/etc/fstab
		$ sudo vim /etc/fstab![](/home/wangzhongju/下载/2.png) 
		按照已有的格式，将新加的硬盘分区信息添加到末尾
		格式为：设备名称 挂载点 分区类型 挂载类型 dump选项 fsck选项
		dump选项-为0表示从不备份
		fsck选项-启动时fsck检查的顺序，0表示不检查，/分区永远是1
	- 修改对应的用户和权限
		$sudo chown -R wangzhongju:wangzhongju /home/wangzhongju/workspace

		$ sudo chmod -R 4755 /home/wangzhongju/workspace

	- 重启电脑
		$ sudo reboot



***ubuntu系统安装多个版本的cuda和cudnn：
	***cuda安装：
		第一个版本的cuda(若已经安装可直接到安装第二版本)：官网下载安装，nvidia驱动不安装选择n
				配置CUDA相关环境变量：
							Tensorflow官方安装历程要求注意的是:配置PATH和LD_LIBRARY_PATH和CUDA_HOME环境变量.
							vim ~/.bashrc #修改配置文件
							#在文件结尾处添加
							export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64
							export PATH=$PATH:/usr/local/cuda/bin
							export CUDA_HOME=$CUDA_HOME:/usr/local/cuda
		第二个版本的cuda安装：cuda symbol link选择n，其他同上

	***多版本cuda随时切换：
		$ cd /usr/local
		$ stat cuda		//查看cuda软链接指向那个cuda版本
		//修改cuda软链接指向版本
		$ sudo rm cuda
		$ sudo ln -sf /usr/local/cuda-9.0 /usr/local/cuda	//此时cuda软链接指向cuda-9.0版本，切换版本改变指向即可


	***cudnn安装：
		1.官网下载对应的cudnn版本(选择for linux，格式为.tgz)
		2.解压到任一路径下，$ sudo tar -zxvf ××× /home/wangzhongju/wzj
		3.将解压后的Lib64文件夹关联到环境变量中
			$ sudo ~/.bashrc
			在弹出的gedit文档编辑器（.bashrc中）中最后一行加入：
			export LD_LIBRARY_PATH=/home/wangzhongju/wzj/cuda/lib64:$LD_LIBRARY_PATH
			$ source ~/.bashrc
		4.将解压后的cuDNN文件夹(一般名为cuda)中的include文件夹中的cudnn.h文件拷贝到/usr/local/cuda/include中
			$ sudo cp /home/wangzhongju/wzj/cuda/include/cudnn.h /usr/local/cuda/include/
			$ sudo chmod a+r /usr/local/cuda/include/cudnn.h	//重置读写权限



***updata-alternatives    (慎用，会导致许多已安装的链接失效)
	维护系统命令链接符的工具，例如切换系统命令符python版本：
	进入root用户
	# update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
	# update-alternatives --install /usr/bin/python python /usr/bin/python3.5 2
	1和2代表优先级	--install用于创建符号链接
	# update-alternatives --list python
	# update-alternatives --config python   输入对应的优先级即可切换


***ubuntu解决安装meteor过慢
	1.下载安装包：
	   https://d3sqy0vbqsdhku.cloudfront.net/packages-bootstrap/1.2.1/meteor-bootstrap-os.linux.x86_64.tar.gz
	2.更改脚本：
	   将官网提供的脚本导出--> curl https://install.meteor.com > install.meteor.sh
	   找到脚本中TARBALL_URL所在位置将其修改为下载的安装包的路径位置，如：TARBALL_URL="file:///home/wangzhongju/workspace/meteor/meteor-bootstrap-os.linux.x86_64.tar.gz"
	   运行脚本即可完成安装
-------------------------------------------------------------------------------------------------------
sudo ln -s  /usr/lib/x86_64-linux-gnu/libproj.so.9 /usr/lib/x86_64-linux-gnu/libproj.so 
ln -s /dev/null /dev/raw1394
-------------------------------------------------------------------------------------------------------



***sudo apt-get update/upgrade
	update更新源，/etc/apt/sources.list和/etc/apt/sources.list.d
	upgrade:
		W: Possible missing firmware /lib/firmware/i915/kbl_dmc_ver1_01.bin for module i915
		W: Possible missing firmware /lib/firmware/i915/kbl_guc_ver9_14.bin for module i915
		W: Possible missing firmware /lib/firmware/i915/bxt_guc_ver8_7.bin for module i915
	解决：缺少固件，去https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/i915下载对应的文件，将下载的.bin文件cp到/lib/firmware/i915目录下即可。



***source.list文件
	/etc/apt/sources.list和/etc/apt/sources.list.d/目录中带.list后缀的文件。
	1.格式和写法
	  deb-二进制包仓库；deb-src二进制包的源码库；URI-库所在的地址，可以是网络地址，也可以是本地的镜像地址；
	  codename-Ubuntu版本的代号，可以用命令lsb_release -sc来查看当前系统的代号(xenial)；components-软件的性质(free或non-free)
	2.deb
	  格式：deb URI section1 section2
	  eg：  deb http://us.archive.ubuntu.com/ubuntu/ trusty universe
	  section1 section2为地址中文件夹名
	


***POINT CLOUD LIBRARY ON UBUNTU 16.04 LTS
	1. .deb安装包
	sudo dpkg -i PCL-1.8.0-Linux.deb(网盘)
	2. 源码编译安装
     	sudo apt-get update
     	sudo apt-get install git build-essential linux-libc-dev
     	sudo apt-get install cmake cmake-gui 
     	sudo apt-get install libusb-1.0-0-dev libusb-dev libudev-dev
     	sudo apt-get install mpi-default-dev openmpi-bin openmpi-common
     	sudo apt-get install libflann1.8 libflann-dev
     	sudo apt-get install libeigen3-dev
     	sudo apt-get install libboost-all-dev
     	sudo apt-get install libvtk5.10-qt4 libvtk5.10 libvtk5-dev
     	sudo apt-get install libqhull* libgtest-dev
     	sudo apt-get install freeglut3-dev pkg-config
     	sudo apt-get install libxmu-dev libxi-dev 
     	sudo apt-get install mono-complete
     	sudo apt-get install qt-sdk openjdk-8-jdk openjdk-8-jre

	git clone https://github.com/PointCloudLibrary/pcl.git

	cd pcl
     	mkdir release
     	cd release
     	cmake -DCMAKE_BUILD_TYPE=None -DCMAKE_INSTALL_PREFIX=/usr \
           -DBUILD_GPU=ON -DBUILD_apps=ON -DBUILD_examples=ON \
           -DCMAKE_INSTALL_PREFIX=/usr ..
     	make -j4
	sudo make -j4 install


***How to run ROS if your default python version is 3.x via Anaconda
	catkin_make error:
		ImportError: "from catkin_pkg.package import parse_package" failed: No module named 'catkin_pkg'
		Make sure that you have installed "catkin_pkg", it is up to date and on the PYTHONPATH.
	1.删除.bashrc中的anaconda路径
	2.卸载ros，sudo apt-get remove --purge ros-* && sudo rm -rf /etc/ros && vim ~/.bashrc 删除其中ros路径
	3.重装ros即可



***docker与主机copy文件
	docker到主机：
		docker cp NAMES:/..docker path../ /..主机path../
	主机到docker：
		调换顺序即可


***anaconda环境与ros或opencv冲突
	echo $PYTHONPATH
    使用ros环境：
	export PYTHONPATH=/opt/ros/kinetic/lib/python2.7/dist-packages
    使用anaconda环境：
	export PYTHONPATH=/home/wangzhongju/workspace/anaconda3/env/tensorflow/lib/python3.6/site-package


***代码批量左右移tab
	首先选择需要移动的行
	左移：Ctrl + [  或  Shift+tab
	右移：Ctrl + ]  或  Shift


***ubuntu无进程显存占用高
	使用nvidia-smi查看显存占用很高但是无进程
	fuser -v /dev/nvidia*
	/dev/nvidia0: 使用 sudo kill 9 PID

***ubuntu python
	pip安装python模块时出错 no attribute 'SSL_ST_INIT'
	rm -rf /usr/lib/python2.7/dist-packages/OpenSSL
　　	rm -rf /usr/lib/python2.7/dist-packages/pyOpenSSL-0.15.1.egg-info
	sudo pip install pyopenssl

***ubuntu源码编译安装caffe及python接口
	tip：此处在ubuntu自带python2.7下编译使用，屏蔽掉已创建的.bashrc文件中的anaconda环境
	git clone https://github.com/BVLC/caffe.git
	cd caffe && mkdir build
	cp Makefile.config.example ./build/Makefile.config
	cd build && 
	修改Makefile.config文件：
		1.去掉CUDA_ARCH前两行-gencode arch=compute_20,code=sm_20 \
					-gencode arch=compute_20,code=sm_21 \
		  去掉USE_CUDNN前的注释使用cudnn加速
		  根据系统安装的opencv版本选择OPENCV_VERSION是否注释
		  PYTHON_INCLUDE python路径可以选择更改其他的路径(如anaconda中的pytghon)
		  INCLUDE_DIRS添加路径/usr/include/hdf5/serial
		  LIBRARY_DIRS添加路径/usr/lib/x86_64-linux-gnu /usr/lib/x86_64-linux-gnu/hdf5/serial
	cmake .. 
	make all && make test && make runtest && make pycaffe
	-------
	make all 报错：
		/etc/profile文件中添加使用的cuda版本环境变量(此处使用cuda9.0,cudnn7.3)
			export PATH=/usr/local/cuda-9.0/bin:$PATH
			export LD_LIBRARY_PATH=/usr/local/cuda-9.0/lib64$LD_LIBRARY_PATH
	import caffe报错no moudle name caffe:
		sudo apt-get install gfortran
		cd ~/caffe/python
		删除该路径下requirements.txt文件中python-dateutil后的版本号默认最新版本
		for req in $(cat requirements.txt); do sudo pip install $req; done
		sudo pip install -r requirements.txt
		在~/.bashrc文件中添加：
			export PYTHONPATH=/home/wangzhongju/workspace/caffe_make/caffe/python:$PYTHONPATH
		source ~/.bashrc && sudo ldconfig
		cd ../build && make pycaffe


***the PyQt5.QtCore and PyQt4.QtCore modules both wrap the QObject class
	sudo apt-get remove python-pyqt5



***ubuntu系统翻墙
	前提：购买vps，并在服务器上配置好shadowsocks
	1.安装ss
	   建议使用系统python环境：
	   sudo apt-get install update
	   sudo apt-get install python-gevent python-pip
	   pip install shadowsocks
	2.建立配置文件(sudo vim /etc/ss.json)
		{
		    "server":"us1.dawangidc.top",  //vps服务器地址
		    "server_port":16000,	   //vps服务器端口
		    "local_address": "127.0.0.1",  //本地
		    "local_port":1080,		   //本地端口(netstat -tln)
		    "password":"goldenridge",	   //vps登录密码
		    "timeout":300,		   //超时时间
		    "method":"chacha20",	   //加密方式，默认
		    "fast_open" : false		   //默认
		}
	3.开启ss
	   sslocal -c /etc/ss.json   (查看sslocal版本：sslocal version)
	   若报错 AttributeError: /usr/lib/x86_64-Linux-gnu/libcrypto.so.1.1: 
		  undefined symbol: EVP_CIPHER_CTX_cleanup
		该问题是由于在openssl1.1.0版本中，废弃了EVP_CIPHER_CTX_cleanup
		解决：vim /usr/local/lib/python2.7/dist-packages/shadowsocks/crypto/openssl.py
		      搜索cleanup,共两处(52行与111行)，修改cleanup为reset
	  ————解决端口占用————
		ctrl+c关掉进程或者关闭当前终端都会直接让网络挂掉，重启电脑也没用，解决办法是：
		usrname$ ps aux | grep python
		找到占用进程号(process_number)
		usrname$ kill -9 process_number
	4.设置开机启动
	   # 打开图像化开机启动项管理界面--> gnome-session-properties
	   # 添加(Add) -> 名称(name)和描述(comment)随便填，命令(command)填写如下：
		sslocal -c /etc/ss.json
	5.转换HTTP代理
	   因为shadowsocks默认是用Socks5协议的，对于Terminal的get，wget等走Http协议的地方是无能为力的，
	   所以需要转换成Http代理，加强通用性，这里使用的转换方法是基于Polipo
		// 输入命令安装Polipo：
		sudo apt-get install polipo

		// 修改配置文件：
		sudo gedit /etc/polipo/config

		// 将下面的内容整个替换到文件中并保存：
		# This file only needs to list configuration variables that deviate
		# from the default values. See /usr/share/doc/polipo/examples/config.sample
		# and "polipo -v" for variables you can tweak and further information.
		logSyslog = false
		logFile = "/var/log/polipo/polipo.log"

		socksParentProxy = "127.0.0.1:1080"
		socksProxyType = socks5

		chunkHighMark = 50331648
		objectHighMark = 16384

		serverMaxSlots = 64
		serverSlots = 16
		serverSlots1 = 32

		proxyAddress = "0.0.0.0"
		proxyPort = 8123

		// 重启Polipo：
		/etc/init.d/polipo restart	   

	6.ubuntu机器和火狐浏览器配置
	   ubuntu配置：
		进入到Setting>Network>Network Proy
		选择Manual模式
		配置Socks Host: 127.0.0.1  1080
		点击 ok(若无则直接退出)
	   火狐浏览器配置
		Setting -> Preferences -> 拉至底部 -> 网络代理Network Proxy -> Setting
		选择Manual proxy configuration
		配置HTTP Proxy: 127.0.0.1  8123
		勾选Use this proxy server for all protocols

***vscode更改显示语言
	Ctrl+Shift+p
	Configure Display Language
	"locale":"en"改为"locale":"zh-CN"
	若为成功需进入商店：Ctrl+Shift+x，输入chinese进行下载

***ubuntu16.04配置c++编译环境
	安装vscode，不要使用sudo权限安装
	1.添加c++扩展
	  在Extension(或Ctrl+Shift+x)中搜索C++，并安装第一个扩展
	2.打开工程文件夹，随便编写一段初始的c++代码，按F5调出launch.json文件
		{
		    // Use IntelliSense to learn about possible attributes.
		    // Hover to view descriptions of existing attributes.
		    // For more information, visit: https://go.microsoft.com/fwlink/?linkid=830387
		    "version": "0.2.0",
		    "configurations": [
			{
			    "name": "(gdb) Launch",
			    "type": "cppdbg",
			    "request": "launch",
			    "program": "${workspaceFolder}/${fileBasenameNoExtension}.o",
			    "args": [],
			    "stopAtEntry": false,
			    "cwd": "${workspaceFolder}",
			    "environment": [],
			    "externalConsole": true,
			    "MIMode": "gdb",
			    "miDebuggerPath": "/usr/bin/gdb",
			    "preLaunchTask": "g++",
			    "setupCommands": [
				{
				    "description": "Enable pretty-printing for gdb",
				    "text": "-enable-pretty-printing",
				    "ignoreFailures": true
				}
			    ]
			},
		    ]
		}
	  program-->表明运行当前目录中与被编译文件同名的.o后缀文件
	  MIMode--->使用的debug工具，ubuntu为gdb，win10为MinGW，MacOS为lldb
	  miDebuggerPath-->指定gdb的位置
	3.task.json文件
		{
		    // See https://go.microsoft.com/fwlink/?LinkId=733558
		    // for the documentation about the tasks.json format
		    "version": "2.0.0",
		    "command": "g++",
		    "args": [
			"-g", 
			"-std=c++11", 
			"${file}", 
			"-o", 
			"${fileBasenameNoExtension}.o",
		    ],// 编译命令参数
		    "problemMatcher":{
			"owner": "cpp",
			"fileLocation":[
			    "relative",
			    "${workspaceFolder}"
			],
			"pattern":[
			    {
				"regexp": "^([^\\\\s].*)\\\\((\\\\d+,\\\\d+)\\\\):\\\\s*(.*)$",
				"file": 1,
				"location": 2,
				"message": 3
			    }
			]
		    },
		    "group": {
			"kind": "build",
			"isDefault": true
		    }
		}
	4.opencv编译环境配置
	  Ctrl+Shift+p-->搜cpp:Edit打开c_cpp_properties.json文件
		{
		    "configurations": [
			{
			    "name": "Linux",
			    "includePath": [
				"${workspaceFolder}/**",
				"/usr/local/include", //请确保你的opencv opencv2头文件夹安装在这个目录
				"/usr/include"
			    ],
			    "defines": [],
			    "compilerPath": "/usr/bin/gcc",
			    "cStandard": "c11",
			    "cppStandard": "c++17",
			    "intelliSenseMode": "clang-x64"
			}
		    ],
		    "version": 4
		}
	task.json中的args参数：
	"args": [
		"-g", "-std=c++11", "${file}", "-o", "${fileBasenameNoExtension}.o",// 设置动态链接库
		"-I", "/usr/local/include",
		"-I", "/usr/local/include/opencv",
		"-I", "/usr/local/include/opencv2",
		"-L", "/usr/local/lib",
		"-l", "opencv_core",
		"-l", "opencv_imgproc",
		"-l", "opencv_imgcodecs",
		"-l", "opencv_video",
		"-l", "opencv_ml",
		"-l", "opencv_highgui",
		"-l", "opencv_objdetect",
		"-l", "opencv_flann",
		"-l", "opencv_imgcodecs",
		"-l", "opencv_photo",
		"-l", "opencv_videoio"
	    ],
	  其中-I表示头文件目录，-L表示库文件目录，-l表示库文件
	tip:缺少libjasper.so.1解决：
		sudo add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main"
		sudo apt update
		sudo apt install libjasper1 libjasper-dev

***选择使用gpu
	import os
	os.environ['CUDA_VISIBLE_DEVICES'] = '2'

***pcl cmake 编译** WARNING ** io features related to pcap/png will be disabled
	pcl编译文件PCLConfig.cmake.in中
	macro(find_external_library _component _lib _is_optional)内
	add some lines to find pcap and png添加一些线寻找pcap与png

***cmake tip
    1.The imported target "vtkRenderingPythonTkWidgets" references the file
   "/usr/lib/x86_64-linux-gnu/libvtkRenderingPythonTkWidgets.so" but this file does not exist.
	解决：
	sudo ln -s /usr/lib/python2.7/dist-packages/vtk/libvtkRenderingPythonTkWidgets.x86_64-linux-gnu.so
	/usr/lib/x86_64-linux-gnu/libvtkRenderingPythonTkWidgets.so

    2.The imported target "vtk" references the file
   "/usr/bin/vtk" but this file does not exist.
	解决：
	sudo update-alternatives --install /usr/bin/vtk vtk /usr/bin/vtk6 10

***ubuntu一个小技巧
	例如，系统使用apt安装了pcl-1.7，自编译了pcl-1.9，cmake使用include_directories(${PCL_INCLUDE_DIRS})
	是会自动找pcl-1.7版本，将/usr/include下的pcl-1.9改名为pcl-1.7既可使用自编译版本的pcl，pcl-1.9需求
	c++14或更高的版本，CMakeLists.txt中加入set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c++14")
	std::auto_ptr在c++11以上已经弃用，单个所有权选择std::unique_ptr，需要复制指针选择std::shared_ptr，
	而pcl-1.7的{...}/pcl-1.7/pcl/visualization/cloud_viewer.h中使用了std::auto_ptr<CloudViewer_impl>
	impl_;编译时会出现警告，选择pcl-1.9或更高版本。

***pip install报错
	Could not install packages due to an EnvironmentError: Missing dependencies for SOCKS support.
	解决：
	    unset all_proxy
	    unset ALL_PROXY
	安装缺少依赖项：
	    pip install --user pysocks
	重置代理：
	    source ~/.bashrc

***ubuntu系统python版本
	修改/etc/alternatives路径中的python指向/usr/bin路径中的python对应版本
	安装pip3:sudo apt-get install python3-pip

***ubuntu安装talex
	1.选择安装Latex发行版
	sudo apt-get install texlive-full
	2.安装XeLaTex编译引擎
	sudo apt-get install texlive-xetex
	3.安装中文支持包
	sudo apt-get install texlive-lang-chinese
	4.安装图形化界面
	sudo apt-get install texstudio
	这里要注意，编译时需要设置编译器为XeLaTeX，TeXstudio中在Options->Configure TeXstudio->
	Build->Default Compiler中更改默认编译器为XeLaTeX即可。在配置中可以更改软件界面语言，
	将Options->Configure TeXstudio->General->Language更改为zh-CN即可将界面设置为中文。



***vim编辑器
   一般模式、编辑模式、命令行模式
   1. 模式之间的切换
	一般模式到编辑模式: i I(插入模式)   r R(替换模式)   (多余-->o O   a A)
	(i为目前光标所在处插入，I为在目前所在行的第一个非空格字符处插入;
	 r只替换光标所在那个字符一次，R会一直替换光标所在字符，直到按下Esc)
	编辑模式到一般模式: Esc
	一般模式到命令行模式: /  :  ?
	编辑模式与命令行模式之间不能互相切换
   2. 常用命令(一般模式下)
      移动光标：
	G(Shift+g): 移动到文件最后一行
	NG(n Shift+g): N代表数字，移动到文件第n行，
	gg: 移动到文件的第一行，相当于1G
	N Enter: N为数字，表示光标向下移动N行
      查找替换：
	/word: 向下查找一个名为word的字符串
	?word: 向上查找一个名为word的字符串
	:n1,n2s/word1/word2/g: 在第n1行与n2行之间寻找word1并将其替换为word2
	:1,$s/word1/word2/gc: 从第一行到最后一行寻找word1并将其替换为word2，替换之前显示提示是否替换当前字符
      删除、复制与粘贴：
	x,X: x-->del   X-->backspace
	dd: 删除光标所在一行
	ndd: 删除光标所在的向下n行，1dd相当与dd删除当前行
	yy: 复制光标所在的一行
	nyy: 复制光标所在的向下n行
	p,P: p为将已复制的内容在光标下一行粘贴，P则为上一行
	u: 复原前一个操作 
   3. vim功能
      a.块选择：
	v: 字符选择，会将光标经过的地方反白选择
	V: 行选择
	Ctrl+v: 块选择
	y: 复制反白的地方
	d: 删除反白的地方
      b.多文件编译：
	vim name1 name2 name3...
	:n: 编辑下一个文件
	:N: 编辑上一个文件
	:files: 列出目前vim打开的所有文件
      c. 多窗口功能：
	可以在一个窗口中打开多个文件，输入命令 :sp{filename}  如: :sp/etc/profile 即可在当前窗口打开profile
	Ctrl+w+j: 先按下Ctrl不放，再按下w后放开所有的按键，再按下j(或者向下的箭头键)，则光标可以移到下方的窗口
	Ctrl+w+k: 同上，移到上方窗口
   9. vim批量注释与取消注释
	注释：
		1.按v进入virtual模式
		2.上下键选中需要注释的行，光标在行首
		3.按Ctrl+v(win下Ctrl+q)进入列模式
		4.按大写I进入插入模式，输入注释符# / //，然后按下ESC两下即可
	反注释：
		Ctrl+v进入列选择模式，选中要删除的行首的注释符号，然后按d即可
   10. vim的配置文件位于/etc/vim/vimrc
		user$ sudo vim /etc/vim/vimrc
	在文件末尾添加：
		set number
		syntax on
		set cursorline
		set hlsearch


***处理Jupyter Notebook报错：IOPub data rate exceeded
	$ jupyter notebook --generate-config
	修改上诉命令生成文件中iopub_data_rate_limit所在行的限制
	$ c.NotebookApp.iopub_data_rate_limit = 10000000000000000000000000000000000000
	重启jupyter即可

***ubuntu搭建hadoop集群
	hadoop2.6+ubuntu16.04+jdk1.8.0_144
	此文档搭建三台计算机hadoop集群，hostname分别为wangzhongju-9527(master)、goldenridge(node1)、
	goldenridge-System-Product-Name(node2);
	tip: 以下用master、node1、node2代表hostname
   1.配置hosts文件
	user$ sudo vim /etc/hostname   找到每台机器的hostname
	user$ ifconfig		       找到 inet addr 对应的ip
	user$ sudo vim /etc/hosts      将三台机器的的ip与对应的hostname添加进文件
		上一步完成后可以在终端ping hostname，三台机器可以相互ping通
   2.建立hadoop运行帐号
	user$ sudo groupadd hadoop
	user$ sudo useradd -s /bin/bash -d /home/hduser -m hduser -g hadoop
		-s 指定用户登录后所使用的shell，
		-d 指定用户登录时的起始目录
		-m 自动创建用户的登录目录
		-g 指定用户所属的群组
	user$ sudo password hduser
	user$ sudo adduser hduser sudo
	user$ su hduser
   3.配置ssh免密码连入
	user$ dpkg --list | grep ssh   先确保机器都装了ssh
	user$ sudo apt-get install openssh-server   如果缺少opensh-server
	(1)此步仅在master机上进行
		hduser@master$ ssh-keygen -t rsa -P '' -f ~/.ssh/id_rsa  生成id_rsa和id_rsa.pub 公钥与私钥
		hduser@master$ cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys   将公钥加入已认证的key中
		hduser@master$ ssh localhost   第一次登录需要密码，exit后再登录不需要密码
	(2)此步在node1与node2上进行
		hduser@node$ scp hduser@master:~/.ssh/id_rsa.pub ~/.ssh/node_rsa.pub
		hduser@node$ cat ~/.ssh/node_rsa.pub ~/.ssh/authorized_keys
	(3)在master机上验证
		hduser@master$ ssh node1
   4.hadoop安装包
		hduser@master$ mkdir /home/hduser/local
	版本：Hadoop2.6.5  （下载地址：http://mirrors.hust.edu.cn/apache/hadoop/common/）
	下载完成后解压到/home/hduser/local，最终路径为/home/hduser/local/hadoop2.6.5
   5.jdk下载(java)
	user$ getconf LONG_BIT   查看系统位数
	下载地址：
	https://www.oracle.com/technetwork/java/javase/downloads/java-archive-javase8-2177648.html
	此处下载jdk1.8.0_144
	user$ sudo mv ~/Downloads/jdk1.8.0_144 /home/hduser/local
   6.配置环境
	user$ sudo vim /etc/profile
	在文件末尾添加：
		# jave_set
		export JAVA_HOME=/home/hduser/local/jdk1.8.0_144
		export HADOOP_HOME=/home/hduser/local/hadoop2.6.5
		export PATH=$PATH:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin:${JAVA_HOME}/bin
	user$ source /etc/profile
	配置软链接(此不可忽略)：
	sudo update-alternatives --install /usr/bin/java java /usr/lib/jvm/jdk1.8.0_144/bin/java 300
	sudo update-alternatives --install /usr/bin/javac javac /usr/lib/jvm/jdk1.8.0_144/bin/javac 300
	hduser@master$ java -version   测试是否成功
	hduser@master$ hadoop version
   7.配置~/hadoop2.6/etc/hadoop目录下的文件
	(1)hadoop-env.sh
		<configuration>
			export JAVA_HOME=/home/hduser/local/jdk1.8.0_144
		</configuration>
	(2)core-site.cml
		<configuration>
			<property>
				<name>fs.defaultFS</name>
				<value>hdfs://wangzhongju-9527:9000</value>
			</property>
			<property>
				<name>hadoop.tmp.dir</name>
				<value>/home/hduser/local/hadoop-2.6.5/tmp</value>
			</property>
			<property>
				<name>fs.trash.interval</name>
				<value>10080</value>
			</property>
		</configuration>	
	(3)hdfs-site.xml
		<configuration>
			<property>
				<name>dfs.namenode.secondary.http-address</name>
				<value>wangzhongju-9527</value>
			</property>
			<property>
				<name>dfs.replication</name>
				<value>3</value>
			</property>
			<property>
				<name>dfs.namenode.name.dir</name>
				<value>/home/hduser/local/hadoop-2.6.5/hdfs/name</value>
			</property>
			<property>
				<name>dfs.datanode.data.dir</name>
				<value>/home/hduser/local/hadoop-2.6.5/hdfs/data</value>
			</property>
		</configuration>
	(4)mapred-site.xml
		<configuration>
			<property>
				<name>mapreduce.framework.name</name>
				<value>yarn</value>
			</property>
		</configuration>
	(5)yarn-site.xml
		<configuration>

		<!-- Site specific YARN configuration properties -->
			<property>
				<name>yarn.nodemanager.aux-services</name>
				<value>mapreduce_shuffle</value>
			</property>
			<property>
				<name>yarn.resourcemanager.hostname</name>
				<value>wangzhongju-9527</value>
			</property>
		</configuration>
	(6)slaves
		localhost
		master
		node1
		node2
   8.格式化namenode并启动集群
	在master上：
	hduser@master:~/hadoop2.6$ hadoop namenode -format   格式化namenode
		(再次初始化需先清空dfs.namenode.name.dir配置的目录
			若datanode连接不上namenode，关闭防火墙)
	hduser@master:~/hadoop2.6$ ./sbin/start-all.sh	     启动集群
	hduser@master:~/hadoop2.6$ jps
	hduser@node:~/hadoop2.6$ jps
   9.浏览器可视化hadoop集群
	192.168.31.92:8088   192.168.31.92:50070
   10.测试hadoop集群
	hduser@master:~/local/hadoop-2.6.5$ ./bin/hdfs dfs -mkdir -p /data/input
	hduser@master:~/local/hadoop-2.6.5$ touch my_wordcount.txt
	hduser@master:~/local/hadoop-2.6.5$ vim my_wordcount.txt
	hduser@master:~/local/hadoop-2.6.5$ hdfs dfs -put my_wordcount.txt /data/input
	hduser@master:~/local/hadoop-2.6.5$ hdfs dfs -ls /data/input
		上一步会显示除刚创建的txt文件信息
	hduser@master:~/local/hadoop-2.6.5$ hadoop jar share/hadoop/mapreduce/hadoop-mapreduce-examples
			-2.6.5.jar wordcount /data/input/my_wordcount.txt /data/output/my_wordcount
	hduser@master:~/local/hadoop-2.6.5$ hdfs dfs -cat /data/output/my_wordcount/part-r-00000
		上一步会将txt文件中每个单词的个数进行统计，显示除统计结果，则hadoop分布式集群环境搭建成功
   11.关闭hadoop集群
	hduser@master:~/local/hadoop-2.6.5/sbin$ ./stop-all.sh

		启动集群后Live Nodes只有一个解决：
		jps子机没有DataNode节点，删除DataNode所有资料，即hdfs与tmp目录，重新格式化。
	

***ubuntu设置自定义终端显示
		user$ vim ~/.bashrc
	在case "$TERM" in一栏中，将PS1更改为：
		PS1="\[\e]0;\u@\h: \w\a\]${debian_chroot:+($debian_chroot)}\[
		\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$"
	PS1语法：
		修改颜色：\e[B;Fm    其中F为字体颜色，编号30~37，B为背景色，编号40~47。
		可通过 \e[0m 关闭颜色输出;特别的，当B为1时，将显示加亮加粗的文字，见下：
		字颜色：30黑 31红 32绿 33黄 34蓝 35紫 36深绿 37白
		字背景颜色：40黑 41深红 42绿 43黄 44蓝 45紫 46深绿 47白
		0关闭所有属性 1设置高亮度 4下划线 5闪烁 7反显 8消隐
		\u当前用户的账户名称 \h仅取主机的第一个名字 \w完整的工作目录名称家目录会以~代替
		

***keras设置多显卡训练keras-yolov3
	1.设置显示使用占比
		import tensorflow as tf
		config = tf.ConfigProto()
		config.gpu_options.per_process_gpu_memory_fraction = 0.8 #0.8代表GPU使用上限占比80%
		set_session(tf.Session(config=config))
	2.当指定单张GPU训练时，可使用os
		import os
		os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
		os.environ["CUDA_VISIBLE_DEVICES"] = "0"  #0代表使用gpu0训练
	3.使用多张GPU同时训练时，os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"不能到达目的
		from keras.utils import multi_gpu_model
		def _main():
			gpus = 2
			batch_size = 32
			model = Get_model(arg1,arg2,...)
			if gpus > 1:
				batch_size *= gpus
				model_multi = multi_gpu_model(model, gpus=gpus)
	(1)修改model.py最后一句
		return loss
	   为
		return K.expand_dims(loss, axis=0)
	(2)修改train.py中
		model.compile(optimizer=Adam(lr=1e-3),loss={'yolo_loss':lambda y_true,y_pred:y_pred})
		model.compile(optimizer=Adam(lr=1e-3),loss={'yolo_loss':lambda y_true,y_pred:y_pred[0]})
	tip：需要注意的是，使用多GPU训练网络时，权重保存需使用model.save_weights而不是使用
	     model_mutil.save_weights().


***python工程文件夹移动地址后运行报错


***anaconda
	打包环境:
		conda env list
		conda activate <envname>
		conda env export > <envname>.yaml
	安装打包的环境包:
		conda env create -f <envname>.yaml
	pytorch是否支持GPU加速:
		torch.cuda.is_available()
	anaconda中添加清华镜像源:(或直接在文件中添加 ~/.condarc)
		conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
		conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
		conda config --set show_channel_urls yes
		conda install pytorch torchvision cudatoolkit=10.0


***ubuntu更改显卡驱动
	执行update-initramfs报warning缺少相应.bin文件时，下载对应文件cp到地址，修改权限777：
	nvidia固件下载地址: https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/tree/i915
	方法1:
		sudo add-apt-repository ppa:graphics-drivers/ppa && sudo apt update
		System Settings->Software & Updates->Additiona Drivers 
		reboot
	方法2:
	     卸载所有安装的nvidia驱动:
		sudo apt-get purge nvidia*
		reboot
	     禁用nouveau驱动和相关的驱动包:
		sudo vim /etc/modprobe.d/blacklist.conf
	        添加:
		blacklist rivafb
		blacklist vga16fb
		blacklist nouveau
		blacklist nvidiafb
		blacklist rivatv
	     安装显卡驱动:官网下载对应版本.run文件
		sudo apt-get updata
		sudo apt-get install dkms build-essential linux-headers-generic
	        ctrl+alt+F1进入命令模式
		sudo service lightdm stop
		chmod 777 <name>.run
	        关闭X服务，禁用nouveau，不安装OpenGL
		sudo ./<name>.run –no-x-check –no-nouveau-check –no-opengl-files
		sudo update-initramfs -u
		sudo reboot
		nvidia-smi

***ubuntu在ROS中使用opencv与pcl
	1.安装ros(官网安装完整版)
	2.安装opencv、pcl
	3.创建ros工程文件夹:
		user$: mkdir -p {..workspace..}/ros_opencv/src && cd {...}/ros_opencv/src
		user$: catkin_create_pkg your_project_name std_msgs rospy roscpp
		user$: cd your_project_name/src
	4.将基于opencv的源码cpp文件写入该文件夹(例子见附录包)
	5.替换CMakeLists.txt和package.xml文件(见附录包)
	  文件中的工程名与源码cpp文件名对应更改
	6.编译
		user$: cd {..workspace..}/ros_opencv
		user$: catkin_make
		user$: source devel/setup.bash
	7.运行(节点名为例子中的设定)(每个终端中都应该source)
	  将roscore启动，然后发布节点，再订阅节点
		user$: roscore
		user$: rosrun opencv_test publish
		user$: rosrun opencv_test subscription


***ubuntu安装MATLAB R2017b Linux
	1.解压安装文件夹下的MATLABR2017b_Linux_Crack.rar与R2017b_glnxa64.zip(unzip解压报错可使用
	  windows系统解压)
	2.挂载镜像文件
		user$ mkdir {...}/temp
		user$ sudo mount -t auto -o loop R2017b_glnxa64.iso {...}/temp
	3.开始安装
		user$ cd {...}/temp
		user$ sudo ./install
	  选择使用文件安装密钥，密钥位于install_key文本文件，安装路径可自行选择，此处为
	  /home/wangzhongju/workspace/MATLAB_INSTALL。
	4.破解
	  前面解压好的MATLABR2017b_Linux_Crack文件夹中
		user$ cd {...}/MATLABR2017b_Linux_Crack
		user$ sudo cp license_standalone.lic /home/wangzhongju/workspace/MATLAB_INSTALL/licenses/
		user$ sudo cp libmwservices.so /home/wangzhongju/workspace/MATLAB_INSTALL/bin/glnxa64/
	5.取消挂载
		user$ sudo umount {...}/temp
	6.优化
		user$ sudo vim /etc/profile
	    添加 export PATH=$PATH:/home/wangzhongju/workspace/MATLAB_INSTALL/bin
		user$ sudo apt-get install matplot-support

***ubuntu外挂gps设备
	配置文件:/etc/udev/rules.d/99-slabs.rules

***ubuntu锁定软件不自动升级
	eg:锁定wps
	dpkg -l | grep wps	#找软件名字，得到wps-office
	sudo echo "wps-office hold" | sudo dpkg --set-selections  #锁定
	sudo dpkg --get-selection | grep hold	#出现wps
	后面使用sudo apt-get upgrade就不会升级wps了

***ubuntu安装搜狗输入法问题
	中文输入模式下回车键输入字母间距问题：全半角切换为半角模式
	输入过程中出现两个图标和输入框：
		sudo vim /etc/rc.local
	在exit 0 前添加代码：
		/bin/ps -ef | grep fcitx-qimpanel | grep -v grep | awk '{print $2}' | xargs kill -9



***ubuntu安装PlayOnLinux
	1.install latest version of wine
		sudo add-apt-repository ppa:ubuntu-wine/ppa
		sudo apt-get update
		sudo apt-get install wine:i386 winbend
	2.download playonlinux
		https://github.com/PlayOnLinux/POL-POM-4

***ctrl + z
	任务中止(即暂停),可以使用fg/bg继续前台或后台的任务,fg命令重新启动前台被中断的任务,bg命令把被中断的任务放在后台执行


***git
	1. git配置文件
		/etc/gitconfig: --system
		~/.gitconfig: --global
		{repo_name}/.git/config: 覆盖上层config
	2. git全局部署
		$ git config --global user.name "your name"
		$ git config --global user.name "your_email@xx.com"
	3. 本地创建ssh key
		$ ssh-keygen -t rsa -C "your_email@xx.com"

	4. github添加ssh key
		$ cat ~/.ssh/id_rsa.pub
	   copy the key in id_rsa.pub, github->Settings->SSH and GPG keys->New SSH key, paste
		$ ssh -T git@github.com
	   提示You’ve successfully authenticated, but GitHub does not provide shell access. OK
	5. 提交 上传
	   本地工程文件夹与github远程repo文件夹同名,此处设为test.
		$ git init
		$ git add .
		$ git commit -m "some descriptive words"

		$ git remote add origin git@github.com:wangzhongju/test.git
		($ git remote add origin https://github.com/wangzhongju/test.git)
		$ git push -u origin master
	   origin可以为任意名字,是远程仓库名
		$ git pull -u origin master  //从远程服务器更新到本地仓库





























	 




