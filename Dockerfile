FROM python:3.9
ENV PYTHONBUFFERED 1
ENV SKLEARN_ALLOW_DEPRECATED_SKLEARN_PACKAGE_INSTALL True
WORKDIR /analytics

RUN apt-get update \
    && apt-get install -y iputils-ping \
    && apt-get install -y ffmpeg

COPY . /analytics
RUN python3 -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 manage.py collectstatic --no-input
CMD ["bash", "-c", "python3 manage.py migrate"]
