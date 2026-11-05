#!/usr/bin/env bash
# Instala OriginPass en una instancia Ubuntu 24.04 de EC2.
# PostgreSQL escucha solo en 127.0.0.1; gunicorn en 127.0.0.1:8000; nginx expone el 80.
# Uso (en la instancia): sudo bash instalar-ec2.sh <IP-o-DNS-publico> [rama]
# Ejemplo: sudo bash instalar-ec2.sh 54.12.34.56 main
# Clona el repositorio publico de GitHub; no necesita archivos locales.
set -euo pipefail

HOST_PUBLICO="${1:?Falta la IP o el DNS publico de la instancia}"
RAMA="${2:-main}"
REPO_URL="https://github.com/Pacha-e/OriginPass.git"
[[ "$(id -u)" -eq 0 ]] || { echo "Ejecuta con sudo"; exit 1; }

APP_DIR=/opt/originpass/app
VENV=/opt/originpass/venv
ENV_FILE=/etc/originpass.env
DB_NAME=originpass
DB_USER=originpass
DB_PASS="$(openssl rand -hex 24)"
SECRET="$(openssl rand -base64 48 | tr -d '\n')"

echo ">> Paquetes del sistema"
apt-get update -y
apt-get install -y git python3 python3-venv python3-pip postgresql nginx openssl curl

echo ">> PostgreSQL: rol y base de datos"
systemctl enable --now postgresql
sudo -u postgres psql -v ON_ERROR_STOP=1 <<SQL
DO \$\$ BEGIN
  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = '${DB_USER}') THEN
    CREATE ROLE ${DB_USER} LOGIN;
  END IF;
END \$\$;
ALTER ROLE ${DB_USER} WITH PASSWORD '${DB_PASS}';
SQL
if ! sudo -u postgres psql -tAc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1; then
  sudo -u postgres createdb -O "${DB_USER}" "${DB_NAME}"
fi

echo ">> Codigo y entorno virtual"
id -u originpass >/dev/null 2>&1 || useradd --system --home /opt/originpass --shell /usr/sbin/nologin originpass
rm -rf "$APP_DIR"
mkdir -p /opt/originpass
git clone --depth 1 --branch "$RAMA" "$REPO_URL" "$APP_DIR"
[[ -f "$APP_DIR/manage.py" ]] || { echo "El clon no contiene manage.py"; exit 1; }
python3 -m venv "$VENV"
"$VENV/bin/pip" install --upgrade pip
"$VENV/bin/pip" install -r "$APP_DIR/requirements.txt"

echo ">> Variables de entorno (solo root; sin comillas)"
umask 077
cat > "$ENV_FILE" <<EOF
DEBUG=0
SECRET_KEY=${SECRET}
ALLOWED_HOSTS=${HOST_PUBLICO},localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://${HOST_PUBLICO}
DATABASE_URL=postgresql://${DB_USER}:${DB_PASS}@127.0.0.1:5432/${DB_NAME}
EOF
chmod 600 "$ENV_FILE"
umask 022

echo ">> collectstatic y migraciones"
set -a
. "$ENV_FILE"
set +a
cd "$APP_DIR"
"$VENV/bin/python" manage.py collectstatic --noinput
"$VENV/bin/python" manage.py migrate --noinput
chown -R originpass:originpass /opt/originpass

echo ">> Servicio gunicorn (systemd)"
cat > /etc/systemd/system/originpass.service <<EOF
[Unit]
Description=OriginPass (gunicorn)
After=network.target postgresql.service

[Service]
User=originpass
Group=originpass
WorkingDirectory=${APP_DIR}
EnvironmentFile=${ENV_FILE}
ExecStart=${VENV}/bin/gunicorn --bind 127.0.0.1:8000 --workers 2 config.wsgi:application
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now originpass

echo ">> nginx en el puerto 80"
cat > /etc/nginx/sites-available/originpass <<'EOF'
server {
    listen 80 default_server;
    server_name _;
    client_max_body_size 10m;

    # Uploaded images: Django serves /media/ only with DEBUG on, so nginx does it.
    location /media/ {
        alias /opt/originpass/app/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/originpass /etc/nginx/sites-enabled/originpass
nginx -t
systemctl enable --now nginx
systemctl reload nginx

echo ">> Comprobacion local"
sleep 3
curl -fsS http://127.0.0.1/healthz/ && echo
echo "Listo. Abre http://${HOST_PUBLICO}/ desde tu PC. Contrasena de PostgreSQL solo en ${ENV_FILE}."
