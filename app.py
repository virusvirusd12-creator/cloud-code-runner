from flask import Flask, request, jsonify, send_from_directory
import tempfile, subprocess, os, sys, shutil, ast

app = Flask(__name__, static_folder='frontend', static_url_path='')

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/run', methods=['POST'])
def run_code():
    data = request.get_json() or {}
    code = data.get('code', '')
    lang = data.get('language', 'python')
    if lang != 'python':
        return jsonify({"output": "", "error": "الواجهة تدعم Python فقط الآن"}), 400

    try:
        ast.parse(code)
    except SyntaxError as se:
        return jsonify({"output": "", "error": f"SyntaxError: {se}"}), 200

    tmpdir = tempfile.mkdtemp(prefix="run_")
    file_path = os.path.join(tmpdir, "code.py")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    try:
        proc = subprocess.run([sys.executable, file_path],
                              stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE,
                              universal_newlines=True,
                              timeout=5)
        stdout = proc.stdout
        stderr = proc.stderr
        combined = stdout + (("\n[stderr]\n" + stderr) if stderr else "")
        return jsonify({"output": combined, "error": ""})
    except subprocess.TimeoutExpired:
        return jsonify({"output": "", "error": "خطأ: نفذت مهلة التشغيل (timeout)"})
    except Exception as e:
        return jsonify({"output": "", "error": f"خطأ داخلي: {e}"})
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)

@app.route('/lint', methods=['POST'])
def lint_code():
    data = request.get_json() or {}
    code = data.get('code', '')
    try:
        import autopep8
        fixed = autopep8.fix_code(code)
        return jsonify({"fixed_code": fixed})
    except Exception:
        try:
            ast.parse(code)
            return jsonify({"fixed_code": None, "message": "لا توجد أخطاء بناء واضحة"})
        except SyntaxError as se:
            return jsonify({"fixed_code": None, "message": f"SyntaxError: {se}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=True)



