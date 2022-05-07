# Afarm Step function


## Notice
- yolo
  - It can track each grape, but grape looks similar
  - Therefore It just count number of images in one image
  - use "skip_frame" input variable how much image to ignore and not to track
- boxinst
  - If the grape's berry count is nder 3 berry, Ignore it
- rfr
  - save all of the each grape properties by csv file. Not only "thining or not" feature

## Position of Model 
- yolo : ```./deepsort/yolov5/```
- boxinst : ```./training_dir/BoxInst_MS_R_50_1x_sick4/```
- rfr : ```./grape_rfr/```


## Directory to save S3
() filetype, [] model
- grapes video (mp4) [start] -> ```grape_before/```
- each grape image (png) [yolo] ->  ```grape_before/${quality_id}/```
- each grape image after segmentation (png) [boxinst] -> ```public/result/```
- mask of each grape (pkl) [boxinst] -> ```mask/${quality_id}/```
- csv about mask and num of instances [boxinst] -> ```mask/```
- csv about feature of each grape [rfr] -> ```csv/```

## Input & Output of Each Step
### start
```json
{"quality_id": 91}
```
### yolo
``` json
[
    {
      "statusCode": 200,
      "quality_id": 91,
      "grape_id": 300,
      "body": "{\"quality_id\": 90}"
    },
    {
      "statusCode": 200,
      "log": "{\"msg\": \"empty\"}"
    }
  ]
```
### boxinst
```json 
{
    "statusCode": 200,
    "quality_id": 91, 
    "grape_id": "{\"start\": 301, \"end\": 334, \"count\": 34}"
}
```
### rfr
```json
{
    "statusCode": 200,
    "quality_id": 91, 
    "grape_id": "{\"start\": 301, \"end\": 334, \"count\": 34}"
}
```
### end



<br>

# TODO: Refactoring 
- filename column in csv to slice [26:]
- Difference of variable name between database and model
    |Korean|DB|Model|
    |---|---|---|
    |가지치기|pruning|thinning|
    |등급|maturity|grade|