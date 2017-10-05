FROM hdfgroup/h5py:2.7.0


# Copy the application folder inside the container
COPY sumstats /sumstats

RUN pip install -r /sumstats/server/requirements.txt

# Expose ports
EXPOSE 8080

# Set the default directory where CMD will execute
WORKDIR /

# Set the default command to execute
# when creating a new container
# i.e. using CherryPy to serve the application
CMD python -m sumstats.server.server


