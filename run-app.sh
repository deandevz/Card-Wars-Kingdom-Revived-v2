#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# --- Detectar Python disponivel ---
PYTHON_CMD=""
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo ""
    echo "  ERRO: Python nao encontrado!"
    echo "  Instale Python 3.x antes de continuar."
    exit 1
fi

# --- Configurar venv automaticamente ---
VENV_DIR="$SCRIPT_DIR/venv"

setup_venv() {
    if [ ! -d "$VENV_DIR" ]; then
        echo "  Criando ambiente virtual (venv)..."
        $PYTHON_CMD -m venv "$VENV_DIR"
        if [ $? -ne 0 ]; then
            echo ""
            echo "  ERRO: Falha ao criar venv."
            echo "  Tente instalar: sudo apt install python3-venv  (Linux)"
            echo "                  ou: sudo pacman -S python       (Steam Deck/Arch)"
            exit 1
        fi
        echo "  Ambiente virtual criado com sucesso!"
    fi

    source "$VENV_DIR/bin/activate"

    # Verificar se os requirements estao instalados
    # Compara o hash do requirements.txt com o ultimo instalado
    REQ_HASH=$(md5sum "$SCRIPT_DIR/requirements.txt" 2>/dev/null || md5 -q "$SCRIPT_DIR/requirements.txt" 2>/dev/null)
    HASH_FILE="$VENV_DIR/.req_hash"

    if [ ! -f "$HASH_FILE" ] || [ "$(cat "$HASH_FILE" 2>/dev/null)" != "$REQ_HASH" ]; then
        echo "  Instalando dependencias..."
        pip install --upgrade pip -q 2>/dev/null
        pip install -r "$SCRIPT_DIR/requirements.txt" -q
        if [ $? -ne 0 ]; then
            echo ""
            echo "  ERRO: Falha ao instalar dependencias."
            exit 1
        fi
        echo "$REQ_HASH" > "$HASH_FILE"
        echo "  Dependencias instaladas com sucesso!"
    fi
}

# --- Menu principal ---
echo ""
echo "  ╔══════════════════════════════════════╗"
echo "  ║   Card Wars Kingdom - Offline Edition ║"
echo "  ║          dev by deandevz              ║"
echo "  ╚══════════════════════════════════════╝"
echo ""
echo "  [1] Iniciar servidor"
echo "  [2] Sincronizar dados com remoto"
echo "  [0] Sair"
echo ""
read -p "  Escolha uma opcao: " opcao

case $opcao in
    1)
        echo ""
        setup_venv
        echo "  Iniciando servidor..."
        echo ""
        python app.py
        ;;
    2)
        echo ""
        setup_venv

        echo "  === Etapa 1/3: Baixando dados do servidor remoto ==="
        echo ""
        python download_blueprints.py
        if [ $? -ne 0 ]; then
            echo ""
            echo "  ERRO: Falha ao baixar dados. Verifique sua conexao."
            exit 1
        fi

        echo ""
        echo "  === Etapa 2/3: Fazendo merge dos blueprints ==="
        echo ""
        python merge_blueprints.py
        if [ $? -ne 0 ]; then
            echo ""
            echo "  ERRO: Falha no merge dos blueprints."
            exit 1
        fi

        echo ""
        echo "  === Etapa 3/3: Aplicar dados atualizados ==="
        echo ""
        echo "  Os dados mesclados estao em: data_merged/persist/blueprints/"
        echo ""
        read -p "  Deseja copiar data_merged para data agora? (s/n): " confirma

        if [ "$confirma" = "s" ] || [ "$confirma" = "S" ]; then
            cp -r data_merged/persist/blueprints/* data/persist/blueprints/
            if [ -f data_merged/persist/manifest.json ]; then
                cp data_merged/persist/manifest.json data/persist/manifest.json
            fi
            echo ""
            echo "  Dados atualizados com sucesso!"
            echo "  Voce pode iniciar o servidor agora com a opcao [1]."
        else
            echo ""
            echo "  OK! Os dados ficam em data_merged/ para voce aplicar manualmente:"
            echo "    cp -r data_merged/persist/blueprints/* data/persist/blueprints/"
        fi
        echo ""
        ;;
    0)
        echo "  Ate mais!"
        exit 0
        ;;
    *)
        echo "  Opcao invalida."
        exit 1
        ;;
esac
