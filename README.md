# Simple Flask App with HTTPS




# Flask server
Run it using `flask run -h localhost -p 6000` or using `gunicorn -b 0.0.0.0:6000 app:app --daemon` to run in background.


# Setup Caddy
Install caddy and run it as a systemctl

Sample caddy configuration (/etc/caddy/CaddyFile) assuming you have a domain `manojmanivannanserver.site`
```shell
ubuntu@manojm-server:~/flaskEdgeAPI$ cat /etc/caddy/Caddyfile
# The Caddyfile is an easy way to configure your Caddy web server.
#
# Unless the file starts with a global options block, the first
# uncommented line is always the address of your site.
#
# To use your own domain name (with automatic HTTPS), first make
# sure your domain's A/AAAA DNS records are properly pointed to
# this machine's public IP, then replace ":80" below with your
# domain name.

manojmanivannanserver.site {
        # Set this path to your site's directory.
        #root * /usr/share/caddy

        # Enable the static file server.
        #file_server

        # Another common task is to set up a reverse proxy:
        reverse_proxy localhost:6000

        # Or serve a PHP site through php-fpm:
        # php_fastcgi localhost:9000
}

# Refer to the Caddy docs for more information:
# https://caddyserver.com/docs/caddyfile
ubuntu@manojm-server:~/flaskEdgeAPI$
```