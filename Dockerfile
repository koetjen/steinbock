FROM ubuntu:20.04

ARG TZ=Europe/Zurich
ARG STEINBOCK_VERSION

ARG ILASTIK_BINARY=ilastik-1.3.3post3-Linux.tar.bz2
ARG CELLPROFILER_VERSION=v4.2.1
ARG CELLPROFILER_PLUGINS_VERSION=v4.2.1

ENV DEBIAN_FRONTEND=noninteractive PYTHONDONTWRITEBYTECODE="1" PYTHONUNBUFFERED="1"

RUN apt-get update && apt-get install -y build-essential git locales python3 python3-dev python3-venv curl

RUN sed -i -e 's/# en_US.UTF-8 UTF-8/en_US.UTF-8 UTF-8/' /etc/locale.gen && locale-gen
ENV LANG="en_US.UTF-8" LANGUAGE="en_US:en" LC_ALL="en_US.UTF-8"

RUN ln -snf "/usr/share/zoneinfo/${TZ}" /etc/localtime && echo "${TZ}" > /etc/timezone

RUN USER=steinbock && \
    GROUP=steinbock && \
    addgroup --gid 1000 "${GROUP}" && \
    adduser --uid 1000 --ingroup "${GROUP}" --disabled-password --gecos "" "${USER}" && \
    curl -SsL https://github.com/boxboat/fixuid/releases/download/v0.5.1/fixuid-0.5.1-linux-amd64.tar.gz | tar -C /usr/local/bin -xzf - && \
    chmod 4755 /usr/local/bin/fixuid && \
    mkdir -p /etc/fixuid && \
    printf "user: ${USER}\ngroup: ${GROUP}\n" > /etc/fixuid/config.yml

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"

RUN mkdir /data && \
    chown steinbock:steinbock /data && \
    chmod 666 /data

# ilastik

RUN mkdir /opt/ilastik && \
    curl -SsL "https://files.ilastik.org/${ILASTIK_BINARY}" | tar -C /opt/ilastik -xjf - --strip-components=1

# cellprofiler

RUN apt-get install -y default-libmysqlclient-dev libgtk-3-dev libnotify-dev libsdl2-dev openjdk-11-jdk-headless
ENV JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"
RUN curl -SsO https://extras.wxpython.org/wxPython4/extras/linux/gtk3/ubuntu-20.04/wxPython-4.1.0-cp38-cp38-linux_x86_64.whl && \
    pip install --upgrade numpy wheel wxPython-4.1.0-cp38-cp38-linux_x86_64.whl && \
    rm wxPython-4.1.0-cp38-cp38-linux_x86_64.whl
RUN git clone -b "${CELLPROFILER_VERSION}" --depth 1 https://github.com/CellProfiler/CellProfiler.git && \
    pip install --upgrade ./CellProfiler && \
    rm -r CellProfiler
RUN git clone -b "${CELLPROFILER_PLUGINS_VERSION}" --depth 1 https://github.com/BodenmillerGroup/ImcPluginsCP.git && \
    cp -r ImcPluginsCP/plugins /opt/cellprofiler_plugins && \
    rm -r ImcPluginsCP

# steinbock

COPY ./requirements.txt .
RUN pip install --upgrade deepcell==0.10.0 && \
    pip install --upgrade -r requirements.txt && \
    rm requirements.txt
ENV TF_CPP_MIN_LOG_LEVEL="2" NO_AT_BRIDGE="1"

RUN mkdir -p /opt/keras/models && \
    curl -SsL https://deepcell-data.s3-us-west-1.amazonaws.com/saved-models/MultiplexSegmentation-7.tar.gz | tar -C /opt/keras/models -xzf - && \
    rm /opt/keras/models/._MultiplexSegmentation

RUN mkdir /app
COPY . /app/steinbock
RUN SETUPTOOLS_SCM_PRETEND_VERSION="${STEINBOCK_VERSION#v}" pip install --upgrade -e /app/steinbock[IMC,DeepCell]

USER steinbock:steinbock
WORKDIR /data
ENTRYPOINT ["/app/steinbock/entrypoint.sh"]
