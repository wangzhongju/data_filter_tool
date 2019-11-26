# requirement:


	opencv3    cuda9.0   python3	tensorflow_gpu>=1.14.0	pytorch>=1.1.0


#  build the project:


	mkdir build && cd build
	cmake ..
	make



# filter images:


	step1:
		put the tars of data into "./data/tar" file
	        furthermore, if your original data is a folder contained images, you just need put the folder into ./data/
		for example:
			if you have a folder named 'test' what contained some images, put folder 'test' into ./data
		    run:
			user$ bash run.sh ./data/test 
	step2:
		Run commond
			user$ bash run.sh parameter1 parameter2
		  parameter1: directory for stored results
		  parameter2: if your original data is just like '*.tar.gz', and run the program for the first time, untar
		      for example:
			user$ bash run.sh ./data/test1 untar
		      so if you change some paras and you want to filter images again, just do:
			user$ bash run.sh ./data/test1

	finally:
		available images located in:
			parameter1
			

# TIP:
	
	parameter1:
	    true: ./data/test1
	   false: ./data/test1/
