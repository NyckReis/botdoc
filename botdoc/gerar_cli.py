import argparse
import os
import sys
from gerador import gerar_comprovante

def main():
    parser = argparse.ArgumentParser(description="Automação Geradora de Comprovante de Conta Nubank • @nyckzao")
    parser.add_argument("--nome", "-n", help="Nome completo da pessoa")
    parser.add_argument("--cpf", "-c", help="CPF da pessoa (com ou sem pontuação)")
    parser.add_argument("--endereco", "-e", help="Endereço completo da pessoa")
    parser.add_argument("--saida", "-o", help="Nome do arquivo PDF de saída (opcional)")

    args = parser.parse_args()

    nome = args.nome
    cpf = args.cpf
    endereco = args.endereco

    if not nome or not cpf or not endereco:
        print("=" * 60)
        print("      GERADOR DE COMPROVANTE NUBANK • @nyckzao")
        print("=" * 60)
        if not nome:
            nome = input("Digite o Nome Completo: ").strip()
        if not cpf:
            cpf = input("Digite o CPF: ").strip()
        if not endereco:
            endereco = input("Digite o Endereço Completo: ").strip()

    if not nome or not cpf or not endereco:
        print("\nErro: Nome, CPF e Endereço são obrigatórios.")
        sys.exit(1)

    clean_name = "".join(c for c in nome if c.isalnum() or c in (" ", "_", "-")).rstrip().replace(" ", "_")
    output_path = args.saida or f"comprovante_{clean_name}.pdf"

    print(f"\nGerando comprovante para {nome}...")
    try:
        resultado = gerar_comprovante(
            nome=nome,
            cpf=cpf,
            endereco=endereco,
            template_path="modelo.pdf",
            output_path=output_path
        )
        print("=" * 60)
        print(f" [OK] Comprovante gerado com sucesso!")
        print(f" [OK] Nome no topo: {resultado['nome'].upper()}")
        print(f" [OK] Conta gerada (aleatória): {resultado['conta']}")
        print(f" [OK] Saldo gerado (alto aleatório): {resultado['saldo']}")
        print(f" [OK] Endereço formatado: {resultado['endereco']}")
        print(f" [OK] Arquivo salvo em: {os.path.abspath(output_path)}")
        print("=" * 60)

        if sys.platform == "win32":
            try:
                os.startfile(os.path.abspath(output_path))
            except Exception:
                pass
    except Exception as e:
        print(f"\nErro ao gerar comprovante: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
