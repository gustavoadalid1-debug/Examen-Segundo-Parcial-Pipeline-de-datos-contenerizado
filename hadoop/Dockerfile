# Imagen base: Ubuntu 22.04
FROM ubuntu:22.04

# Evita preguntas interactivas durante apt-get
ENV DEBIAN_FRONTEND=noninteractive

# Java 8 (lo requiere Hadoop), SSH (servidor y cliente), wget para descargar Hadoop y Python para el streaming
RUN apt-get update && apt-get install -y --no-install-recommends \
        openjdk-8-jdk-headless \
        openssh-server \
        openssh-client \
        wget \
        ca-certificates \
        python3 \
    && rm -rf /var/lib/apt/lists/*

# Variables de entorno de Java y Hadoop
ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HADOOP_VERSION=3.3.6
ENV HADOOP_HOME=/opt/hadoop
ENV PATH=$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin

# Descargar Hadoop, descomprimirlo en /opt y limpiar el tar.gz
RUN wget -q https://archive.apache.org/dist/hadoop/common/hadoop-${HADOOP_VERSION}/hadoop-${HADOOP_VERSION}.tar.gz \
    && tar -xzf hadoop-${HADOOP_VERSION}.tar.gz -C /opt \
    && mv /opt/hadoop-${HADOOP_VERSION} ${HADOOP_HOME} \
    && rm hadoop-${HADOOP_VERSION}.tar.gz

# Decirle a Hadoop dónde está Java (hadoop-env.sh)
RUN echo "export JAVA_HOME=${JAVA_HOME}" >> ${HADOOP_HOME}/etc/hadoop/hadoop-env.sh

# SSH sin contraseña: llave RSA sin passphrase, autorizada para el mismo usuario (root).
# Como todos los contenedores salen de esta imagen, comparten la llave y pueden
# entrar entre sí (ssh localhost y ssh <otro-contenedor>).
RUN mkdir -p /root/.ssh /var/run/sshd \
    && ssh-keygen -t rsa -b 4096 -N "" -f /root/.ssh/id_rsa \
    && cat /root/.ssh/id_rsa.pub >> /root/.ssh/authorized_keys \
    && chmod 700 /root/.ssh \
    && chmod 600 /root/.ssh/authorized_keys \
    && printf "Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n" > /root/.ssh/config \
    && chmod 600 /root/.ssh/config

# Permitir login de root solo con llave (sin contraseña)
RUN sed -i 's/^#\?PermitRootLogin.*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config \
    && sed -i 's/^#\?PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config

WORKDIR /root

# Arranca el servicio SSH y deja el contenedor vivo
CMD ["/bin/bash", "-c", "service ssh start && tail -f /dev/null"]
