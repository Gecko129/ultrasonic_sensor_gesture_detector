import pandas as pd           # Libreria per manipolazione e analisi dei dati
from sklearn.model_selection import train_test_split  # Funzione per dividere il dataset in train e test
from sklearn.ensemble import RandomForestClassifier  # Algoritmo di machine learning basato su foreste casuali
from sklearn.metrics import classification_report    # Genera report di valutazione per classificazione
from sklearn.preprocessing import LabelEncoder       # Converte etichette testuali in valori numerici
import joblib                 # Permette di salvare e caricare modelli di machine learning
import os                     # Fornisce funzionalità per interagire con il sistema operativo

# Percorso del CSV
csv_path = os.path.join("dati_registrati", "training_data.csv")

# Caricamento del CSV
df = pd.read_csv(csv_path)

# Preparazione di una lista vuota per trasformare i dati
long_data = []
for column in df.columns:     # Esaminare una per una ogni colonna del DataFrame
    label = column.split("_acq")[0]  # Estrae la label dal nome colonna
    values = df[column].dropna().tolist()  # Ottiene tutti i valori non-null dalla colonna come lista
    for v in values:          # Passiamo in rassegna su ogni valore della colonna
        if pd.notnull(v):     # Controlla che il valore sia valido (non NaN)
            long_data.append([label, float(v)])  # Aggiunge coppia [etichetta, valore] alla lista

# Creazione DataFrame da dati riorganizzati
long_df = pd.DataFrame(long_data, columns=["label", "distance"])

# Encoding delle etichette
le = LabelEncoder()  # Inizializza l'encoder per le etichette
long_df["label_encoded"] = le.fit_transform(long_df["label"])  # Applica l'encoding e aggiunge nuova colonna

# Feature e target
X = long_df[["distance"]]     # X contiene le caratteristiche (feature) per l'addestramento
y = long_df["label_encoded"]  # y contiene le classi target (etichette codificate)

# Split train/test (Divide il dataset in set di addestramento e test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)  # 80% train, 20% test

# Addestramento modello
clf = RandomForestClassifier(n_estimators=100, random_state=42)  # Inizializzazione classificatore
clf.fit(X_train, y_train)  # Addestra il modello sui dati di training

# Valutazione
y_pred = clf.predict(X_test)  # Genera previsioni usando il set di test
print("=== REPORT ===")  # Intestazione del report di valutazione
print(classification_report(y_test, y_pred, target_names=le.classes_))  # Stampa metriche dettagliate di valutazione

# Cartella per il salvataggio
output_dir = os.path.join(os.getcwd(), "modello_addestrato")  # Percorso della cartella
os.makedirs(output_dir, exist_ok=True)  # Crea la directory se non esiste già

# Salvataggio modello e encoder
model_path = os.path.join(output_dir, "modello_random_forest.pkl")  # Percorso del file del modello
encoder_path = os.path.join(output_dir, "label_encoder.pkl")  # Percorso del file dell'encoder

joblib.dump(clf, model_path)  # Salva il modello addestrato su disco
joblib.dump(le, encoder_path)  # Salva l'encoder delle etichette su disco

print(f"Modello e label encoder salvati in:\n- {model_path}\n- {encoder_path}")  # Conferma del salvataggio
