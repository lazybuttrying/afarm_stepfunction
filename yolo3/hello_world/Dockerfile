FROM public.ecr.aws/lambda/python:3.9

RUN yum update -y && yum install -y mesa-libGL tar git wget

COPY requirements.txt app.py /deepsort .env ./
RUN export $(cat .env | xargs) && python3.9 -m pip install -r requirements.txt

# Command can be overwritten by providing a different command in the template directly.
CMD ["app.lambda_handler"]