# EthereumWheel

## Raspberry Pi

### Algemeen

Er wordt een Raspberry Pi (RPi) 4 gebruikt om de Ethereum prijs periodiek op te vragen. De RPi stuurt dan telkens twee waardes naar de Arduino via UART. De eerste waarde is de versnelling waar het wiel naar moet overschakelen. Dan is er een spatie gevolgd door de tweede waarde. Dit is een percentage (0-100) dat eengeeft hoe fel de verandering van de prijs is.

### Berekening van versnelling en verandering

De versnelling gaat simpelweg 1 omhoog wanneer de prijs omhoog gaat en 1 omlaag wanneer de prijs omlaag gaat. De versnellingen beginnen bij 1 en de maximum versnelling is standaard 6. Wanneer de versnelling 1 is en de prijs omlaag gaat, wordt de versnelling 6. Wanneer de versnelling 6 is en de prijs gaat omhoog, wordt de versnelling terug 1.

De verandering is een percentage dat aangeeft hoe fel de verandering in de prijs is. Er wordt een rolling average bijgehouden van het verschil tussen de laatste X (standaard 10) waardes. De verandering wordt dan berekend als volgt:
``` 
verandering = |huidige prijs - vorige prijs| / (2 * gemiddeld verschil) * 100
```
Bijvoorbeeld, als de huidige prijs hetzelfde is als de vorige prijs, zal verandering 0% zijn. Als het verschil tussen de huidige en vorige prijs gelijk is aan het gemiddeld verschil, zal de verandering 50% zijn. Als het verschil tussen de huidige en vorige prijs twee (of meer) keer groter is dan het gemiddeld verschil, dan zal de verandering 100% zijn. 

> Note: bij de eerste 2 updates zijn er nog niet genoeg waardes in de history om de verandering te berekenen, de verandering is dan standaard 50%.

### Gebruik

In een terminal op de RPi:

```
$ cd Desktop/EthereumWheel/rpi
$ source venv/bin/activate
(venv) $ python main.py
```

Er zijn enkele optionele parameters die meegegeven kunnen worden.
| parameter | default | beschrijving |
| --- | --- | --- |
| --gears, -g | 6 | maximum versnelling |
| --ticker, -t | "ETH-EUR" | id van de stock |
| --rate, -r | 30 | aantal seconden tussen prijs checks |
| --hist, -hi | 10 | aantal waardes in de history, wordt gebruikt om de verandering te berekenen |
| --dev, -d | probeert automatisch te verbinden | device naam van de Arduino, bv "/dev/ttyACM0", voor seriële communicatie |
| --baud, -b | 9600 | baud rate van de seriële communicatie met de Arduino

Voorbeeld (8 versnellingen, 60 seconden tussen updates, device naam "/dev/ttyACM0"):

```
(venv) $ python main.py --gears 8 --rate 60 --dev "/dev/ttyACM0"
```
