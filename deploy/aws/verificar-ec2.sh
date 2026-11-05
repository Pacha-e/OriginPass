#!/usr/bin/env bash
# Comprueba desde fuera la instancia: /healthz/ debe devolver 200 con "status": "ok".
# Uso: bash deploy/aws/verificar-ec2.sh <IP-o-DNS-publico>
set -uo pipefail

HOST_PUBLICO="${1:?Falta la IP o el DNS publico}"
fallos=0

comprobar() {
  local ruta="$1" patron="$2" cuerpo codigo
  cuerpo="$(curl -s -m 30 -w '\n%{http_code}' "http://${HOST_PUBLICO}${ruta}")" || cuerpo=$'\n000'
  codigo="${cuerpo##*$'\n'}"
  cuerpo="${cuerpo%$'\n'*}"
  if [[ "$codigo" == "200" ]] && { [[ -z "$patron" ]] || grep -Eq "$patron" <<<"$cuerpo"; }; then
    echo "OK    ${codigo} ${ruta}"
  else
    echo "FALLO ${codigo} ${ruta}"
    fallos=$((fallos + 1))
  fi
}

comprobar "/healthz/" '"status"[[:space:]]*:[[:space:]]*"ok"'
comprobar "/" ""
comprobar "/static/favicon.svg" ""

if (( fallos > 0 )); then
  echo "Verificacion fallida: ${fallos} comprobacion(es)."
  exit 1
fi
echo "Verificacion correcta."
