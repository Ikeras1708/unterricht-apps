# Unterrichts-Apps

Kleine, offline lauffähige HTML-Apps für den Unterricht, ausgeliefert über GitHub Pages.

- `strandmaus/`: „Die Eule und die Strandmäuse“, Simulationsspiel zur natürlichen Auslese (Biologie, Klasse 8).
  Adressparameter: `?lehrkraft=1` (Ansicht für die Lehrkraft mit gemessenem Fangfaktor), `?auto=1` (die Eule jagt
  allein), dazu `start`, `wanderung`, `naechte`, `fang`, `zeit`, `tarnung`, `fangfaktor`.

Die Dateien hier sind Kopien. Die Quelle liegt im Obsidian-Vault des Referendars im Stundenordner; geändert wird
dort, danach `python -I -B veroeffentlichen.py`. Die Apps speichern nur Spielzahlen im Browser-Tab
(sessionStorage), keine Cookies, kein Datenversand. Erstellt mit KI-Unterstützung (Claude).
