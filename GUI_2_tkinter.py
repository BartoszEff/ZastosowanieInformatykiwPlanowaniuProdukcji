import ctypes
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from ctypes import Structure, c_int
import tkinter as tk
from tkinter import messagebox

dll_path = 'C:/Users/beffe/OneDrive/Desktop/ZastosowanieInformatykiwPlanowaniuProdukcji/harmonogram.dll'
try:
    lib = ctypes.CDLL(dll_path)
except OSError as e:
    print(f"Błąd podczas ładowania biblioteki DLL: {e}")
    sys.exit(1)

class Operacja(Structure):
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
lib.inicjalizuj_generator()
lib.generuj_dane.argtypes = [
    c_int, c_int,
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int)
]
lib.generuj_dane.restype = None

lib.symulowane_wyzarzanie.argtypes = [
    ctypes.POINTER(c_int),
    c_int,
    c_int,
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int)
]
lib.symulowane_wyzarzanie.restype = None

lib.brute_force.argtypes = [
    ctypes.POINTER(c_int),
    c_int,
    c_int,
    c_int,
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int)
]
lib.brute_force.restype = None

lib.generuj_dane_harmonogramu.argtypes = [
    ctypes.POINTER(c_int),
    c_int, c_int,
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(Operacja)
]
lib.generuj_dane_harmonogramu.restype = c_int

liczba_zadan = 0
liczba_maszyn = 0
can_use_brute_force = False
czasy_przetwarzania = None
typy_zadan = None
czasy_przezbrojen = None
kolejnosc_zadan = None
najlepsze_rozwiazanie_symulowane = None
najlepsze_rozwiazanie_brute = None

def generuj():
    global liczba_zadan, liczba_maszyn
    global czasy_przetwarzania, typy_zadan, czasy_przezbrojen, kolejnosc_zadan
    global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute, can_use_brute_force

    try:
        liczba_zadan = int(entry_zadania.get())
        liczba_maszyn = int(entry_maszyny.get())
        if liczba_zadan <= 0 or liczba_maszyn <= 0:
            messagebox.showerror("Błąd", "Liczba zadań i maszyn musi być > 0.")
            return
    except ValueError:
        messagebox.showerror("Błąd", "Podaj liczby całkowite.")
        return

    if liczba_zadan > 5 or liczba_maszyn > 8:
        can_use_brute_force = False
        messagebox.showinfo("Info", "Brute force nie będzie uruchomiony (max 5 zadań i 8 maszyn).")
    else:
        can_use_brute_force = True

    czasy_przetwarzania = (c_int * (liczba_zadan * liczba_maszyn))()
    typy_zadan = (c_int * liczba_zadan)()
    czasy_przezbrojen = (c_int * liczba_maszyn)()
    kolejnosc_zadan = (c_int * liczba_zadan)(*list(range(liczba_zadan)))
    najlepsze_rozwiazanie_symulowane = (c_int * liczba_zadan)()
    najlepsze_rozwiazanie_brute = (c_int * liczba_zadan)()

    lib.generuj_dane(liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen)
    messagebox.showinfo("Sukces", f"Wygenerowano dane dla {liczba_zadan} zadań i {liczba_maszyn} maszyn.")

def uruchom_symulowane_wyzarzanie():
    if czasy_przetwarzania is None:
        messagebox.showerror("Błąd", "Najpierw generuj dane.")
        return
    wynik_makespan_sa = c_int()
    lib.symulowane_wyzarzanie(
        kolejnosc_zadan,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        najlepsze_rozwiazanie_symulowane,
        ctypes.byref(wynik_makespan_sa)
    )

    messagebox.showinfo("Symulowane Wyżarzanie", f"Wykonano Symulowane Wyżarzanie\nMakespan: {wynik_makespan_sa.value}")

def uruchom_brute_force():
    if czasy_przetwarzania is None:
        messagebox.showerror("Błąd", "Najpierw generuj dane.")
        return
    if not can_use_brute_force:
        messagebox.showerror("Błąd", "Brute force nie dostępne.")
        return
    wynik_makespan_bf = c_int()
    lib.brute_force(
        kolejnosc_zadan,
        0,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        ctypes.byref(wynik_makespan_bf),
        najlepsze_rozwiazanie_brute
    )
    messagebox.showinfo("Brute Force", f"Wykonano Brute Force \nMakespan: {wynik_makespan_bf.value}")

