"""
Script di riconoscimento gesti attraverso sensore di distanza HC-SR04 e machine learning.
Questo programma acquisisce dati da un sensore di distanza collegato ad Arduino,
elabora i dati con un modello di machine learning pre-addestrato e invia il risultato
del riconoscimento del gesto nuovamente ad Arduino.
"""

# === IMPORTAZIONI LIBRERIE ===
import serial     # Gestisce la comunicazione seriale con Arduino
import joblib     # Consente di caricare modelli di machine learning salvati
import time       # Fornisce funzioni per gestire il tempo e le pause
import numpy as np # Libreria per calcoli matematici e manipolazione di array
import os         # Permette di interagire con il sistema operativo (gestione file)
from collections import Counter  # Usato per contare occorrenze (frequenze)

# === CARICAMENTO MODELLO E ENCODER ===
model_path = os.path.join("modello_addestrato", "modello_random_forest.pkl")  # Percorso del modello salvato
encoder_path = os.path.join("modello_addestrato", "label_encoder.pkl")  # Percorso dell'encoder salvato

model = joblib.load(model_path)  # Carichiamo il modello di machine learning pre-addestrato
label_encoder = joblib.load(encoder_path)  # Carichiamo l'encoder per tradurre numeri in etichette

# === CONFIGURAZIONE SERIALE ===
ser = serial.Serial('COM13', 9600, timeout=1)  # Inizializziamo comunicazione con Arduino
ser.setDTR(False)  # Disabilitiamo il segnale DTR per evitare reset Arduino
time.sleep(3)  # Attesa per stabilizzazione della connessione seriale

# === COUNTDOWN 5 SECONDI ===
print("Preparati... inizio registrazione tra 5 secondi!")  # Avviso utente
for i in range(5, 0, -1):
    print(f"{i}...")  # Mostra il conto alla rovescia
    time.sleep(1)     # Pausa di 1 secondo tra ogni numero

# === RACCOLTA DATI ===
print("Inizio registrazione dei dati...")  # Avviso inizio acquisizione
start_time = time.time()  # Memorizziamo tempo di inizio
distanze = []  # Lista per salvare le letture del sensore

while time.time() - start_time < 1.5:  # Acquisizione per 1.5 secondi (durata ottimale)
    line = ser.readline().decode('utf-8').strip()  # Leggiamo dati da Arduino
    if line.isdigit():
        distanze.append(int(line))  # Convertiamo in intero e aggiungiamo alla lista
    time.sleep(0.01)  # Breve pausa per non sovraccaricare la CPU

if not distanze:
    print("Nessun dato letto dal sensore.")  # Avviso se non ci sono dati
    ser.close()  # Chiudiamo la connessione
    exit()  # Usciamo dal programma

# === CLASSIFICAZIONE ===
X = np.array(distanze).reshape(-1, 1)  # Prepariamo dati per il modello
predizioni = model.predict(X)  # Facciamo predizioni sui dati raccolti
etichette = label_encoder.inverse_transform(predizioni)  # Convertiamo numeri in nomi gesti

conteggio = Counter(etichette)  # Contiamo frequenza di ogni gesto predetto
gesto_rilevato, frequenza = conteggio.most_common(1)[0]  # Troviamo il gesto più frequente
confidenza = (frequenza / len(etichette)) * 100  # Calcoliamo percentuale di confidenza

print("\n--- RISULTATO ---")
print(f"Campioni raccolti: {len(etichette)}")  # Numero di campioni analizzati
print(f"Gesto rilevato: {gesto_rilevato.upper()} ({confidenza:.1f}%)")  # Mostriamo gesto e confidenza

# === INVIO RISULTATO A ARDUINO ===
# Prepariamo la stringa da inviare ad Arduino nel formato "gesto;confidenza"
risultato_seriale = f"{gesto_rilevato};{confidenza:.1f}"
print(f"Invio ad Arduino: {risultato_seriale}")

ser.write((risultato_seriale + '\n').encode())  # Inviamo il risultato ad Arduino
ser.flush()  # Assicuriamo invio completo dei dati
time.sleep(1)  # Tempo per completare la trasmissione

# === Scrittura su file di log ===
log_file = "log_file.txt"  # Nome del file di log
with open(log_file, "a") as file:  # Apriamo file in modalità append
    file.write(f"Inviato a Arduino: {risultato_seriale}\n")  # Registriamo l'operazione

ser.close()  # Chiudiamo la connessione seriale
