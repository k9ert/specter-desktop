FROM python:3.8

RUN apt-get update && apt-get install -y libusb-1.0-0-dev libudev-dev

WORKDIR /usr/src/app 
ENV PYTHONUNBUFFERED 1
ENV PORT 8080
EXPOSE 8080
COPY requirements.txt . 
RUN pip install -r requirements.txt
COPY . .
RUN pip install -e .
# Remark: The port is specified in GCR via the PORT env-var.
# This is already implemented in specter
# https://github.com/ahmetb/cloud-run-faq#how-do-i-make-my-web-application-compatible-with-cloud-run
CMD [ "python3", "-m" , "cryptoadvance.specter", "server", "--host=0.0.0.0" ]