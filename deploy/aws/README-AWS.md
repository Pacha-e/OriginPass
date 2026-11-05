# Despliegue en AWS EC2 (AWS Academy Learner Lab)

Despliegue del entregable 4. Sustituye al despliegue de Azure, que se retiró.
Estado: **desplegado** el 5 de noviembre de 2026, con HTTPS (sección HTTPS). La dirección pública cambia si la instancia se detiene y se vuelve a iniciar; la vigente está en la sección "Entregable 4" del README.

## Arquitectura

- Una instancia EC2 con Ubuntu Server 26.04.1 LTS. El script de instalación se escribió para 24.04 y se instaló sin cambios en 26.04.1.
- nginx escucha en los puertos 80 y 443 y reenvía a gunicorn en `127.0.0.1:8000` (Django). El puerto 80 redirige a HTTPS.
- PostgreSQL local del paquete `postgresql` de Ubuntu 26.04, escuchando solo en `127.0.0.1`. No queda expuesto a Internet. Python es el `python3` del sistema. Versiones leídas en la instancia el 5 de noviembre de 2026 con `python3 --version; psql --version`: Python 3.14.4 y PostgreSQL 18.6.
- Código: clon público de este repositorio (rama `main`).
- HTTPS con un certificado de Let's Encrypt para el nombre sslip.io de la instancia.
- Archivos subidos (`media/`) en disco local de la instancia.

## 1. Especificaciones de la instancia

Consola EC2 → **Launch instance**.

| Campo | Valor |
|---|---|
| Name | `originpass-d4` |
| AMI | **Ubuntu Server 26.04 LTS** (se usó 26.04.1), 64-bit (x86) |
| Instance type | **t3.small** (2 GiB de RAM). Si no aparece, `t3.micro` (1 GiB) con swap (ver paso 4) |
| Key pair | **Proceed without a key pair.** El acceso se hace con EC2 Instance Connect desde la consola (paso 2) |
| Network / VPC | VPC por defecto |
| Subnet | Cualquier subred pública de la región |
| Auto-assign public IP | **Enable** |
| Security group | Nuevo, con las reglas de la tabla siguiente |
| Storage | **16 GiB gp3**, volumen raíz (mínimo 12) |
| IAM instance profile | No hace falta |
| User data | Vacío (la instalación se hace a mano, paso 3) |

Reglas de entrada del security group:

| Tipo | Protocolo | Puerto | Origen |
|---|---|---|---|
| SSH | TCP | 22 | **My IP** |
| HTTP | TCP | 80 | **Anywhere** (0.0.0.0/0) |

No abras 5432 ni 8000. No se usa 443 porque no hay HTTPS.

Región: la del lab (menú superior derecho de la consola). Anótala; debe coincidir en todo.

Cuando la instancia esté en `running`, anota su **Public IPv4 address** (por ejemplo `54.12.34.56`). Esa es `IP_PUBLICA` en los pasos siguientes.

## 2. Entrar por SSH

La instancia no tiene key pair, así que no hay SSH desde PowerShell. Usa la consola:

1. En EC2 → **Instances**, selecciona `originpass-d4`.
2. Pulsa **Connect → EC2 Instance Connect → Connect**. Se abre una terminal en el navegador, como usuario `ubuntu`.

Si la conexión falla con timeout, el security group no deja entrar el puerto 22 desde el servicio de la consola. Añade temporalmente una regla SSH 22 desde `0.0.0.0/0`, y **quítala** al terminar la instalación.

## 3. Instalar

Dentro de la instancia (sustituye `IP_PUBLICA`):

```bash
curl -fsSL https://raw.githubusercontent.com/Pacha-e/OriginPass/main/deploy/aws/instalar-ec2.sh -o instalar-ec2.sh
sudo bash instalar-ec2.sh IP_PUBLICA main
```

El script instala git, PostgreSQL, nginx y Python; clona el repositorio en `/opt/originpass/app`; crea la base y el usuario de PostgreSQL con contraseñas aleatorias; aplica migraciones; y arranca gunicorn y nginx. Termina con una comprobación local de `/healthz/`.

Las credenciales de la base quedan solo en `/etc/originpass.env` (permisos 600).

Si el script falla, el mensaje indica el paso. Corrige la causa y vuelve a ejecutarlo: es repetible.

## 4. Swap (solo si usas t3.micro)

Con 1 GiB de RAM la instalación puede agotar la memoria. Antes del paso 3:

