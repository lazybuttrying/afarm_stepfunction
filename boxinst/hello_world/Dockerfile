FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && yum install -y gcc gcc-c++ mesa-libGL which wget git tar

COPY .env app.py requirements.txt ./upload ./
RUN export $(cat .env | xargs) && python3.9 -m pip install -r requirements.txt  && python3.9 -m pip install 'git+https://github.com/lazybuttrying/detectron2.git'

COPY ./box  ./box
WORKDIR box

RUN wget https://modelfiles-bucket.s3.ap-northeast-2.amazonaws.com/model_0059999.pth -P ./training_dir/BoxInst_MS_R_50_1x_sick4/ \
    && python3.9 setup.py build develop

WORKDIR ../
CMD ["app.lambda_handler"]