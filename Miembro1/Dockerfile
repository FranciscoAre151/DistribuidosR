FROM python:3.9

# Set the working directory inside the container
WORKDIR /P2Distribuidos

# Instalar el paquete 'tabulate'
RUN pip install --no-cache-dir tabulate

# Copy the script into the container
COPY Miembro1/miembro1.py /P2Distribuidos/Miembro1/miembro1.py

EXPOSE 6001

CMD ["python", "Miembro1/miembro1.py"]

