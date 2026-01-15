# 1. Q&A

### 1. A chi è destinata l’interfaccia/web application?
L’interfaccia sarà destinata esclusivamente all’utilizzo da parte dei medici.

### 2. È possibile avere una panoramica generale del funzionamento attuale e del codice?
Per una descrizione dettagliata del funzionamento e del codice attualmente disponibile, si rimanda alla documentazione tecnica, al paper allegato e al repository GitHub:
- [Paper tecnico](https://www.mdpi.com/2077-0383/13/20/6252#)
- [Repository GitHub](https://github.com/MicheleMureddu/Pediatric_fdopa_pipeline)

### 3. In che modo possiamo accedere ai dati del sistema Galiera per effettuare delle prove con l'applicazione?
Non sarà necessario accedere all’intero database dell’ospedale. Verrà messo a disposizione un dataset completamente anonimizzato, conforme alle normative sulla privacy dei pazienti.

### 4. Su quale infrastruttura sarà eseguita l’applicazione? Sarà una web app con accesso ai server del Galiera oppure un’applicazione locale destinata all’uso sui computer dei medici?
Per motivi legati alle licenze del codice, non sarà possibile interfacciarsi direttamente con il PACS (Picture Archiving and Communication System).  
Pertanto, l'applicazione e l’interfaccia grafica dovranno essere sviluppate per l'esecuzione in locale.  
Anche i dati clinici da analizzare saranno gestiti localmente, e non sarà necessaria alcuna autenticazione.

### 5. Quali tipologie di input accetterà l’interfaccia (es. immagini DICOM e NIFTI) e quali output dovrà generare (es. immagini NIFTI, file CSV)?
L’interfaccia dovrà accettare come input una o più cartelle contenenti i dati completi di uno o più pazienti, in formato DICOM o NIFTI.  
Poiché il codice attuale lavora su dati in formato NIFTI, sarà necessario includere una fase di conversione da DICOM a NIFTI.  
In output, l’applicazione restituirà per ciascun paziente una cartella contenente i dati processati e i risultati generati dal codice.

### 6. Quali funzionalità dovrà offrire l’interfaccia?
L’interfaccia dovrà:
- semplificare per il medico l’inserimento dei dati nel sistema,
- integrare in un unico flusso i processi di analisi,
- presentare i risultati in modo chiaro e intuitivo per l’utente.

### 7. Sono disponibili risorse o documentazione che possiamo consultare per comprendere meglio gli obiettivi del progetto e il contesto medico di riferimento?
Sarà utile consultare le seguenti risorse:
- [Materiali aggiuntivi e riferimenti medici](./res/)
