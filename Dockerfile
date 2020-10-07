FROM arm32v7/python:rc-buster

ENV INSTALL_KEY=379CE192D401AB61
ENV DEB_DISTRO=buster

RUN apt update && apt-get install gnupg1 apt-transport-https dirmngr -y
RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys $INSTALL_KEY
RUN echo "deb https://ookla.bintray.com/debian ${DEB_DISTRO} main" | tee  /etc/apt/sources.list.d/speedtest.list
RUN apt-get update && apt-get install speedtest

ENV DASH_DEBUG_MODE True

RUN set -ex && \
    pip install dash dash-daq dash-bootstrap-components

EXPOSE 8050

COPY ./app /app

WORKDIR /app

CMD ["python", "app.py"]
