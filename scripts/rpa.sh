#!/bin/bash
# Uso: ./scripts/rpa.sh ["término de búsqueda"]
# Seguro de correr con `./rpa.sh`, `bash rpa.sh` o `. rpa.sh` (source): todo
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

run_rpa() {
  local IMAGE_NAME="${RPA_IMAGE_NAME:-prueba-tecnica-rpa}"
  local CONTAINER_NAME="${CONTAINER_NAME:-prueba-tecnica}"
  local PORT="${PORT:-8090}"
  local SEARCH_TERM="${1:-Python (programming language)}"
  local REPO_ROOT
  REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
  local inicio
  inicio="$(date '+%Y-%m-%d %H:%M:%S')"

  echo ""
  _hr "rpa.sh" "$MG"
  _c "$DM" "  Inicio  : $inicio"
  _c "$DM" "  Término : $SEARCH_TERM"
  echo ""

  _c "$CY" "==> Verificando que la app esté corriendo ('$CONTAINER_NAME')..."
  if [ -z "$(docker ps -q --filter "name=^${CONTAINER_NAME}$")" ]; then
    echo ""
    _hr "Resumen" "$MG"
    _c "$RD" "  La app no está corriendo."
    _c "$DM" "  Levántala primero con ./scripts/run.sh"
    _hr "" "$DM"
    return 1
  fi

  _c "$CY" "==> Construyendo imagen '$IMAGE_NAME' (usa caché si no cambió nada)..."
  if ! docker build -t "$IMAGE_NAME" "$REPO_ROOT/rpa"; then
    echo ""
    _hr "Resumen" "$MG"
    _c "$RD" "  Falló el build. Revisa el error de arriba."
    _hr "" "$DM"
    return 1
  fi

  _c "$CY" "==> Corriendo el scraper para: \"$SEARCH_TERM\""
  echo ""
  if docker run --rm --network host \
    -e "RPA_RESULTS_API_URL=http://localhost:${PORT}/api/v1/rpa/extractions" \
    -e "ASSISTANT_API_URL=http://localhost:${PORT}/api/v1/assistant/summarize" \
    "$IMAGE_NAME" python -m rpa.main "$SEARCH_TERM"; then
    echo ""
    _hr "Resumen" "$MG"
    _c "$GR" "  Extracción completada — revisa el dashboard para verla en vivo."
    _hr "" "$DM"
    return 0
  fi

  echo ""
  _hr "Resumen" "$MG"
  _c "$YL" "  El scraper terminó con error (ver log de arriba)."
  _c "$DM" "  La extracción puede haberse guardado igual, aunque el resumen de IA fallara."
  _hr "" "$DM"
  return 1
}

run_rpa "${1:-}"
