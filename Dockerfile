FROM python:latest

RUN apt-get update && apt-get install -y python3-opencv && apt-get install -y git

WORKDIR /home/app/code

RUN mkdir "tmp"
RUN mkdir "tmp/downloadable_files"
RUN mkdir "tmp/uploaded_files"

WORKDIR 'lib'
RUN git clone https://github.com/pjreddie/darknet
WORKDIR 'darknet'
RUN make

WORKDIR /home/app/code
COPY yolov3.weights lib/darknet

ADD requirements.txt ./
RUN pip install -r requirements.txt

COPY . ./

CMD ["sh", "run.sh"]
