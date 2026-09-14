# Primjena algoritama maksimalnog toka u problemima raspodjele resursa

Projekt se odnosi na implementaciju algoritama maksimalnog toka: Ford-Fulkersonovog i Edmonds-Karp u Pythonu. Za izradu su korištene gotove biblioteke NetworkX, za modeliranje grafova, te Matplotlib, za vizualne prikaze. Pronalazak rezidualnog puta u Ford-Fulkersonovom algoritmu definiran je pretraživanjem u dubinu (engl. Depth-First Search, DFS), dok je u slučaju Edmonds-Karp algoritma definiran pretraživanjem u širinu (engl. Breadth-First Search, BFS).

Svaki graf definiran je matricom kapaciteta, pri čemu je početni tok inicijaliziran na vrijednost nula. Nakon početnog stanja slijedi prikaz svake iteracije s označenim uvećavajućim putem i rezidualnim kapacitetima, dok su prijelazi između iteracija omogućeni korištenjem strelica lijevo i desno na tipkovnici. Na kraju je prikazan konačni graf s maksimalnim kapacitetom.

Osim prikaza rada algoritma na gotovim primjerima, omogućeno je interaktivno kreiranje novih mreža tokova te uređivanje postojećih.


## Struktura projekta

- `ford_fulkerson.py` - Implementacija Ford-Fulkersonovog algoritma
- `edmonds_karp.py` - Implementacija Edmonds-Karp algoritma
- `examples.py` - Primjeri grafova
- `editor.py` - Uređivanje grafova
- `visualizer.py` - Vizualizacija rada algoritama
- `main.py` - Glavna skripta za pokretanje koda


## Pokretanje koda

```bash
pip install networkx matplotlib
py main.py
