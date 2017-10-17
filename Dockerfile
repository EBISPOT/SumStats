FROM hdfgroup/h5py:2.7.0


# Copy the application folder inside the container
COPY sumstats /application/sumstats
COPY setup.py /application/
#COPY config.yml /application/

RUN pip install /application/ 
#RUN pip install -r /application/sumstats/server/requirements.txt

# Expose ports
#EXPOSE 8080

# Set the default directory where CMD will execute
WORKDIR /application

# Set the default command to execute
# when creating a new container
#CMD python -m sumstats.server.server
CMD python sumstats/run.py

