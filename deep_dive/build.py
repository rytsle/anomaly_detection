# Builds the self-contained deep_dive.html: python3 deep_dive/build.py (run after make_data.py and slides/make_figs.py)
import base64, json
from pathlib import Path
here = Path(__file__).parent
img = lambda f: "data:image/png;base64," + base64.b64encode((here.parent / "slides" / f).read_bytes()).decode()
html = (here / "template.html").read_text()
html = html.replace("{{IMG_ANOMALY}}", img("fig_anomaly.png")).replace("{{IMG_SESSIONS}}", img("fig_sessions.png")).replace("{{IMG_TIMELINE}}", img("fig_timeline.png"))
q = (here / "questions_section.html").read_text()
fill = json.loads((here / "questions_fill.json").read_text()) if (here / "questions_fill.json").exists() else {}
for k, v in fill.items():
    q = q.replace("{{" + k + "}}", v)
html = html.replace("{{QUESTIONS}}", q).replace("/*WIDGET_C*/", (here / "widget_c.js").read_text())
html = html.replace("{{DATA}}", json.dumps(json.loads((here / "data.json").read_text()), separators=(",", ":")))
(here / "deep_dive.html").write_text(html)
print("deep_dive.html", len(html) // 1024, "KB")
