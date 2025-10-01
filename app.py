from flask import Flask, request, jsonify, render_template_string
import requests

app = Flask(__name__)

HTML_PAGE = """<!DOCTYPE html>
<html lang="ar">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>BNGX PANEL</title>
    <style>
        body {
            background:#0d0d0d;
            color:#ff66cc; /* النص زهري */
            font-family:monospace;
            text-align:center;
            margin:0;
            padding:0;
        }
        .container {
            max-width:600px;
            margin:50px auto;
            padding:20px;
            background:rgba(0,0,0,0.7);
            border-radius:10px;
            box-shadow: 0 0 20px #ff66cc;
        }
        .input-field {
            width:100%;
            padding:10px;
            margin:10px 0;
            border-radius:6px;
            border:1px solid #ff66cc;
            background:#111;
            color:#ff66cc;
            font-size:16px;
        }
        .btn {
            padding:10px 20px;
            border:none;
            border-radius:6px;
            background:linear-gradient(90deg,#ff99cc,#cc66ff);
            color:#000;
            font-weight:bold;
            cursor:pointer;
            font-size:16px;
            transition: 0.3s;
        }
        .btn:hover { transform: scale(1.05); }
        #status { margin-top:10px; font-weight:bold; }
        .result-card {
            margin-top:20px;
            text-align:right;
            background: linear-gradient(145deg, rgba(255,102,204,0.2), rgba(255,102,204,0.05));
            border: 1px solid #ff66cc;
            padding: 15px;
            border-radius:10px;
            color: #ffd6f0;
            box-shadow: 0 0 10px #ff66cc inset, 0 0 20px #ff66cc;
        }
        .result-key { color:#ff99ff; font-weight:bold; }
        .matrix-canvas {
            position: fixed;
            top:0;
            left:0;
            width:100%;
            height:100%;
            z-index:-1;
        }

        /* BNGX Profile Section */
        .team-card {
            background:rgba(255,102,204,0.1);
            border:1px solid #ff66cc;
            padding:20px;
            border-radius:10px;
            text-align:center;
            box-shadow:0 0 15px #ff66cc;
            max-width:300px;
            margin:20px auto;
            opacity:0;
            transform: translateY(20px);
            animation: fadeInUp 1s forwards;
        }
        .team-card img {
            width:120px;
            height:120px;
            border-radius:50%;
            border:3px solid #ff66cc;
            object-fit:cover;
            margin-bottom:15px;
            box-shadow:0 0 15px #ff66cc;
        }
        .team-card h3 { color:#ff66cc; }
        .team-card p { margin:5px 0; }
        .team-card a {
            display:inline-block;
            margin-top:10px;
            padding:10px 20px;
            border-radius:6px;
            background:linear-gradient(90deg,#ff99cc,#cc66ff);
            color:#000;
            font-weight:bold;
            text-decoration:none;
            transition:0.3s;
        }
        .team-card a:hover { transform:scale(1.05); }

        @keyframes fadeInUp {
            0% { opacity:0; transform: translateY(20px); }
            100% { opacity:1; transform: translateY(0); }
        }
    </style>
</head>
<body>
    <canvas id="matrix-canvas" class="matrix-canvas"></canvas>

    <div class="container">
        <h1>BNGX PANEL - Add Likes</h1>
        <input type="text" id="uid" class="input-field" placeholder="ادخل ID اللاعب" />
        <button id="sendBtn" class="btn">Add Likes</button>
        <div id="status"></div>
        <div id="result" class="result-card">هنا ستظهر النتيجة...</div>

        <!-- BNGX Section -->
        <section id="team" class="tool-section">
            <div class="team-card">
                <img src="{{ url_for('static', filename='images/IMG_2108.jpeg') }}" alt="BNGX Profile" />
                <h3 class="dev-name">BNGX</h3>
                <p class="dev-role">BNGX PANEL</p>
                <p class="dev-description">Site creator</p>
                <a href="https://t.me/Gooo1235" target="_blank">
                    💬 تواصل عبر تيليجرام
                </a>
            </div>
        </section>
    </div>

<script>
document.getElementById("sendBtn").addEventListener("click", async () => {
    const uid = document.getElementById("uid").value.trim();
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");

    if (!uid) {
        statusDiv.innerHTML = "⚠️ يرجى إدخال ID صالح.";
        return;
    }

    statusDiv.innerHTML = "⏳ جاري إرسال الطلب...";
    resultDiv.innerHTML = "جارٍ المعالجة...";

    try {
        const res = await fetch("/api/add_likes", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ id: uid })
        });

        const data = await res.json();

        if (data.error) {
            statusDiv.innerHTML = "❌ حدث خطأ";
            resultDiv.innerHTML = data.error;
            return;
        }

        statusDiv.innerHTML = "✅ تمت العملية بنجاح!";
        resultDiv.innerHTML = `
            <div><span class="result-key">👤 الاسم:</span> ${data.player_name}</div>
            <div><span class="result-key">🆔 ID:</span> ${data.player_id}</div>
            <div><span class="result-key">👍 اللايكات قبل:</span> ${data.likes_before}</div>
            <div><span class="result-key">✨ اللايكات المضافة:</span> ${data.likes_added}</div>
            <div><span class="result-key">🎯 اللايكات بعد:</span> ${data.likes_after}</div>
            <div><span class="result-key">⏱️ المدة حتى المسموح القادم:</span> ${data.seconds_until_next_allowed} ثانية</div>
        `;
    } catch (err) {
        statusDiv.innerHTML = "❌ فشل الاتصال بالخادم.";
        resultDiv.innerHTML = err.message || "خطأ غير معروف";
    }
});

// 💖 Matrix Rain قلوب نازلة
const canvas = document.getElementById('matrix-canvas');
const ctx = canvas.getContext('2d');
let width, height, fontSize=20, columns, drops;

function resizeCanvas() {
    width = window.innerWidth;
    height = window.innerHeight;
    canvas.width = width;
    canvas.height = height;
    columns = Math.floor(width / fontSize);
    drops = Array(columns).fill(1);
}

function drawMatrix() {
    ctx.fillStyle = 'rgba(0,0,0,0.08)';
    ctx.fillRect(0,0,width,height);
    ctx.font = fontSize + "px monospace";
    for(let i=0;i<drops.length;i++){
        const text = "💖"; // قلب
        ctx.fillStyle = '#ff66cc'; // زهري متوهج
        ctx.fillText(text, i*fontSize, drops[i]*fontSize);
        if(drops[i]*fontSize>height && Math.random()>0.975) drops[i]=0;
        drops[i]++;
    }
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();
setInterval(drawMatrix, 50);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_PAGE)

@app.route("/api/add_likes", methods=["POST"])
def add_likes():
    try:
        data = request.get_json(force=True)
        uid = data.get("id")
        if not uid:
            return jsonify({"error": "⚠️ لم يتم إدخال ID اللاعب"}), 400

        api_url = f"https://likes-khaki.vercel.app/send_like?player_id={uid}"

        try:
            r = requests.get(api_url, timeout=20)
            r.raise_for_status()
        except requests.exceptions.RequestException:
            return jsonify({"error": "❌ فشل الاتصال مع السيرفر الخارجي"}), 502

        try:
            return jsonify(r.json())
        except Exception:
            return jsonify({"error": "❌ رد السيرفر غير صالح"}), 500

    except Exception:
        return jsonify({"error": "⚠️ خطأ داخلي في السيرفر"}), 500

if __name__ == "__main__":
    app.run(debug=True)
