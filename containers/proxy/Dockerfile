FROM caddy:latest

# Copy main Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Create directory for additional Caddyfile imports
RUN mkdir -p /etc/caddy/conf.d

# Expose port 80
EXPOSE 80