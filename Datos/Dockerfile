FROM python:3.9

# Set the working directory inside the container
WORKDIR /P2Distribuidos

# Install tzdata to set the timezone
RUN apt-get update && apt-get install -y tzdata

# Set the timezone to America/Argentina/Buenos_Aires
RUN ln -sf /usr/share/zoneinfo/America/Argentina/Buenos_Aires /etc/localtime && \
    echo "America/Argentina/Buenos_Aires" > /etc/timezone

# Copy the script into the container
COPY Datos/datos.py /P2Distribuidos/Datos/datos.py

EXPOSE 6000

CMD ["python", "Datos/datos.py"]
