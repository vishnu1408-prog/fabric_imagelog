FROM ubuntu:20.04
ENV DEBIAN_FRONTEND noninteractive
RUN apt update && apt install -y python3 && apt install -y python3-pip && pip3 install --upgrade pip
RUN mkdir /install
COPY ./requirements.txt /install
RUN pip3 install --upgrade sentry-sdk
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip3 install -r /install/requirements.txt 
RUN pip3 install matplotlib
RUN pip3 install opencv-python
RUN apt update
RUN apt install unzip
RUN apt-get update && apt-get install -y wkhtmltopdf

# Set the timezone to Asia/Kolkata
ENV TZ=Asia/Kolkata

# Update the package list and install tzdata
RUN apt-get update && apt-get install -y tzdata

# Configure the timezone
RUN ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && dpkg-reconfigure -f noninteractive tzdata




