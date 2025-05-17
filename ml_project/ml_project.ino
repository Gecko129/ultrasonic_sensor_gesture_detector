#include <LiquidCrystal.h>    // Libreria per gestire il display LCD

// Pin collegati al display LCD 
const int rs = A0, en = A1, d4 = 7, d5 = 6, d6 = 5, d7 = 4;  // Pin di controllo del display LCD
const int trigPin = 9;        // Pin per il trig del sensore ultrasonico
const int echoPin = 10;       // Pin per ricevere l'echo dal sensore ultrasonico

LiquidCrystal lcd(rs, en, d4, d5, d6, d7);  // Inizializza l'oggetto LCD con i pin definiti

int lastDistance = -1;        // Memorizza l'ultima distanza misurata (-1 indica nessuna misurazione)
String serialInput = "";      // Buffer per memorizzare i dati ricevuti via seriale
bool nuovoRisultato = false;  // Flag per indicare quando è disponibile un nuovo risultato

void setup() {
  lcd.begin(16, 2);           // Inizializza il display LCD con 16 colonne e 2 righe
  pinMode(trigPin, OUTPUT);   // Configura il pin trig come uscita
  pinMode(echoPin, INPUT);    // Configura il pin echo come ingresso
  Serial.begin(9600);         // Inizia la comunicazione seriale
  delay(2000);                // Attende 2 secondi per la stabilizzazione del sistema
  lcd.clear();                // Resetta il display LCD
  lcd.print("Sistema pronto"); // Visualizza messaggio iniziale sul display
  Serial.println("Setup completato. Sistema pronto."); // Invia messaggio di conferma via seriale
}

void loop() {
  // Ricezione risultato da Python
  while (Serial.available()) {   // Controlla se ci sono dati disponibili sulla porta seriale
    char c = Serial.read();      // Legge un carattere dalla porta seriale
    // Gestione sia \r che \n per i terminatori linea
    if (c == '\n' || c == '\r') {        // Se è un carattere di fine linea
      if (serialInput.length() > 0) {    // E abbiamo già ricevuto dei dati
        nuovoRisultato = true;           // Segnala che è disponibile un nuovo risultato
      }
      break;       // Esci dal ciclo di lettura seriale
    }
    serialInput += c;         // Aggiungi il carattere letto al buffer
  }

  if (nuovoRisultato) {           // Se è disponibile un nuovo risultato
    Serial.print("Ricevuto da Python: ");
    Serial.println(serialInput);  // Mostra il risultato ricevuto sulla console seriale

    lcd.clear();                  // Resetta il display per mostrare il nuovo risultato
    int separatore = serialInput.indexOf(';');  // Trova la posizione del separatore nel formato "gesto;confidenza"
    if (separatore != -1) {       // Se il separatore è presente
      String gesto = serialInput.substring(0, separatore);  // Estrae il nome del gesto
      String conf = serialInput.substring(separatore + 1);  // Estrae il valore di confidenza

      lcd.setCursor(0, 0);        // Posiziona il cursore all'inizio della prima riga
      // Limito la lunghezza per adattarsi allo schermo
      if (gesto.length() > 16) {  // Se il nome del gesto è troppo lungo
        gesto = gesto.substring(0, 16);  // Tronca il nome per adattarlo al display
      }
      lcd.print("Gesto:");        // Stampa l'etichetta "Gesto:" sul display

      // Sulla riga 0, dopo "Gesto:" scrivo il gesto
      lcd.setCursor(7, 0);        // Posiziona il cursore dopo l'etichetta
      lcd.print(gesto);           // Mostra il nome del gesto rilevato

      lcd.setCursor(0, 1);        // Posiziona il cursore all'inizio della seconda riga
      lcd.print("Conf: ");        // Stampa l'etichetta "Conf: "
      lcd.print(conf);            // Mostra il valore di confidenza
      lcd.print("%");             // Aggiunge il simbolo di percentuale
    } else {
      Serial.println("Errore: formato dati ricevuto non valido.");  // Se il formato dei dati non è valido
      lcd.print("Errore dati");   // Mostra messaggio di errore sul display
    }

    serialInput = "";             // Azzera il buffer di input seriale
    nuovoRisultato = false;       // Resetta il flag di nuovo risultato

    // Mostra il risultato per 5 secondi senza misurare la distanza
    unsigned long t0 = millis();  // Memorizza il tempo corrente
    while (millis() - t0 < 5000) {  // Attende per 5 secondi
      delay(100);                 // Brevi pause durante l'attesa per non bloccare il sistema
    }

    lcd.clear();                  // Resetta il display dopo aver mostrato il risultato
    lastDistance = -1;            // Resetta l'ultima distanza per forzare aggiornamento display
  }

  // === Misura distanza ===
  long duration;                  // Variabile per memorizzare la durata dell'echo
  int distance;                   // Variabile per memorizzare la distanza calcolata

  digitalWrite(trigPin, LOW);     // Assicura che il pin trig sia LOW
  delayMicroseconds(2);           // Breve pausa per stabilizzazione
  digitalWrite(trigPin, HIGH);    // Imposta il pin trig su HIGH per emettere l'impulso
  delayMicroseconds(10);          // Mantiene l'impulso per 10 microsecondi
  digitalWrite(trigPin, LOW);     // Termina l'impulso

  duration = pulseIn(echoPin, HIGH, 25000);  // Misura il tempo di ritorno dell'echo
  distance = duration * 0.034 / 2;           // Calcola la distanza in cm

  if (distance > 0 && distance < 400) {  // Se la distanza è valida (tra 0 e 400 cm)
    if (distance != lastDistance) {      // Se la distanza è cambiata rispetto all'ultima misurazione
      lcd.clear();                       // Resetta il display
      lcd.setCursor(0, 0);               // Posiziona il cursore all'inizio della prima riga
      lcd.print("Distanza:");            // Stampa l'etichetta "Distanza:"
      lcd.setCursor(0, 1);               // Posiziona il cursore all'inizio della seconda riga
      lcd.print(distance);               // Mostra il valore della distanza
      lcd.print(" cm");                  // Aggiunge l'unità di misura
      lastDistance = distance;           // Aggiorna l'ultima distanza misurata
    }
    Serial.println(distance);     // Invia la distanza misurata via seriale (per Python)
  }

  delay(100);                     // Breve pausa tra le misurazioni (100 ms)
}
