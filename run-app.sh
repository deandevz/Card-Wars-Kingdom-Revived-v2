#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

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
        echo "  Ativando ambiente virtual..."
        source venv/bin/activate
        echo "  Iniciando servidor..."
        echo ""
        python app.py
        ;;
    2)
        echo ""
        source venv/bin/activate

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
