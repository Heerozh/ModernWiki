FROM caddy:latest

RUN apk add --no-cache gettext

# Copy main Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile.template

# Create directory for additional Caddyfile imports
RUN mkdir -p /etc/caddy/conf.d

# Expose port 80 443
EXPOSE 80
EXPOSE 443

CMD ["/bin/sh", "-c", "envsubst < /etc/caddy/Caddyfile.template > /etc/caddy/Caddyfile && caddy run --config /etc/caddy/Caddyfile --adapter caddyfile"]