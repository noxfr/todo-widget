# todo-widget

Petit widget GTK4/libadwaita pour Ubuntu qui affiche `~/todo.md` en liste de tâches à cocher, avec un badge Urgent / Pas urgent. Le fichier est surveillé : toute modification extérieure (éditeur, script, Claude Code) apparaît immédiatement.

Fourni avec un skill Claude Code (`skill/todo-widget`) pour ajouter, lister et cocher des tâches en langage naturel.

## Format

```markdown
- [ ] Tâche à faire
- [x] Tâche faite
- [ ] Tâche urgente #urgent
```

## Prérequis

- Python 3, PyGObject, GTK 4, libadwaita (`sudo apt install python3-gi gir1.2-gtk-4.0 gir1.2-adw-1`)

## Installation

```bash
./install.sh
gtk-launch local.TodoWidget
```

Le script installe le lanceur et l'icône dans `~/.local/share`, et lie le skill dans `~/.claude/skills/todo-widget`. Le widget tourne depuis ce dossier : ne pas le déplacer après installation.

Pour l'avoir dans le dock : clic droit sur l'icône → « Épingler au dock ».
