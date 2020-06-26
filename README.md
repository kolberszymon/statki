# Statki
Nasze podejście do klasycznej gry w statki, do rozgrywania szybkich partii w sieci lokalnej w ramach projektu z przedmiotu Programowanie Sieciowe.

### Wymogi

Do poprawnego działania skryptów potrzebny jest Python 3.6+ i biblioteki biblioteki pygame i socket.
```
pip install pygame
pip install socket
```

### Informacje o projekcie

Gra została zbudowana na architekturze klient-serwer, z asynchroniczną obsługą dwóch klientów przez serwer, opartą na protokole TCP. Klienci przesyłają do serwera dane o aktualnej pozycji znacznika, fazy gry w której się znajdują, wciśniętych klawiszach oraz o tym, który gracz jest aktywny. Serwer po przetworzeniu informacji przechowuje potrzebne dane (np. położenie statków każdego z graczy) i przesyła odpowiednie dane do każdego z klientów.
W naszym projekcie znajduje się kilka plików, których funkcje i działanie opisane są poniżej:
* server.py

Plik do uruchamiania serwera.
```
server.py -ip <adresIP> -p <port>
server.py -h - pomoc
```

* run.py

Plik do uruchamiania klienta (okna gry).
```
run.py -ip <adresIP(serwera)> -p <port(serwera)>
run.py -h - pomoc
```

* game_update.py

Plik uruchamiany w pliku run.py, odpowiada za pętlę gry (rysowanie, obliczenia, sterowanie) oraz tworzy instancję klasy Network, do połączenia się z serwerem.

* network.py

Zawiera kod odpowiedzialny za połączenie się klienta z serwerem (tworzy gniazdo klienta i łączy się z gniazdem stworzonym przez serwer).

* utilities.py

Zawiera dodatkowe dane potrzebne do odpowiedniego działania gry (stworzona dla zwiększenia czytelności kodu).
  
### Jak zacząć

Wystarczy pobrać pliki z repozytorium i uruchomić w kolejności: server.py i na każdym z komputerów run.py (z odpowiednimi parametrami)

#### Sterowanie
WSAD - poruszanie znacznikiem
Enter/Return - stawianie statków, oddanie strzału (w zależności od fazy gry)

## Authors

* **Szymon Kolber**
* **Rafał Kołacz**
* **Szymon Lenart**