Step1: configure experimental environments
	conda env create -f IDE.yml
------------------------------------------------------------------------------
Step2: coda activate IDE
------------------------------------------------------------------------------
Step3: run code 
         1)train:   
                 python  train_IDE_plus.py --gpu_ids 3 --name PersonX --train_all --batchsize 32  --data_dir ../dataset/personX/pytorch

 	* --name is the dir to save the trained model 
 	  --data_dir is the dir of training data
	------------------------------------------------------------------------------------------
         2)extract feature:
                  python  test_original.py  --name PersonX --cross  market.mat  --test_dir ../dataset/market/pytorch

 	* --name is the dir to load the trained model 
                  --cross is the name of feature 
 	  --tes_dir is the dir of testing data
	------------------------------------------------------------------------------------------
         3)test:
                  python  evaluate.py  --name PersonX --cross  market.mat   --logs_dir log/personx2market.txt

 	* --name is the dir to load the feature
                  --cross is the name of feature 
 	  --logs_dir is the dir to save the log
	------------------------------------------------------------------------------------------

------------------------------------------------------------------------------
Step4: traning and tesing on our first subset
         1)train:   
                 python  train_IDE_plus.py --gpu_ids 3 --name Example  --train_all --batchsize 32  --data_dir ../dataset/example1/pytorch_sp

 	* --name is the dir to save the trained model 
 	  --data_dir is the dir of training data
	------------------------------------------------------------------------------------------
         2)extract feature:
                  python  test_original.py  --name Example  --cross  example1.mat  --test_dir ../dataset/example1/pytorch_sp

 	* --name is the dir to load the trained model 
                  --cross is the name of feature 
 	  --tes_dir is the dir of testing data
	------------------------------------------------------------------------------------------
         3)test:
                  python  evaluate.py  --name Example  --cross  example1.mat --logs_dir log/test_on_subset1.txt

 	* --name is the dir to load the feature
                  --cross is the name of feature 
 	  --logs_dir is the dir to save the log
	------------------------------------------------------------------------------------------


* this example is training on personX and tesing on market dataset