def rysuj_gantta_matplotlib(harmonogram, tytul):
    if czasy_przetwarzania is None:
        messagebox.showerror("Błąd", "Najpierw generuj dane i uruchom algorytm.")
        return
    max_operacji = liczba_zadan * liczba_maszyn
    operacje = (Operacja * max_operacji)()
    liczba_operacji = lib.generuj_dane_harmonogramu(
        harmonogram,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        operacje
    )
    lista_operacji = [operacje[i] for i in range(liczba_operacji)]

    fig, ax = plt.subplots(figsize=(12, 6))
    num_zadan = max(op.zadanie for op in lista_operacji) + 1
    cmap = plt.get_cmap('tab20', num_zadan)
    kolory = [cmap(i) for i in range(num_zadan)]
    import matplotlib.patches as mpatches

    for op in lista_operacji:
        y = liczba_maszyn - op.maszyna - 1
        czas_przezbrojenia = op.przezbrojenie_koniec - op.przezbrojenie_start
        if czas_przezbrojenia > 0:
            ax.broken_barh([(op.przezbrojenie_start, czas_przezbrojenia)], (y - 0.4, 0.8), facecolors='gray', edgecolors='black', hatch='//', alpha=0.5)
            ax.text(op.przezbrojenie_start + czas_przezbrojenia/2, y, 'P', va='center', ha='center', color='black', fontsize=8)

        czas_operacji = op.koniec - op.start
        ax.broken_barh([(op.start, czas_operacji)], (y - 0.4, 0.8), facecolors=kolory[op.zadanie], edgecolors='black')
        ax.text(op.start + czas_operacji/2, y, f'Z{op.zadanie+1}', va='center', ha='center', color='white', fontsize=8)

    ax.set_ylim(-1, liczba_maszyn)
    ax.set_xlim(0, max(op.koniec for op in lista_operacji) + 10)
    ax.set_xlabel('Czas')
    ax.set_ylabel('Maszyna')
    ax.set_yticks(range(liczba_maszyn))
    ax.set_yticklabels([f'M{m+1}' for m in range(liczba_maszyn)][::-1])
    ax.grid(True)
    legend_elements = [mpatches.Patch(facecolor='gray', edgecolor='black', hatch='//', label='Przezbrojenie', alpha=0.5)] + [
        mpatches.Patch(facecolor=kolory[i], edgecolor='black', label=f'Zadanie {i+1}') for i in range(num_zadan)
    ]
    ax.legend(handles=legend_elements, loc='upper right')
    plt.title(tytul)
    plt.tight_layout()

    new_window = tk.Toplevel(root)
    new_window.title(tytul)

    canvas = FigureCanvasTkAgg(fig, master=new_window)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

def rysuj_wykres_sa():
    if najlepsze_rozwiazanie_symulowane is None:
        messagebox.showerror("Błąd", "Uruchom wyżarzanie!")
        return
    rysuj_gantta_matplotlib(najlepsze_rozwiazanie_symulowane, 'Wykres Gantta - SA')

def rysuj_wykres_brute():
    if not can_use_brute_force:
        messagebox.showerror("Błąd", "Brute force nie dostępne.")
        return
    if najlepsze_rozwiazanie_brute is None or all(x == 0 for x in najlepsze_rozwiazanie_brute):
        messagebox.showerror("Błąd", "Brak danych brute force.")
        return
    rysuj_gantta_matplotlib(najlepsze_rozwiazanie_brute, 'Wykres Gantta - Brute')

root = tk.Tk()
root.title("Harmonogramowanie")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

tk.Label(frame, text="Liczba zadań:").grid(row=0, column=0, sticky='e')
entry_zadania = tk.Entry(frame)
entry_zadania.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame, text="Liczba maszyn:").grid(row=1, column=0, sticky='e')
entry_maszyny = tk.Entry(frame)
entry_maszyny.grid(row=1, column=1, padx=5, pady=5)

btn_generuj = tk.Button(frame, text="Generuj dane", command=generuj)
btn_generuj.grid(row=2, column=0, columnspan=2, pady=5)

btn_sa = tk.Button(frame, text="Symulowane Wyżarzanie", command=uruchom_symulowane_wyzarzanie)
btn_sa.grid(row=3, column=0, columnspan=2, pady=5)

btn_brute = tk.Button(frame, text="Brute force", command=uruchom_brute_force)
btn_brute.grid(row=4, column=0, columnspan=2, pady=5)

btn_wykres_sa = tk.Button(frame, text="Wykres SA", command=rysuj_wykres_sa)
btn_wykres_sa.grid(row=5, column=0, columnspan=2, pady=5)

btn_wykres_brute = tk.Button(frame, text="Wykres Brute-force", command=rysuj_wykres_brute)
btn_wykres_brute.grid(row=6, column=0, columnspan=2, pady=5)

root.mainloop()
