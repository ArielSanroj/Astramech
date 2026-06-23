#!/bin/bash
# ============================================
# 🏛️ CTO RULES VERIFICATION
# ============================================
# Propósito: Verificar cumplimiento de estándares CTO
# Se activa cuando el código crece 2x o más
# Atributo de Calidad: Escalabilidad + Gobernanza
# ============================================

echo "🏛️ ======================================"
echo "   CTO RULES VERIFICATION"
echo "========================================"

score=0
total=8

FIND_EXCLUDES=(
    -path "*/.venv/*" -o
    -path "*/venv/*" -o
    -path "*/env/*" -o
    -path "*/node_modules/*" -o
    -path "*/__pycache__/*" -o
    -path "*/.git/*" -o
    -path "*/site-packages/*" -o
    -path "*/external_repos/*"
)

# 1. Verificar documentación README
echo -e "\n📚 [1/8] Documentación README..."
if [ -f "README.md" ]; then
    readme_lines=$(wc -l < README.md)
    if [ "$readme_lines" -gt 30 ]; then
        echo "  ✅ README.md existe ($readme_lines líneas)"
        ((score++))
    else
        echo "  ⚠️  README.md muy corto ($readme_lines líneas, mínimo: 30)"
    fi
else
    echo "  ❌ README.md no existe"
fi

# 2. Verificar CHANGELOG
echo -e "\n📋 [2/8] CHANGELOG..."
if [ -f "CHANGELOG.md" ] || [ -f "HISTORY.md" ]; then
    echo "  ✅ Archivo de cambios encontrado"
    ((score++))
else
    echo "  ⚠️  No existe CHANGELOG.md"
fi

# 3. Verificar tests
echo -e "\n🧪 [3/8] Tests..."
test_count=$(find . \( "${FIND_EXCLUDES[@]}" \) -prune -o \( -name "test_*.py" -o -name "*_test.py" \) -print 2>/dev/null | wc -l)
if [ "$test_count" -ge 5 ]; then
    echo "  ✅ $test_count archivos de test encontrados"
    ((score++))
elif [ "$test_count" -gt 0 ]; then
    echo "  ⚠️  Solo $test_count tests (mínimo recomendado: 5)"
else
    echo "  ❌ No hay tests"
fi

# 4. Verificar tamaño de módulos
echo -e "\n📏 [4/8] Tamaño de módulos..."
big_files=$(find . \( "${FIND_EXCLUDES[@]}" \) -prune -o -name "*.py" -exec wc -l {} \; 2>/dev/null | awk '$1 > 300 {count++} END {print count+0}')
if [ "$big_files" -eq 0 ]; then
    echo "  ✅ Todos los archivos bajo 300 líneas"
    ((score++))
else
    echo "  ⚠️  $big_files archivos exceden 300 líneas"
fi

# 5. Verificar secrets hardcodeados
echo -e "\n🔒 [5/8] Seguridad - Secrets..."
secrets=$(grep -rn "password\s*=\s*['\"][^'\"]\+" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="env" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".git" --exclude-dir="site-packages" --exclude-dir="external_repos" . 2>/dev/null | grep -v "password\s*=\s*['\"]['\"]" | wc -l)
api_keys=$(grep -rn "api_key\s*=\s*['\"][A-Za-z0-9]\+" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="env" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".git" --exclude-dir="site-packages" --exclude-dir="external_repos" . 2>/dev/null | wc -l)
total_secrets=$((secrets + api_keys))

if [ "$total_secrets" -eq 0 ]; then
    echo "  ✅ No se encontraron secrets hardcodeados"
    ((score++))
else
    echo "  ❌ $total_secrets posibles secrets encontrados"
fi

# 6. Verificar logging
echo -e "\n📝 [6/8] Sistema de logging..."
if grep -rq "import logging\|from logging" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="env" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".git" --exclude-dir="site-packages" --exclude-dir="external_repos" . 2>/dev/null; then
    echo "  ✅ Sistema de logging implementado"
    ((score++))
else
    echo "  ⚠️  No se encontró logging configurado"
fi

# 7. Verificar type hints
echo -e "\n🏷️  [7/8] Type hints..."
typed_funcs=$(grep -rn "def .*(.*).*->" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="env" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".git" --exclude-dir="site-packages" --exclude-dir="external_repos" . 2>/dev/null | wc -l)
total_funcs=$(grep -rn "def .*(" --include="*.py" --exclude-dir=".venv" --exclude-dir="venv" --exclude-dir="env" --exclude-dir="node_modules" --exclude-dir="__pycache__" --exclude-dir=".git" --exclude-dir="site-packages" --exclude-dir="external_repos" . 2>/dev/null | wc -l)

if [ "$total_funcs" -gt 0 ]; then
    ratio=$((typed_funcs * 100 / total_funcs))
    if [ "$ratio" -ge 50 ]; then
        echo "  ✅ $ratio% de funciones con type hints"
        ((score++))
    else
        echo "  ⚠️  Solo $ratio% de funciones con type hints"
    fi
else
    echo "  ℹ️  No hay funciones para analizar"
fi

# 8. Verificar dependencias circulares
echo -e "\n🔄 [8/8] Dependencias circulares..."
circular=$(python3 << 'EOF' 2>/dev/null
import ast, os
from collections import defaultdict

imports = defaultdict(set)
for root, dirs, files in os.walk("."):
    dirs[:] = [d for d in dirs if d not in ["node_modules", ".venv", "venv", "__pycache__", ".git", "env", "site-packages", "external_repos"]]
    for f in files:
        if f.endswith(".py"):
            path = os.path.join(root, f)
            try:
                with open(path) as file:
                    tree = ast.parse(file.read())
                    module = path.replace("/", ".").replace(".py", "").lstrip(".")
                    for node in ast.walk(tree):
                        if isinstance(node, ast.ImportFrom) and node.module:
                            imports[module].add(node.module)
            except: pass

count = 0
for mod, deps in imports.items():
    for dep in deps:
        if dep in imports and mod in imports[dep]:
            count += 1
print(count // 2)  # Dividir por 2 porque cada par se cuenta dos veces
EOF
)

if [ "$circular" -eq 0 ]; then
    echo "  ✅ No hay dependencias circulares"
    ((score++))
else
    echo "  ❌ $circular dependencias circulares encontradas"
fi

# Resultado final
echo -e "\n========================================"
echo "📊 SCORE FINAL: $score/$total"
echo "========================================"

if [ $score -eq $total ]; then
    echo "🎉 ¡EXCELENTE! Todas las CTO Rules cumplidas"
    exit 0
elif [ $score -ge 6 ]; then
    echo "✅ APROBADO - Algunas mejoras pendientes"
    exit 0
elif [ $score -ge 4 ]; then
    echo "⚠️  ATENCIÓN - Revisar items pendientes"
    exit 1
else
    echo "❌ NO CUMPLE - Acción requerida antes de merge"
    exit 1
fi
