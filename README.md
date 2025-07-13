# Cerebrum Pulse - Controllo Multimediale con Gestures

**Autore:** VincenzoT

---

## Descrizione

Cerebrum Pulse è un'applicazione Python che utilizza la webcam per riconoscere gesti della mano tramite la libreria MediaPipe e permette di controllare il volume, la riproduzione multimediale e la navigazione di brani/video con semplici movimenti della mano.  
Ad esempio, un pollice in su aumenta il volume ecc.

---

## Funzionalità

- Rilevamento gesti:
  - Pollice in su → Volume su
  - Pollice in giù → Volume giù
  - Palmo aperto → Play/Pausa
  - Indice puntato → Avanti
  - Segno V (indice e medio) → Indietro

- Box di stato con il nome del gesto rilevato.
- Ritardo tra azioni per evitare ripetizioni accidentali.

---

## Requisiti

- Python 3.7+
- OpenCV
- MediaPipe
- PyAutoGUI
- NumPy

---

## Installazione

1. Clona il repository o scarica lo script Python.
2. Installa le librerie richieste:

```bash
pip install opencv-python mediapipe pyautogui numpy
