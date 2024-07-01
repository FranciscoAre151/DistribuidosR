FROM python:3.9

# Set the working directory inside the container
WORKDIR /P2Distribuidos

RUN pip install docker

# Copy the script into the container
COPY Servidor/servidor.py /P2Distribuidos/Servidor/servidor.py

EXPOSE 6004

CMD ["python", "Servidor/servidor.py"]
