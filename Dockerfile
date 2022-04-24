FROM python:latest

RUN apt-get update && apt-get install -y python3-opencv

WORKDIR /home/app/code

ADD requirements.txt ./

RUN pip install -r requirements.txt

COPY . ./

RUN mkdir "tmp"
RUN mkdir "tmp/downloadable_files"
RUN mkdir "tmp/uploaded_files"

CMD ["sh", "run.sh"]
