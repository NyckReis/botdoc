import os
import uuid
import zipfile
import webbrowser
from threading import Timer
from flask import Flask, render_template, request, jsonify
from gerador import gerar_comprovante
from gerador_energisa import gerar_energisa

app = Flask(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static", "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/gerar", methods=["POST"])
def api_gerar():
    try:
        data = request.get_json() or {}
        nome = data.get("nome", "").strip()
        cpf = data.get("cpf", "").strip()
        endereco = data.get("endereco", "").strip()

        if not nome or not cpf or not endereco:
            return jsonify({"success": False, "error": "Nome, CPF e Endereço são obrigatórios."}), 400

        clean_name = "".join(c for c in nome if c.isalnum() or c in (" ", "_", "-")).rstrip().replace(" ", "_")
        uid = uuid.uuid4().hex[:6]

        # 1. Gerar Comprovante Nubank
        filename_nu = f"comprovante_nubank_{clean_name}_{uid}.pdf"
        output_nu = os.path.join(OUTPUT_DIR, filename_nu)
        res_nu = gerar_comprovante(
            nome=nome,
            cpf=cpf,
            endereco=endereco,
            template_path="modelo.pdf",
            output_path=output_nu
        )

        # 2. Gerar Comprovante Energisa (Conta de Luz)
        filename_energisa = f"comprovante_energisa_{clean_name}_{uid}.pdf"
        output_energisa = os.path.join(OUTPUT_DIR, filename_energisa)
        res_energisa = gerar_energisa(
            nome=nome,
            cpf=cpf,
            endereco=endereco,
            template_path="modelo_energisa.pdf",
            output_path=output_energisa
        )

        # 3. Gerar arquivo ZIP com os 2 comprovantes prontos
        filename_zip = f"comprovantes_{clean_name}_{uid}.zip"
        output_zip = os.path.join(OUTPUT_DIR, filename_zip)
        with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
            zf.write(output_nu, arcname=f"01_Comprovante_Nubank_{clean_name}.pdf")
            zf.write(output_energisa, arcname=f"02_Comprovante_Energisa_{clean_name}.pdf")

        return jsonify({
            "success": True,
            "nubank_url": f"/static/output/{filename_nu}",
            "energisa_url": f"/static/output/{filename_energisa}",
            "zip_url": f"/static/output/{filename_zip}",
            "dados": {
                "nome": res_nu["nome"],
                "cpf": res_nu["cpf"],
                "conta": res_nu["conta"],
                "saldo": res_nu["saldo"],
                "endereco": res_nu["endereco"]
            }
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

def open_browser():
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("==================================================")
    print(f" Gerador de Comprovantes • @nyckzao (Porta {port})")
    print(f" Acesse: http://localhost:{port}")
    print("==================================================")
    if not os.environ.get("PORT"):
        Timer(1.2, open_browser).start()
    app.run(host="0.0.0.0", port=port, debug=False)
