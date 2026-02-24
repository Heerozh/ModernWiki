FROM hugomods/hugo:git

# Install SSH client for cloning git@... repositories
RUN apk update && apk --no-cache upgrade
RUN apk add --no-cache openssh-client
RUN apk add --no-cache python3

# Create working directory
WORKDIR /src

# Copy build script
COPY build.sh /usr/local/bin/build.sh
RUN dos2unix /usr/local/bin/build.sh
RUN chmod +x /usr/local/bin/build.sh

# Default command
ENTRYPOINT ["/bin/sh", "/usr/local/bin/build.sh"]
