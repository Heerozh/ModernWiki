FROM hugomods/hugo:git

# Create working directory
WORKDIR /src

# Copy build script
COPY build.sh /usr/local/bin/build.sh
RUN dos2unix /usr/local/bin/build.sh
RUN chmod +x /usr/local/bin/build.sh

# Default command
ENTRYPOINT ["/bin/sh", "/usr/local/bin/build.sh"]
