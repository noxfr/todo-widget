---
name: todo-widget
description: Ajoute, liste ou coche des tâches dans ~/todo.md, affiché en direct par le widget Todo (GTK) sur Ubuntu. Utilise ce skill dès que l'utilisateur dit « ajoute une tâche / un todo / mets dans le todo / note-moi de… », veut voir ses todos ou cocher une tâche.
---

# Todo widget

Les tâches sont des lignes `- [ ] texte` (ou `- [x]` si faites) dans `~/todo.md`. Le widget Todo surveille le fichier et se met à jour seul : pas de redémarrage à prévoir.

## Ajouter

```bash
echo "- [ ] Texte de la tâche" >> ~/todo.md
```

Ne pas ajouter de date : le fichier n'en contient plus.

Tâche urgente : terminer la ligne par ` #urgent` (le widget affiche un badge rouge « Urgent »). Sans ce suffixe, la tâche est « Pas urgent ».

## Lister

```bash
grep -n '^- \[' ~/todo.md
```

## Cocher

Remplacer `[ ]` par `[x]` sur la ligne voulue : `sed -i 'Ns/^- \[ \]/- [x]/' ~/todo.md` (N = numéro de ligne donné par `grep -n`).

## Règles

- Reformuler en texte court et actionnable, sans changer le sens ; ne pas créer de tâches non demandées.
- Ne jamais supprimer de ligne.
- Lancer le widget si besoin : `gtk-launch local.TodoWidget`.
