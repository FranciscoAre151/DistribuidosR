FROM python:3.9

# Set the working directory inside the container
WORKDIR /P2Distribuidos

# Instalar el paquete 'tabulate'
RUN pip install --no-cache-dir tabulate

# Copy the script into the container
COPY Miembro2/miembro2.py /P2Distribuidos/Miembro2/miembro2.py

EXPOSE 6002

CMD ["python", "Miembro2/miembro2.py"]
