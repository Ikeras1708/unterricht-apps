"""Veröffentlicht die Unterrichts-Apps aus dem Vault auf GitHub Pages und legt QR-Codes in den Stundenordner.

Quelle der Wahrheit ist die HTML-Datei im Stundenordner des Vaults; geändert wird dort, nie in diesem Ordner.
Dieser Ordner ist nur die Kopie, die GitHub Pages ausliefert (Repository `unterricht-apps`, öffentlich).

Aufruf mit dem Interpreter der Vault-Werkzeuge:
  python -I -B veroeffentlichen.py einrichten   einmalig nach `gh auth login`: Repository anlegen, Pages einschalten
  python -I -B veroeffentlichen.py              Apps aus dem Vault kopieren, committen, hochladen, QR-Codes neu
  python -I -B veroeffentlichen.py --nur-qr     nur die QR-Codes neu erzeugen
  python -I -B veroeffentlichen.py --pruefen    nur prüfen, ob die Adressen antworten

Datenschutz: Die Commits tragen den Namen „Unterricht-Apps“ und die noreply-Adresse von GitHub, nie die
private E-Mail-Adresse. Die Apps enthalten keine Daten von Lernenden.
"""
import datetime
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HIER = Path(__file__).resolve().parent
VAULT = Path(r"C:\Users\tille\Documents\Claude Ref")
REPO = "unterricht-apps"
BESCHREIBUNG = "Kleine Lern-Apps für den Biologie- und Mathematikunterricht (offline lauffähige HTML-Dateien)"

# Je App: Ordner im Repository, Quelle im Vault, QR-Codes (Dateiname im Stundenordner, Zusatz an der Adresse)
APPS = [
    {
        "ordner": "strandmaus",
        "quelle": VAULT / "20_Lerngruppen" / "Ausbildungsunterricht" / "8.1-Biologie" / "26-11-19-UB-Strandmaus"
        / "1119-Strandmaus-Spiel.html",
        "qr": [("1119-Strandmaus-Spiel-QR.png", ""), ("1119-Strandmaus-Spiel-QR-Lehrkraft.png", "?lehrkraft=1")],
    },
]


def gh_pfad():
    for kandidat in (shutil.which("gh"), r"C:\Program Files\GitHub CLI\gh.exe",
                     str(Path.home() / "AppData/Local/Programs/GitHub CLI/gh.exe")):
        if kandidat and Path(kandidat).is_file():
            return kandidat
    sys.exit("GitHub CLI nicht gefunden. Einmalig installieren: winget install --id GitHub.cli -e, dann gh auth login")


def lauf(befehl, pruefen=True):
    ergebnis = subprocess.run(befehl, cwd=HIER, capture_output=True, text=True, encoding="utf-8")
    if pruefen and ergebnis.returncode != 0:
        sys.exit(f"Fehler bei {' '.join(map(str, befehl))}:\n{ergebnis.stderr.strip() or ergebnis.stdout.strip()}")
    return ergebnis.stdout.strip()


def konto():
    gh = gh_pfad()
    login = lauf([gh, "api", "user", "--jq", ".login"])
    kennung = lauf([gh, "api", "user", "--jq", ".id"])
    return gh, login, kennung


def adresse(login, ordner, zusatz=""):
    return f"https://{login.lower()}.github.io/{REPO}/{ordner}/{zusatz}"


def kopieren():
    for app in APPS:
        if not app["quelle"].is_file():
            sys.exit(f"Quelle fehlt: {app['quelle']}")
        ziel = HIER / app["ordner"] / "index.html"
        ziel.parent.mkdir(exist_ok=True)
        shutil.copyfile(app["quelle"], ziel)
        print(f"kopiert: {app['quelle'].name} -> {app['ordner']}/index.html")


def identitaet(login, kennung):
    lauf(["git", "config", "user.name", "Unterricht-Apps"])
    lauf(["git", "config", "user.email", f"{kennung}+{login}@users.noreply.github.com"])


def committen():
    lauf(["git", "add", "-A"])
    if not lauf(["git", "status", "--porcelain"]):
        print("keine Änderungen")
        return False
    lauf(["git", "commit", "-m", f"Apps aktualisiert {datetime.date.today().isoformat()}"])
    return True


def qr_codes(login):
    sys.path.insert(0, str(VAULT / ".claude" / "werkzeuge"))
    import office_hilfe as oh
    for app in APPS:
        for datei, zusatz in app["qr"]:
            ziel = app["quelle"].parent / datei
            oh.qr_bild(adresse(login, app["ordner"], zusatz), ziel)
            print(f"QR: {ziel.name} -> {adresse(login, app['ordner'], zusatz)}")


def pruefen(login, warten=0):
    ende = time.time() + warten
    for app in APPS:
        url = adresse(login, app["ordner"])
        while True:
            try:
                anfrage = urllib.request.Request(url, headers={"User-Agent": "unterricht-apps-pruefung/1.0"})
                with urllib.request.urlopen(anfrage, timeout=20) as antwort:
                    print(f"erreichbar ({antwort.status}): {url}")
                    break
            except Exception as fehler:  # Pages braucht nach dem ersten Hochladen einige Minuten
                if time.time() > ende:
                    print(f"noch nicht erreichbar: {url} ({fehler})")
                    break
                time.sleep(20)


def einrichten():
    gh, login, kennung = konto()
    if not (HIER / ".git").is_dir():
        lauf(["git", "init", "-b", "main"])
    identitaet(login, kennung)
    kopieren()
    committen()
    if not lauf(["git", "remote"], pruefen=False):
        lauf([gh, "repo", "create", REPO, "--public", "--source", ".", "--remote", "origin", "--push",
              "--description", BESCHREIBUNG])
    else:
        lauf(["git", "push", "-u", "origin", "main"])
    vorhanden = subprocess.run([gh, "api", f"repos/{login}/{REPO}/pages"], cwd=HIER, capture_output=True)
    if vorhanden.returncode != 0:
        lauf([gh, "api", "-X", "POST", f"repos/{login}/{REPO}/pages",
              "-f", "source[branch]=main", "-f", "source[path]=/"])
    qr_codes(login)
    pruefen(login, warten=300)


def main():
    argumente = sys.argv[1:]
    if argumente[:1] == ["einrichten"]:
        einrichten()
        return
    gh, login, kennung = konto()
    if "--pruefen" in argumente:
        pruefen(login)
        return
    if "--nur-qr" not in argumente:
        identitaet(login, kennung)
        kopieren()
        if committen():
            lauf(["git", "push"])
    qr_codes(login)
    pruefen(login, warten=180)


if __name__ == "__main__":
    main()
