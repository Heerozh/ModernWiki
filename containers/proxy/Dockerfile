FROM caddy:latest

RUN apk add --no-cache gettext

# Copy main Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Create directory for additional Caddyfile imports
RUN mkdir -p /etc/caddy/conf.d

# Expose port 80 443
EXPOSE 80
EXPOSE 443