# Afarm Step function


## Install
1. Docker : https://www.docker.com/products/docker-desktop/
2. AWS CLI : https://docs.aws.amazon.com/ko_kr/cli/latest/userguide/getting-started-install.html
3. AWS SAM CLI : https://docs.aws.amazon.com/ko_kr/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html
4. AWS Toolkit for VS Code (for Deploy) : https://docs.aws.amazon.com/toolkit-for-vscode/latest/userguide/setup-toolkit.html

## Run in Local
### Local Test
move to "hello_world" folder of each model
```bash
# Build
docker build -t {model_name} .

# Run
docker run --name {model_name} -it {model_name}
```
### Lambda Test on Local
move to location of template.yml of each model
```bash
# build
sam build

# test
sam local envoke -e events/qevents.json
```


## Architecture
<img width="477" alt="state_machine" src="https://user-images.githubusercontent.com/79500842/168296457-90fd322d-8a3d-4cf3-a7a7-3adda51e9398.png">

![Architecture](https://user-images.githubusercontent.com/79500842/169014560-bce64f7d-446a-4bb3-ad6e-33f33b2be650.png)


## Notice
- yolo
  - It can track each grape, but grape looks similar
  - Therefore It just count number of images in one image
  - use "skip_frame" input variable how much image to ignore and not to track
- boxinst
  - If the grape's berry count is under 3 berries, Ignore it
  - AWS Lambda failed when input was too much high resolution image
    - (Especially when size of one mask file is over 500MB) 
- rfr
  - save all of the each grape properties by csv file. Not only "thining or not" feature
- delete_boxinst_result
    - just delete past result in database and s3 bucket
    - to do not appear in user's grape_info page

## Position of Specific File 
### Model 
- Every model files can get by wget. I stored in my public S3 bucket. Look at each Dockerfile.
- yolo : ```./deepsort/yolov5/```
- boxinst : ```./training_dir/BoxInst_MS_R_50_1x_sick4/```
- rfr : ```./grape_rfr/```
### .env
- yolo : ```./yolo/hello_world/```
- boxinst : ```./boxinst/hello_world/```
- rfr : ```./rfr/hello_world/```


## S3 bucket
### Directory
```
.
├── csv
├── grape_before
│   └── {quality_id}
├── mask
│   └── {quality_id}
└── public
    ├── drone
    └── result
```

### Save path of each step
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
      "body": "{\"quality_id\": 91}"
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
- make new lambda function for new name "delete_boxinst_result"
    - have to delete other model's result too.
- Difference of variable name between database and model
    |Korean|DB|Model|
    |---|---|---|
    |가지치기|pruning|thinning|
    |등급|maturity|grade|
