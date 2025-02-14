# Use Ruby as the base image since Pact Broker is a Ruby application
FROM ruby:3.2

# Set environment variables
ENV PACT_BROKER_DATABASE_ADAPTER=postgres \
    PACT_BROKER_PORT=9292

# Install required dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev 

# Create a working directory
WORKDIR /app

# Install Pact Broker
RUN gem install pact_broker -v 2.111.0

# Expose Pact Broker port
EXPOSE 9292

# Start the Pact Broker server
CMD ["pact-broker", "start", "-p", "9292", "--host", "0.0.0.0"]

