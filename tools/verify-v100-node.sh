#!/usr/bin/env bash
# verify-v100-node.sh — приёмка узла 4×V100 SXM2 до установки движка.
# Использование: ./verify-v100-node.sh [--min-links 24]
# Коды выхода: 0 — всё сходится; 1 — есть отказы; 2 — нет окружения (не тот хост).
set -uo pipefail
MIN_LINKS=${2:-24}
[ "${1:-}" = "--min-links" ] || MIN_LINKS=24
fail=0
ok()   { printf '  \033[32mOK\033[0m   %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m %s\n' "$*"; fail=1; }
warn() { printf '  \033[33mWARN\033[0m %s\n' "$*"; }

command -v nvidia-smi >/dev/null 2>&1 || { echo "nvidia-smi не найден — это не GPU-узел или нет драйвера"; exit 2; }

echo "== 1. Карты =="
n_gpu=$(nvidia-smi -L 2>/dev/null | grep -c '^GPU ')
[ "$n_gpu" -eq 4 ] && ok "4 GPU видны" || bad "видно GPU: $n_gpu (нужно 4)"
if nvidia-smi -L | grep -q 'V100-SXM2-32GB'; then ok "модель V100-SXM2-32GB"; else warn "модель не та, что ждём: $(nvidia-smi --query-gpu=name --format=csv,noheader | head -1)"; fi

echo "== 2. NVLink =="
if nvidia-smi nvlink --status >/dev/null 2>&1; then
  total=$(nvidia-smi nvlink --status | grep -c 'Link ')
  active=$(nvidia-smi nvlink --status | grep -c 'Active')
  [ "$active" -ge "$MIN_LINKS" ] && [ "$total" -eq "$active" ] \
    && ok "линки: $active/$total Active" \
    || bad "линки: $active Active из $total (нужно $MIN_LINKS+, и все активные)"
  [ "$(nvidia-smi nvlink --status | grep -ci 'inactive')" -gt 0 ] && \
    warn "есть неактивные линки: ослабить 16 центральных винтов на 2 оборота и проверить светодиоды прижима"
else
  bad "nvlink-отчёта нет: либо не SXM2-модуль, либо драйвер без NVLink"
fi

echo "== 3. Топология =="
topo=$(nvidia-smi topo -m 2>/dev/null)
if echo "$topo" | grep -qE 'SYS|PHB'; then
  bad "в topo -m есть SYS/PHB: часть связей идёт через хост, NVLink неполный"
  echo "$topo" | sed 's/^/       /'
else
  ok "все пары GPU — через NVLink"
fi

echo "== 4. Счётчики ошибок NVLink (должны быть нули) =="
if errs=$(nvidia-smi nvlink -e 2>/dev/null); then
  bad_lines=$(echo "$errs" | grep -E 'Errors' | grep -vE ':\s*0\s*$' || true)
  [ -z "$bad_lines" ] && ok "счётчики чистые" || { bad "ненулевые счётчики:"; echo "$bad_lines" | sed 's/^/       /'; }
else
  warn "nvidia-smi nvlink -e недоступен"
fi

echo "== 5. PCIe: все карты под одним мостом =="
if command -v lspci >/dev/null 2>&1; then
  tree=$(lspci -tv 2>/dev/null | grep -i -c 'nvidia')
  [ "$tree" -ge 4 ] && ok "в дереве PCIe $tree записи NVIDIA" || bad "в дереве PCIe $tree записей NVIDIA"
else
  warn "lspci нет"
fi

echo "== 6. Температуры и лимит мощности =="
nvidia-smi --query-gpu=index,temperature.gpu,power.draw,power.limit,clocks_throttle_reasons.active \
  --format=csv,noheader 2>/dev/null | sed 's/^/  /'
warn "проверить после нагрузки: троттлинг не должен быть SW Thermal / HW Thermal"

echo
[ "$fail" -eq 0 ] && echo "ИТОГ: узел принят" || echo "ИТОГ: есть отказы — см. FAIL выше"
exit "$fail"
