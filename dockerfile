FROM python:3.11

RUN sudo apt-get install portaudio19-dev

WORKDIR /
ADD . /

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 80

ENV NAME World

CMD [ "python" , "sender.py" ]