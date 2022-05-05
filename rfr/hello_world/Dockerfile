FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && yum install -y gcc gcc-c++ mesa-libGL which wget git tar

COPY . ./
RUN export $(cat .env | xargs) \
    && python3.9 -m pip install -r requirements.txt \
    && python3.9 -m pip install 'git+https://github.com/lazybuttrying/detectron2.git' \
    && wget https://modelfiles-bucket.s3.ap-northeast-2.amazonaws.com/regressor_model.pkl -P ./grape_rfr/

CMD ["app.lambda_handler"]