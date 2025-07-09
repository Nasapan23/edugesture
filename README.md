# 🎓 EduGesture

Aplicație educațională care permite navigarea printre fișierele PDF folosind gesturi ale mâinii, generarea de rezumate și teste cu Ollama.

## Funcționalități

- 👉 Navighează printre fișierele PDF din folderul Lectii/ cu gesturi
- 📄 Deschide fișiere PDF și navigează prin paginile lor
- 🤖 Generează rezumate și teste grilă ca PDF-uri folosind Ollama
- 🖐️ Control complet cu gesturi ale mâinii detectate prin camera video

## Gesturi

| Gest | Acțiune |
|------|---------|
| 👉 Deget spre dreapta | Navigare înainte (în meniu sau document) |
| 👉 Deget spre stânga | Navigare înapoi (în meniu sau document) |
| ✌️ Două degete | Generează rezumat + test ca PDF-uri cu Ollama |
| 👌 Semn OK | Deschide fișierul selectat |
| ✋ Palma deschisă | Închide fișierul / revine la meniu |

## Cerințe

- Python 3.8+
- Cameră web
- [Ollama](https://ollama.ai/) instalat și funcțional
- Model LLM disponibil în Ollama (implicit: llama3.2:1b - optimizat pentru CPU)
- Windows 10/11

### Dependențe Python

```
pygame>=2.1.0
mediapipe>=0.8.10
opencv-python>=4.5.5
PyPDF2>=2.10.0
pdf2image>=1.16.0
Pillow>=9.0.0
requests>=2.27.1
numpy>=1.22.0
python-dotenv>=0.19.2
fpdf2>=2.7.4
```

Pentru Windows, este necesar și [Poppler pentru Windows](https://github.com/oschwartz10612/poppler-windows/releases/) pentru procesarea PDF.

## Instalare

1. Clonează repository-ul:
   ```
   git clone https://github.com/numele-tău/edugesture.git
   cd edugesture
   ```

2. Creează un mediu virtual și activează-l:
   ```
   python -m venv venv
   venv\Scripts\activate
   ```

3. Instalează dependințele:
   ```
   pip install -r requirements.txt
   ```

4. Descarcă și instalează [Poppler pentru Windows](https://github.com/oschwartz10612/poppler-windows/releases/)
   - Adaugă calea către Poppler bin în PATH sau specifică calea în pdf_handler.py

5. Asigură-te că Ollama este instalat și rulează
   - Instalează [Ollama](https://ollama.ai/download)
   - Rulează Ollama și asigură-te că are modelul llama3.2:1b instalat (optimizat pentru CPU):
     ```
     ollama pull llama3.2:1b
     ```

6. Adaugă fișiere PDF în directorul `Lectii/` pentru a putea naviga prin ele:
   ```
   # Directorul Lectii/ conține deja exemple de PDF-uri
   # Poți adăuga propriile fișiere PDF în acest director
   ```

## Utilizare

1. Rulează aplicația:
   ```
   python main.py
   ```

2. Opțional, poți specifica parametri:
   ```
   python main.py --camera 0 --ollama-host http://localhost:11434 --ollama-model llama3.2:1b
   ```

3. Folosește gesturile pentru a naviga în interfață:
   - 👉 Navigare prin fișiere
   - 👌 Deschide fișierul selectat
   - ✌️ Generează rezumat și test ca PDF-uri (doar pentru PDF)
   - ✋ Închide documentul și revino la meniu

## Configurare opțională

Creează un fișier `.env` pentru a configura aplicația:

```
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2:1b
```

## Structura proiectului

```
edugesture/
├── main.py              # Aplicația principală
├── gesture_detector.py  # Detectarea gesturilor cu MediaPipe
├── pdf_handler.py       # Gestionarea fișierelor PDF
├── ollama_connector.py  # Conectarea cu Ollama
├── ui_manager.py        # Interfața grafică
├── utils.py            # Funcții utilitare
├── install_poppler.py  # Script pentru instalarea Poppler
├── requirements.txt    # Dependențe Python
├── Lectii/            # Director pentru fișiere PDF
│   ├── Capitolul_1.pdf
│   ├── Capitolul_2.pdf
│   └── Exemple_IA.pdf
└── README.md          # Documentație
```

## Funcționare

Aplicația va afișa într-o interfață grafică modernă:
- Camera video în timp real cu detecția gesturilor (cu afișaj color-coded)
- Lista fișierelor PDF din directorul Lectii/ (cu indicatori de tip fișier)
- Conținutul PDF-ului deschis (cu suport pentru diacritice românești)
- Log-uri cu acțiunile efectuate (cu color-coding pentru diferite tipuri de mesaje)
- Legendă cu gesturile disponibile (cu culori distinctive pentru fiecare acțiune)

## Depanare

### Poppler pentru PDF

Dacă întâmpini probleme cu procesarea PDF, asigură-te că Poppler este instalat corect și configurează calea în pdf_handler.py:

```python
# În pdf_handler.py - linia 95 aprox.
poppler_path = r'C:\cale\spre\poppler\bin'
```

### Detecția gesturilor

Pentru o detecție mai bună a gesturilor:
- Folosește o cameră cu rezoluție bună
- Asigură iluminare adecvată
- Ține mâna la o distanță potrivită de cameră (30-60 cm)

### Ollama

Asigură-te că serverul Ollama rulează înainte de a porni aplicația:
```
ollama serve
```

## Licență

Acest proiect este licențiat sub [MIT License](LICENSE).



