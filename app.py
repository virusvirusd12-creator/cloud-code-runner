from flask import Flask, request, jsonify
import subprocess
import tempfile
import os

app = Flask(__name__)


# -----------------------------
# 🔵 API: تشغيل كود Python
# -----------------------------
@app.route("/run", methods=["POST"])
def run_code():
    try:
        data = request.get_json()
        code = data.get("code", "")

        if not code.strip():
            return jsonify({"error": "الكود فارغ، الرجاء كتابة شيء."})

        # إنشاء ملف مؤقت لتشغيل الكود
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as temp:
            temp.write(code.encode("utf-8"))
            temp.flush()
            filename = temp.name

        # تشغيل الكود باستخدام Python
        result = subprocess.run(
            ["python3", filename],
            capture_output=True,
            text=True,
            timeout=8
        )

        output = result.stdout
        error = result.stderr

        os.unlink(filename)

        if error:
            return jsonify({"error": error})

        return jsonify({"output": output})

    except subprocess.TimeoutExpired:
        return jsonify({"error": "تنبيه: الكود أخذ وقتاً طويلاً وتوقف التنفيذ."})

    except Exception as e:
        return jsonify({"error": f"خطأ غير متوقع: {str(e)}"})


# -----------------------------
# 🔵 API: تنسيق — Lint
# -----------------------------
@app.route("/lint", methods=["POST"])
def lint_code():
    data = request.get_json()
    code = data.get("code", "")

    if not code.strip():
        return jsonify({"message": "لا يوجد كود لتنسيقه."})

    try:
        import autopep8
        fixed = autopep8.fix_code(code)
        return jsonify({"fixed_code": fixed})

    except Exception as e:
        return jsonify({
"message": "تعذر تحسين التنسيق.",
"error": str(e)
        })


# -----------------------------
# 🔵 تشغيل التطبيق
# -----------------------------
@app.route("/")
def home():
    return "Cloud Code Runner is running successfully!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
