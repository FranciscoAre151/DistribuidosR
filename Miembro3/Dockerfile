FROM python:3.9

# Set the working directory inside the container
WORKDIR /P2Distribuidos

# Instalar el paquete 'tabulate'
RUN pip install --no-cache-dir tabulate

# Copy the script into the container
COPY Miembro3/miembro3.py /P2Distribuidos/Miembro3/miembro3.py

EXPOSE 6003

CMD ["python", "Miembro3/miembro3.py"]
