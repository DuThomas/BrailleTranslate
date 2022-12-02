# BrailleTranslate 2022

Traducteur de braille français - Projet de la mineur ***Métiers de la création 1***

## Application

###Au préalable:

Installer *tkinter*

Linux OS
```bash
python3 ./app.py
```

Windows OS
```bash
python ./app.py
```

###Aperçu :

![exemple_r](res/readmeImg/exemple_r.png)

Application basée sur la table suivante :

[![tableBraille](res/readmeImg/tableBraille.png)](https://fr.wikipedia.org/wiki/Braille)

## Traducteur de braille

Pour traduire un texte en braille, il faut déjà avoir le texte.

### 1. Ecrire du texte en braille

###Au préalable:

Installer *cv2 (cv)*

Linux OS
```bash
python3 ./brailleWritter.py
```

Windows OS
```bash
python ./brailleWritter.py
```

Ce script permet de d'écrire un texte en braille sur une image blanche.

Utiliser la touche :

- "entrée" pour sauter une ligne
- "échap" pour enregistrer l'image et quiter

Une image intitulée "brailleText.png" sera ensuite enregistrée dans le dossier [`./res/`](res)

![texte braille](res/readmeImg/brailleText.png)

### 2. Lire et traduire ce texte

###Au préalable:

Installer *cv2 (cv)*

Linux OS
```bash
python3 ./brailleReader.py
```

Windows OS
```bash
python ./brailleReader.py
```

Ce script va ensuite récupérer l'image enregistrée précédemment pour traduire le braille qu'elle contient.

Voici le résultat :

![texte traduit](res/readmeImg/output.png)

## Contributeurs

- Du Thomas
- Jules Tristan
