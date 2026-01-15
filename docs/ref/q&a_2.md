# 2. Q&A

### Obiettivo dell'incontro

Approfondire i dettagli del funzionamento attuale della pipeline e definire con maggiore chiarezza i requisiti funzionali della GUI da sviluppare.
Discussione su ulteriore integrazione di un modello di Deep Learning nella pipeline.

### 1. Com’è il processo attuale?

Abbiamo eseguito step-by-step l’intero processo sul nostro computer locale, comprendendo:

* Input iniziali richiesti
* Output prodotti
* Script Python e strumenti esterni utilizzati
* Ordine e dipendenze tra le fasi

#### 1.1 Quali sono le fasi della pipeline?

Le 4 fasi principali della pipeline sono:

1. Input dei dati (cartelle con PET/MRI in formato DICOM o NIFTI)
2. Conversione (opzionale) da DICOM a NIFTI
3. MRIcroGL – automatic lesion drawing
4. FSL skull stripping
5. Esecuzione script Python (analisi quantitativa/statistica)
6. Output dei risultati (immagini (GIF e PNG), CSV, NiFTI)

La GUI dovrà:

* Guidare l’utente in ogni fase
* Permettere di interrompere il processo; (riprenderlo successivamente desiderabile)
* Tenere traccia dello stato di avanzamento

#### 1.2 Quali sono gli input?

* PET statica
* PET dinamica 
* Risonanza magnetica originale (T1 o FLAIR)
* Risonanza, T1 o FLAIR, skull-stripped (FSL bet)
* Mask della lesione (MRIcroGL)
Il disegno delle mask è realizzato tramite MRIcroGL – “automatic drawing”.
L’interfaccia dovrebbe permettere di selezionare manualmente una lesion mask oppure procedere in automatico (da implementare in un secondo momento).

```bash
.
└── sub-1
    ├── anat
    │   ├── sub-1_flair.json
    │   ├── sub-1_flair.nii.gz
    │   └── sub-1_flair_brain_3.nii.gz
    ├── ses-01
    │   └── pet
    │       ├── sub-1_ses-01_pet.json
    │       └── sub-1_ses-01_pet.nii.gz
    └── ses-02
        └── pet
            ├── sub-1_ses-02_pet.json
            └── sub-1_ses-02_pet.nii.gz
```
```bash
.
└── path-to-the-code-py-script-folder
    ├── tumor_MRI
    │   └── tumor1.nii.gz
```
| File                         | Descrizione                                                    |
| ---------------------------- | -------------------------------------------------------------- |
| `sub-1_flair.nii.gz`         | Immagine RM FLAIR originale del paziente (`anat/`)             |
| `sub-1_flair.json`           | Metadati associati alla RM FLAIR                               |
| `sub-1_flair_brain_3.nii.gz` | Versione **skull-stripped** della FLAIR (ottenuta con FSL BET) |
| `sub-1_ses-01_pet.nii.gz`    | Immagine PET statica                                  |
| `sub-1_ses-01_pet.json`      | Metadati della PET statica                            |
| `sub-1_ses-02_pet.nii.gz`    | Immagine PET dinamica (opzionale)                                |
| `sub-1_ses-02_pet.json`      | Metadati della PET dinamica (opzionale)                          |


#### 1.3. Quali sono e come devono essere visualizzati gli output?

* I file CSV possono essere aperti con applicazioni di sistema (es. Excel).
* I file NIFTI (.nii.gz) saranno visualizzati con MRIcroGL: sarebbe ideale integrarlo o quantomeno automatizzare la loro apertura dalla GUI.
* Possibile aggiunta: grafici interattivi per visualizzare slope e time to peak – desiderabile in futuro.
* È richiesto integrare la visualizzazione dei risultati NIFTI (idealmente direttamente nella GUI)
* Overlay delle mappe sul background anatomico è desiderato, se tecnicamente fattibile

### 2. Il PACS sarà coinvolto?

* In futuro si desidera aggiungere la possibilità di importare dati direttamente dal PACS per facilitare l’input (funzionalità opzionale).
* In generale, per questioni di licenze, al momento non sarà utilizzato per l'interfaccia in uscita.

### 3. Privacy e gestione dell’anonimato

* La GUI potrà trattare sia dati anonimizzati che non anonimi.
* In caso di presenza di metadati personali, l’interfaccia dovrà avvisare l’utente con un messaggio chiaro (es. alert).

### 4. Deep Learning: quando?

È stata richiesta l’integrazione di un’ulteriore pipeline basata sul Deep Learning.

* Pubblicazione prevista del paper: data ancora da definire, ma utile come possibile deadline.

