from flask import Flask, render_template_string, request

app = Flask(__name__)

# HTML form template using Jinja2
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Online Calculator</title>
</head>
<body>
    <h2>Simple Calculator</h2>
    <form method="post">
        <input type="number" name="num1" step="any" required>
        <select name="operation">
            <option value="+">+</option>
            <option value="-">−</option>
            <option value="*">×</option>
            <option value="/">÷</option>
        </select>
        <input type="number" name="num2" step="any" required>
        <input type="submit" value="Calculate">
    </form>
    {% if result is not none %}
        <h3>Result: {{ result }}</h3>
    {% endif %}
</body>
</html>
'''

@app.route("/", methods=["GET", "POST"])
def calculator():
    result = None
    if request.method == "POST":
        try:
            num1 = float(request.form["num1"])
            num2 = float(request.form["num2"])
            op = request.form["operation"]
            if op == "+":
                result = num1 + num2
            elif op == "-":
                result = num1 - num2
            elif op == "*":
                result = num1 * num2
            elif op == "/":
                result = num1 / num2 if num2 != 0 else "Error (divide by zero)"
            else:
                result = "Invalid operation"
        except Exception as e:
            result = f"Error: {e}"
    return render_template_string(HTML_TEMPLATE, result=result)

if __name__ == "__main__":
    app.run(debug=True)
