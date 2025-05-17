import serial  # Gestisce la comunicazione seriale con Arduino
import time    # Fornisce funzioni per gestire il tempo e le pause
import csv     # Permette di leggere e scrivere file CSV
import os      # Permette di interagire con il sistema operativo (gestione file)


# Configurazione iniziale
ser = serial.Serial('COM13', 9600, timeout=1)  # Inizializziamo comunicazione con Arduino (modificare la porta se necessario)

# Cartella di output per i dati
output_folder = "dati_registrati"  # Nome della cartella dove verranno salvati i dati
os.makedirs(output_folder, exist_ok=True)  # Crea la cartella se non esiste già

# Percorso file CSV
csv_file_path = os.path.join(output_folder, 'training_data.csv')

# Durate per ogni gesto
durations = {
    "carezza": 1.5,
    "incoraggiamento": 5.0,
    "schiaffo": 0.75
}

repetitions_per_label = 10  # Numero di ripetizioni per ogni tipo di gesto

# Dizionario per contenere tutti i dati
all_data = {}

def record_data(label, duration, repetitions):
    all_data[label] = []  # Inizializza una lista vuota per ogni tipo di gesto
    for i in range(repetitions):
        print(f"\nPreparati per la raccolta {i+1} di {repetitions} per il gesto '{label}'. Inizio tra 5 secondi...")  # Messaggio di preparazione per l'utente
        for countdown in range(5, 0, -1):
            print(f"{countdown}...")  # Countdown
            time.sleep(1)  # Pausa di un secondo tra i numeri del countdown

        print(f"Inizio registrazione per '{label}' per {duration} secondi...")  # Avviso di inizio registrazione
        acquisition = []  # Lista per memorizzare le letture di questa acquisizione
        start_time = time.time()  # Memorizza il tempo di inizio
        while time.time() - start_time < duration:  # Continua a registrare fino alla durata specificata
            line = ser.readline().decode('utf-8').strip()  # Legge una linea di dati da Arduino
            if line.isdigit():  # Verifica che la linea contenga solo cifre (distanza)
                distanza = int(line)  # Converte la stringa in un numero intero
                acquisition.append(distanza)  # Aggiunge la distanza all'acquisizione corrente
                print(f"Letto: {distanza} cm")  # Mostra la distanza letta in tempo reale

        all_data[label].append(acquisition)  # Aggiunge l'acquisizione completata alla lista del gesto
        print(f"Registrazione {i+1} per '{label}' completata.")  # Messaggio di completamento

# Avvia raccolta dati
for label, duration in durations.items():
    print(f"\n=== Inizio acquisizione per il gesto: '{label}' ===")  # Messaggio che indica l'inizio dell'acquisizione per un nuovo gesto
    record_data(label, duration, repetitions_per_label)  # Chiama la funzione di registrazione con i parametri appropriati

ser.close()  # Chiude la comunicazione seriale con Arduino

# Trova la lunghezza massima per ogni colonna
max_len = max(len(acq) for gesture in all_data.values() for acq in gesture)

# Prepara intestazioni
headers = []  # Lista per contenere le intestazioni delle colonne del CSV
for label in durations:
    for i in range(repetitions_per_label):
        headers.append(f"{label}_acq{i+1}")

# Pulisce il file CSV prima di iniziare
if os.path.exists(csv_file_path):
    os.remove(csv_file_path)  # Rimuove il file esistente per evitare di aggiungere a dati precedenti
    print(f"File CSV {csv_file_path} rimosso per una nuova sessione di acquisizione.")  # Messaggio di conferma rimozione

# Salva su CSV
with open(csv_file_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(headers)

    for row_idx in range(max_len):  # Itera attraverso tutte le righe di dati
        row = []  # Lista per contenere i valori di questa riga
        for label in durations:  # Per ogni tipo di gesto
            for acq in all_data[label]:  # Per ogni acquisizione di quel gesto
                if row_idx < len(acq):  # Se l'indice è all'interno dell'acquisizione
                    row.append(acq[row_idx])  # Aggiungi il valore alla riga
                else:
                    row.append("")  # Valore vuoto se la colonna è più corta
        writer.writerow(row)  # Scrive la riga nel file CSV

print(f"\nTutti i dati sono stati salvati in formato colonne separate su '{csv_file_path}'.")  # Messaggio finale di conferma
