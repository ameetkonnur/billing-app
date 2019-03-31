FROM ameetk/azure-usage-superset:v2

# ssh
ENV SSH_PASSWD "root:Docker!"
RUN apt-get update \
        && apt-get install -y --no-install-recommends dialog \
        && apt-get update \
    && apt-get install -y --no-install-recommends openssh-server \
    && echo "$SSH_PASSWD" | chpasswd

EXPOSE 8088 2222

RUN cd /
RUN mkdir my-app-code
WORKDIR /my-app-code
RUN git clone https://github.com/ameetkonnur/billing-app
WORKDIR /my-app-code/billing-app
RUN cp sshd_config /etc/ssh/
RUN cp init-container.sh /usr/local/bin/
RUN chmod u+x /usr/local/bin/init-container.sh
ENTRYPOINT ["/usr/local/bin/init-container.sh"]