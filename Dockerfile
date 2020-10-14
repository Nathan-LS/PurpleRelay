FROM fedora:32
LABEL maintainer="nathan@nathan-s.com"
LABEL url="https://github.com/Nathan-LS/PurpleRelay"

ENV PYTHONUNBUFFERED=1

RUN dnf install -y coreutils

RUN dnf install -y python38
#dependencies for pygobject
RUN dnf install -y gcc gobject-introspection-devel cairo-devel pkg-config python3-devel gtk3
# pip3 requirements for install
RUN dnf install -y cairo-gobject-devel
# finch
RUN dnf install -y finch
#plugins
RUN dnf install -y purple-discord pidgin-discord

RUN dnf install -y screen dbus-x11 nano
RUN dnf clean all

RUN groupadd -g 1007 purplerelay
RUN useradd --system --shell /bin/bash --home /app -u 1006 -g purplerelay purplerelay

USER root
WORKDIR /opt
COPY ./ /opt/PurpleRelay/
RUN find /opt/PurpleRelay -type f -exec chmod 0640 {} \;
RUN find /opt/PurpleRelay -type d -exec chmod 0750 {} \;
RUN chmod 0500 /opt/PurpleRelay/DockerEntry.sh
RUN mkdir /app /app/.purple
RUN chmod 0700 /app/.purple
RUN chown purplerelay:purplerelay /opt/PurpleRelay /app -R

USER purplerelay
WORKDIR /opt/PurpleRelay
RUN pip3 install --user -r requirements.txt
WORKDIR /app
ENTRYPOINT ["/opt/PurpleRelay/DockerEntry.sh"]
CMD ["python3.8", "/opt/PurpleRelay/PurpleRelay"]