```bash
sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
sudo mkswap /swapfile && sudo swapon /swapfile
```

## 5. Verificar

Desde tu PC, PowerShell:

```powershell
curl.exe -i http://IP_PUBLICA/healthz/
```

Debe responder `HTTP/1.1 200 OK` y contener `"status": "ok"`. Después, abre `http://IP_PUBLICA/` en el navegador.

Si falla, dentro de la instancia:

```bash
sudo systemctl status originpass --no-pager
sudo journalctl -u originpass -n 50 --no-pager
sudo tail -n 30 /var/log/nginx/error.log
```

## 6. Cuenta de administración

El sitio arranca sin usuarios. Crea un administrador desde la instancia:

```bash
sudo bash -c 'set -a; . /etc/originpass.env; set +a; cd /opt/originpass/app && /opt/originpass/venv/bin/python manage.py createsuperuser'
```

## HTTPS

Instalado el 5 de noviembre de 2026 con Let's Encrypt, en `https://44-206-186-9.sslip.io`.

1. En el security group, agrega **HTTPS (443)** con origen **Anywhere-IPv4**.
2. `sudo apt-get install -y certbot python3-certbot-nginx`
3. `sudo certbot --nginx -d 44-206-186-9.sslip.io --redirect -m TU_CORREO --agree-tos --no-eff-email`. El `--redirect` manda el HTTP a HTTPS. El certificado vence el 3 de febrero de 2027; la renovación es automática.
4. En `/etc/originpass.env`, `ALLOWED_HOSTS` incluye el nombre, `CSRF_TRUSTED_ORIGINS=https://44-206-186-9.sslip.io`, y se añaden `BEHIND_TLS_PROXY=1`, `SESSION_COOKIE_SECURE=1` y `CSRF_COOKIE_SECURE=1`.
5. `sudo systemctl restart originpass`

Los QR impresos deben apuntar a la dirección HTTPS. Los QR antiguos con la IP siguen funcionando por redirección, pero el certificado no cubre la IP y el navegador mostraría una advertencia.

## Actualizar el servidor

La primera vez, trae el script nuevo:

```bash
sudo -u originpass git -C /opt/originpass/app pull --ff-only
```

Después, en cada actualización:

```bash
sudo bash /opt/originpass/app/deploy/aws/actualizar-ec2.sh 44-206-186-9.sslip.io
```

El script instala dependencias, aplica migraciones, copia los archivos estáticos, reinicia el servicio y comprueba `/healthz/` por HTTPS con el certificado validado. Si un paso falla, se detiene.

## Datos de demostración

Se cargaron una vez con `seed_demo`, con `DEBUG=1` solo para ese comando. Las cuentas de demostración comparten una contraseña conocida. Esa decisión es del responsable del proyecto para la demostración en clase, no una práctica de producción.

## Limitaciones conocidas

- **Elastic IP.** Desde el 5 de noviembre de 2026 la instancia tiene la Elastic IP `44.206.186.9`, así que la dirección no cambia al parar y arrancar la instancia. Consume algo del presupuesto del lab, también con la instancia detenida. Si alguna vez cambia la IP, cambia con ella el nombre sslip.io: hay que emitir el certificado para el nombre nuevo (sección HTTPS, paso 3), poner el nombre nuevo en `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` de `/etc/originpass.env`, ejecutar `actualizar-ec2.sh` con el nombre nuevo y volver a exportar los QR, que llevan la dirección dentro.
- **Sin copia de seguridad.** La base de datos y `media/` viven en el disco de la instancia; terminarla los borra.
- **Correo sin SMTP.** Las notificaciones y el enlace de restablecimiento de contraseña no salen de la instancia mientras no se configure `EMAIL_BACKEND` con un servicio SMTP.
- **Región de los escaneos.** Sin un CDN delante, `TRUST_GEO_HEADERS` queda apagado: los escaneos nuevos no registran región y la alerta de copia no se dispara. La alerta que se ve en el panel viene de los datos de demostración.
- **No volver a ejecutar `instalar-ec2.sh`** sobre una instancia con datos: genera una `SECRET_KEY` nueva y las firmas existentes dejarían de validar. Para actualizar, `actualizar-ec2.sh`.

## Coste y limpieza

- El Learner Lab tiene presupuesto limitado. Al terminar la demostración, **termina la instancia** (Instance state → Terminate). Terminar borra el disco.
- Al cerrar el lab, las instancias se detienen. Al volver a abrirlo, la IP puede cambiar.
