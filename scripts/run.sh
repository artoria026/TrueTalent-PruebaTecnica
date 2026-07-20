#!/bin/bash
# Seguro de correr con `./run.sh`, `bash run.sh` o `. run.sh` (source): todo
# vive en una función y usa `return`, nunca `exit`.
set -uo pipefail

R='\033[0m'
CY='\033[36m'
MG='\033[35m'
GR='\033[32m'
YL='\033[33m'
RD='\033[31m'
DM='\033[2m'

_c() { printf '%b%s%b\n' "$1" "$2" "$R"; }

_hr() {
  local titulo="${1:-}" color="${2:-$DM}" width=64
  if [ -n "$titulo" ]; then
    local resto=$(( width - ${#titulo} - 4 ))
    (( resto < 0 )) && resto=0
    printf '%b── %s %s%b\n' "$color" "$titulo" "$(printf '─%.0s' $(seq 1 "$resto"))" "$R"
  else
    printf '%b%s%b\n' "$color" "$(printf '─%.0s' $(seq 1 "$width"))" "$R"
  fi
}

run_all() {
  local IMAGE_NAME="${IMAGE_NAME:-prueba-tecnica}"
  local CONTAINER_NAME="${CONTAINER_NAME:-prueba-tecnica}"
  local PORT="${PORT:-8090}"
  local REPO_ROOT
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  local inicio
  inicio="$(date '+%Y-%m-%d %H:%M:%S')"

  echo ""
  _hr "run.sh" "$MG"
  _c "$DM" "  Inicio  : $inicio"
  _c "$DM" "  Imagen  : $IMAGE_NAME"
  _c "$DM" "  Puerto  : $PORT"
  echo ""

  _c "$CY" "==> Eliminando contenedor previo '$CONTAINER_NAME' (si existe)..."
  docker rm -f "$CONTAINER_NAME" >/dev/null 2>&1 || true

  _c "$CY" "==> Verificando si el puerto $PORT está ocupado..."

  local OTHER_CONTAINERS
  OTHER_CONTAINERS="$(docker ps -q --filter "publish=$PORT" 2>/dev/null || true)"
  if [ -n "$OTHER_CONTAINERS" ]; then
    _c "$YL" "    Contenedor(es) usando el puerto $PORT, cerrando: $OTHER_CONTAINERS"
    docker rm -f $OTHER_CONTAINERS >/dev/null 2>&1 || true
  fi

  if command -v fuser >/dev/null 2>&1; then
    fuser -k "${PORT}/tcp" >/dev/null 2>&1 || true
  fi

  _c "$CY" "==> Construyendo imagen '$IMAGE_NAME'..."
  if ! docker build -f "$REPO_ROOT/Dockerfile.allinone" -t "$IMAGE_NAME" "$REPO_ROOT"; then
    echo ""
    _hr "Resumen" "$MG"
    _c "$RD" "  Falló el build. Revisa el error de arriba."
    _hr "" "$DM"
    return 1
  fi

  local ENV_FILE_ARGS=()
  if [ -f "$REPO_ROOT/.env" ]; then
    _c "$DM" "==> Encontrado .env local, se pasará al contenedor (no se commitea)."
    ENV_FILE_ARGS=(--env-file "$REPO_ROOT/.env")
  fi

  _c "$CY" "==> Levantando contenedor '$CONTAINER_NAME' en el puerto $PORT..."
  if ! docker run -d --name "$CONTAINER_NAME" -p "${PORT}:8000" "${ENV_FILE_ARGS[@]}" "$IMAGE_NAME" >/dev/null; then
    echo ""
    _hr "Resumen" "$MG"
    _c "$RD" "  Falló al levantar el contenedor. Revisa el error de arriba."
    _hr "" "$DM"
    return 1
  fi

  _c "$CY" "==> Esperando a que la app esté healthy..."
  local STATUS="starting"
  local i
  for i in $(seq 1 30); do
    STATUS="$(docker inspect --format='{{.State.Health.Status}}' "$CONTAINER_NAME" 2>/dev/null || echo starting)"
    if [ "$STATUS" = "healthy" ]; then
      break
    fi
    sleep 1
  done

  echo ""
  _hr "Resumen" "$MG"
  if [ "$STATUS" = "healthy" ]; then
    _c "$GR" "  Estado : healthy"
    _c "$GR" "  Lista  : http://localhost:${PORT}  (docs: http://localhost:${PORT}/docs)"
    _hr "" "$DM"
    return 0
  fi

  _c "$RD" "  Estado : no confirmó 'healthy' tras 30s"
  _c "$DM" "  Revisa : docker logs $CONTAINER_NAME"
  _hr "" "$DM"
  return 1
}

run_all
