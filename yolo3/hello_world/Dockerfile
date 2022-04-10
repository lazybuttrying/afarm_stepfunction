FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && yum install -y mesa-libGL tar git wget


COPY requirements.txt ./
RUN python3.9 -m pip install -r requirements.txt
#COPY ./deepsort/grape_demo.mp4 ./

COPY app.py /deepsort .env ./
RUN export $(cat .env | xargs)
# Command can be overwritten by providing a different command in the template directly.
RUN pwd
CMD ["app.lambda_handler"]