import requests
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class OllamaConnector:
    def __init__(self, host="http://localhost:11434", model="llama3.2:1b"):
        """Initialize the Ollama connector"""
        self.host = host
        self.model = model
        self.api_url = f"{host}/api/generate"
        self.start_time = 0
        self.end_time = 0
        
    def generate(self, prompt, system_prompt=None, max_tokens=2048):
        """Generate text from Ollama API"""
        self.start_time = time.time()
        
        # Prepare the request
        request_data = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "max_tokens": max_tokens
        }
        
        # Add system prompt if provided
        if system_prompt:
            request_data["system"] = system_prompt
            
        try:
            response = requests.post(self.api_url, json=request_data)
            
            if response.status_code == 200:
                result = response.json()
                self.end_time = time.time()
                return result.get("response", "")
            else:
                print(f"Error calling Ollama API: {response.status_code}")
                print(response.text)
                self.end_time = time.time()
                return f"Error: {response.status_code}"
                
        except Exception as e:
            print(f"Exception calling Ollama API: {e}")
            self.end_time = time.time()
            return f"Exception: {e}"
    
    def generate_summary(self, text):
        """Generate a summary of the text"""
        prompt = f"""Generează un rezumat complet și clar al următorului text. 
Pune accentul pe conceptele cheie, definițiile importante și ideile principale.
Structurează rezumatul cu subtitluri și puncte pentru mai multă claritate.

TEXT:
{text}

REZUMAT:
"""

        system_prompt = """Ești un expert în crearea de rezumate educaționale clare și comprehensive.
Vei genera un rezumat bine structurat al textului, care să includă:
1. Conceptele și termenii cheie
2. Definiții importante
3. Principalele teorii sau idei  
4. Exemple relevante dacă există

Folosește formatare cu subtitluri, liste cu puncte și paragrafe scurte pentru a face rezumatul ușor de citit și de înțeles.
"""
        
        return self.generate(prompt, system_prompt)
    
    def generate_test(self, text, num_questions=5):
        """Generate a multiple choice test based on the text"""
        prompt = f"""Creează un test grilă cu {num_questions} întrebări bazate pe următorul text.
Fiecare întrebare trebuie să aibă 3 variante de răspuns, din care doar una este corectă.
Marchează răspunsul corect cu [✓].

TEXT:
{text}

TEST GRILĂ:
"""

        system_prompt = """Ești un expert în crearea de teste educaționale.
Vei genera un test grilă cu întrebări despre conceptele importante din text.
Pentru fiecare întrebare:
1. Formulează întrebarea clar și concis
2. Oferă 3 variante de răspuns, doar una fiind corectă
3. Marchează răspunsul corect cu [✓]
4. Variază tipurile de întrebări (definire concepte, aplicații practice, relații cauză-efect etc.)

Asigură-te că întrebările testează înțelegerea materialului, nu doar memorarea.
"""
        
        return self.generate(prompt, system_prompt)
    
    def get_execution_time(self):
        """Get the execution time of the last API call in seconds"""
        if self.start_time > 0 and self.end_time > 0:
            return self.end_time - self.start_time
        return 0 