# Sistem za detekciju i gašenje požara
>Projekat iz predmeta **Ugradbeni sistemi (2024/25)** na Elektrotehničkom fakultetu Sarajevo.

Sistem omogućava kontinuirano praćenje temperature i prisustva plamena u realnom vremenu, uz mogućnost automatske reakcije aktiviranjem vodene pumpe radi gašenja požara. Pored lokalnog rada, sistem nudi daljinski nadzor i ručno upravljanje putem WiFi mreže i MQTT protokola.

---

## Arhitektura sistema
Sistem se bazira na **picoETF** (Raspberry Pi Pico) mikrokontroleru koji povezuje senzorske ulaze, aktuatore i komunikacijski modul.

```
Arhitektura Sistema
├── LOKALNI KONTROLER: picoETF (Raspberry Pi Pico)
│   ├── Senzori (Inputs):
│   │   ├── LM35 (Analogno očitavanje temperature)
│   │   └── Flame Sensor (Digitalna detekcija plamena)
│   ├── Aktuatori (Outputs):
│   │   ├── TFT Ekran (Lokalni grafički prikaz)
│   │   └── Relej + Vodena pumpa (Sistem za gašenje)
│   └── Komunikacija: WiFi (povezivanje na mrežu)
│
└── REMOTE (MQTT Broker):
    ├── Monitoring: Praćenje temperature i alarma u realnom vremenu
    └── Kontrola: Slanje komandi za pumpu i promjenu režima rada
```

---

## Funkcionalnosti

**Detekcija požara**  
Istovremeno praćenje temperature preko **LM35 senzora** i detekcija otvorenog plamena pomoću **flame senzora**.

**Automatski režim**  
Sistem samostalno aktivira pumpu čim detektuje plamen i gasi je kada opasnost prođe.

**Ručni režim**  
Korisnik putem **MQTT poruka (0 ili 1)** može direktno upravljati pumpom, što je korisno za testiranje ili specifične intervencije.

**Lokalni vizuelni prikaz**  
Na **TFT ekranu** se prikazuje trenutna temperatura, a u slučaju požara ispisuje se crveno upozorenje uz grafički simbol plamena.

**IoT integracija**  
Podaci se šalju svakih **2 sekunde** na javni MQTT broker, omogućavajući nadzor sistema s bilo koje lokacije.

---

## Korišteni hardver

| Komponenta | Pin na picoETF | Namjena |
|-------------|----------------|---------|
| LM35 | GP28 (ADC) | Mjerenje temperature okoline |
| Senzor plamena | GP14 | Digitalna detekcija vatre |
| Relej (Pumpa) | GP13 | Upravljanje aktivacijom gašenja |
| TFT SPI ekran | GP15 - GP20 | Vizuelni prikaz stanja i upozorenja |

---

## Tehnologije i komunikacija

**Jezik:**  
MicroPython

**Protokol:**  
MQTT (Broker: `broker.hivemq.com`)

---

## Pokretanje sistema

**1. Hardver**  
Spojite komponente prema tabeli pinova.

**2. Konfiguracija**  
U izvornom kodu unesite podatke za vašu **WiFi mrežu (SSID i password)**.

**3. Upload**  
Pomoću **Thonny IDE-a** prebacite glavni kod i potrebne biblioteke na Pico:

- ili934xnew  
- fontovi  
- umqtt.simple

**4. Monitoring**  
Koristite bilo koji **MQTT klijent** (npr. MQTT Explorer) i pretplatite se na: `picoETF/#`
Na taj način možete pratiti rad sistema i slati komande pumpi.
