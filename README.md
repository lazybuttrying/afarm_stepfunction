# Afarm Step function


### Notice
- yolo
  - It can track each grape, but grape looks similar
  - Therefore It just count number of images in one image
  - use "skip_frame" input variable how much image to ignore and not to track
- boxinst
  - If the grape's berry count is nder 3 berry, ignore it
- rfr
  - save all of the each grape properties by csv file. not only "thining or not" feature


### Input & Output of each model
- yolo
  - input :
  - output :
- boxinst
  - input :
  - output :
- rfr
  - input :
  - output :
  
  
### Position of Model 
- yolo : ./deepsort/yolov5/
- boxinst : ./training_dir/BoxInst_MS_R_50_1x_sick4/
- rfr : ./grape_rfr/
