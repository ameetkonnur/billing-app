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
RUN chmod 755 init_container.sh
ENTRYPOINT ["/code/init_container.sh"]