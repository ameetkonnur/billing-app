FROM ameetk/azure-billing-alerts-app

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd

EXPOSE 8088
EXPOSE 2222

#!/bin/bash
RUN service ssh start

RUN cd /
RUN cd code
RUN git init
RUN git pull https://github.com/ameetkonnur/billing-app
COPY init_container.sh /opt/startup
RUN chmod 755 /opt/startup/init_container.sh
RUN superset init
ENTRYPOINT ["/opt/startup/init_container.sh"]
