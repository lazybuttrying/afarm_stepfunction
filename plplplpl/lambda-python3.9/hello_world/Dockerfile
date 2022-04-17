
FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && yum install -y gcc gcc-c++ mesa-libGL which wget git tar

COPY .env app.py requirements.txt ./
RUN python3.9 -m pip install -r requirements.txt 

RUN python3.9 -m pip install 'git+https://github.com/lazybuttrying/detectron2.git'

COPY ./box  ./box
WORKDIR box
RUN python3.9 setup.py build develop
#RUN wget -P ./training_dir/BoxInst_MS_R_50_1x/ https://modelfiles-bucket.s3.ap-northeast-2.amazonaws.com/model_final.pth
# Command can be overwritten by providing a different command in the template directly.

#RUN pwd && pwd
WORKDIR ../
RUN export $(cat .env | xargs)

CMD ["app.lambda_handler"]