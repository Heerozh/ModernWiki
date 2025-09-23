FROM hugomods/hugo:latest

# Install git
RUN apk add --no-cache git

# Create working directory
WORKDIR /src

# Copy build script
COPY build.sh /usr/local/bin/build.sh
RUN chmod +x /usr/local/bin/build.sh

# Default command
CMD ["/usr/local/bin/build.sh"]