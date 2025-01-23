import ctypes
import sys
import matplotlib.pyplot as plt
from ctypes import Structure, c_int

try:
    lib = ctypes.CDLL('C:/Users/beffe/OneDrive/Desktop/ZastosowanieInformatykiwPlanowaniuProdukcji/harmonogram.dll')
except OSError as e:
    print(f"Błąd podczas ładowania biblioteki DLL: {e}")
    sys.exit(1)

class Operacja(ctypes.Structure):
    _fields_ = [
        ('maszyna', c_int),
        ('zadanie', c_int),
        ('start', c_int),
        ('koniec', c_int),
        ('przezbrojenie_start', c_int),
        ('przezbrojenie_koniec', c_int)
    ]


lib.inicjalizuj_generator.argtypes = []
lib.inicjalizuj_generator.restype = None
lib.generuj_dane.argtypes = [
    ctypes.c_int, 
    ctypes.c_int,  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int), 
    ctypes.POINTER(ctypes.c_int)   
]
lib.generuj_dane.restype = None

lib.symulowane_wyzarzanie.argtypes = [
    ctypes.POINTER(ctypes.c_int), 
    ctypes.c_int,                  
    ctypes.c_int,                 
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int)  
] 
lib.symulowane_wyzarzanie.restype = None
lib.brute_force.argtypes = [
    ctypes.POINTER(ctypes.c_int),
    ctypes.c_int,                  
    ctypes.c_int,                  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int)   
]
lib.brute_force.restype = None

lib.generuj_dane_harmonogramu.argtypes = [
    ctypes.POINTER(ctypes.c_int),  
    ctypes.c_int,                 
    ctypes.c_int,                 
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(ctypes.c_int),  
    ctypes.POINTER(Operacja)       
]
lib.generuj_dane_harmonogramu.restype = c_int
lib.inicjalizuj_generator()

while True:
    try:
        liczba_zadan = int(input("Podaj liczbę zadań: "))
        liczba_maszyn = int(input("Podaj liczbę maszyn: "))
        if liczba_zadan <= 0 or liczba_maszyn <= 0:
            print("Liczba zadań i maszyn musi być większa od zera.")
            continue
        break
    except ValueError:
        print("Proszę podać poprawną liczbę całkowitą.")
if liczba_zadan > 5 or liczba_maszyn > 8:
    can_use_brute_force = False
    print("Ze względu na ograniczenia, algorytm brute-force nie zostanie uruchomiony (maksymalnie 5 zadań i 8 maszyn).")
else:
    can_use_brute_force = True

czasy_przetwarzania = (ctypes.c_int * (liczba_zadan * liczba_maszyn))()
typy_zadan = (ctypes.c_int * liczba_zadan)()
czasy_przezbrojen = (ctypes.c_int * liczba_maszyn)()
kolejnosc_zadan = (ctypes.c_int * liczba_zadan)(*list(range(liczba_zadan)))
najlepsze_rozwiazanie_symulowane = (ctypes.c_int * liczba_zadan)()
""" najlepsze_rozwiazanie_neh = (ctypes.c_int * liczba_zadan)() """
najlepsze_rozwiazanie_brute = (ctypes.c_int * liczba_zadan)()
najlepszy_makespan_brute = ctypes.c_int()

lib.generuj_dane(
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen
)

lib.symulowane_wyzarzanie(
    kolejnosc_zadan,
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen,
    najlepsze_rozwiazanie_symulowane
)

if can_use_brute_force:
    lib.brute_force(
        kolejnosc_zadan,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        ctypes.byref(najlepszy_makespan_brute),
        najlepsze_rozwiazanie_brute
    )

max_operacji = liczba_zadan * liczba_maszyn
operacje = (Operacja * max_operacji)()

def rysuj_wykres_gantta(lista_operacji, liczba_maszyn, tytul):
    import matplotlib.patches as mpatches
    fig, ax = plt.subplots(figsize=(12, 6))

    num_zadan = max(op.zadanie for op in lista_operacji) + 1
    cmap = plt.get_cmap('tab20', num_zadan)
    kolory = [cmap(i) for i in range(num_zadan)]
    for op in lista_operacji:
        y = liczba_maszyn - op.maszyna - 1  

        czas_przezbrojenia = op.przezbrojenie_koniec - op.przezbrojenie_start
        if czas_przezbrojenia > 0:
            ax.broken_barh(
                [(op.przezbrojenie_start, czas_przezbrojenia)],
                (y - 0.4, 0.8),
                facecolors='gray',
                edgecolors='black',
                hatch='//',
                alpha=0.5
            )
            ax.text(
                op.przezbrojenie_start + czas_przezbrojenia / 2,
                y,
                'P',
                va='center',
                ha='center',
                color='black',
                fontsize=8
            )

        czas_operacji = op.koniec - op.start
        ax.broken_barh(
            [(op.start, czas_operacji)],
            (y - 0.4, 0.8),
            facecolors=kolory[op.zadanie],
            edgecolors='black'
        )
        ax.text(
            op.start + czas_operacji / 2,
            y,
            f'Z{op.zadanie+1}',
            va='center',
            ha='center',
            color='white',
            fontsize=8
        )

    ax.set_ylim(-1, liczba_maszyn)
    ax.set_xlim(0, max(op.koniec for op in lista_operacji) + 10)
    ax.set_xlabel('Czas')
    ax.set_ylabel('Maszyna')
    ax.set_yticks(range(liczba_maszyn))
    ax.set_yticklabels([f'M{m+1}' for m in range(liczba_maszyn)][::-1])
    ax.grid(True)
    legend_elements = [
        mpatches.Patch(facecolor='gray', edgecolor='black', hatch='//', label='Przezbrojenie', alpha=0.5)
    ] + [
        mpatches.Patch(facecolor=kolory[i], edgecolor='black', label=f'Zadanie {i+1}') for i in range(num_zadan)
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    plt.title(tytul)
    plt.tight_layout()
    plt.show()

liczba_operacji = lib.generuj_dane_harmonogramu(
    najlepsze_rozwiazanie_symulowane,
    liczba_zadan,
    liczba_maszyn,
    czasy_przetwarzania,
    typy_zadan,
    czasy_przezbrojen,
    operacje
)
lista_operacji = [operacje[i] for i in range(liczba_operacji)]
print("\nWykres Gantta dla symulowanego wyżarzania:")
rysuj_wykres_gantta(lista_operacji, liczba_maszyn, 'Wykres Gantta - Symulowane Wyżarzanie (z przezbrojeniami)')
lista_operacji = [operacje[i] for i in range(liczba_operacji)]
if can_use_brute_force:
    liczba_operacji = lib.generuj_dane_harmonogramu(
        najlepsze_rozwiazanie_brute,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        operacje
    )
    lista_operacji = [operacje[i] for i in range(liczba_operacji)]
    print("\nWykres Gantta dla brute-force:")
    rysuj_wykres_gantta(lista_operacji, liczba_maszyn, 'Wykres Gantta - Brute-force (z przezbrojeniami)')
