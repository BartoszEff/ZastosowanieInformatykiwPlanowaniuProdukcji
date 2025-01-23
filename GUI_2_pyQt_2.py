import ctypes
import sys
import csv

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ctypes import Structure, c_int

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialog, QFileDialog, QGridLayout
)
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


##
## ŚCIEŻKA DO BIBLIOTEKI DLL
##
dll_path = 'C:/Users/beffe/OneDrive/Desktop/ZastosowanieInformatykiwPlanowaniuProdukcji/harmonogram.dll'
try:
    lib = ctypes.CDLL(dll_path)
except OSError as e:
    print(f"Błąd podczas ładowania biblioteki DLL: {e}")
    sys.exit(1)

##
## STRUKTURA Operacja - zgodna z C
##
class Operacja(Structure):
    _fields_ = [
        ('maszyna', c_int),
        ('zadanie', c_int),
        ('start', c_int),
        ('koniec', c_int),
        ('przezbrojenie_start', c_int),
        ('przezbrojenie_koniec', c_int)
    ]

## Deklaracje funkcji z DLL:
lib.inicjalizuj_generator.argtypes = []
lib.inicjalizuj_generator.restype = None
lib.inicjalizuj_generator()

lib.generuj_dane.argtypes = [
    c_int,                 # liczba_zadan
    c_int,                 # liczba_maszyn
    ctypes.POINTER(c_int), # czasy_przetwarzania
    ctypes.POINTER(c_int), # typy_zadan
    ctypes.POINTER(c_int)  # czasy_przezbrojen
]
lib.generuj_dane.restype = None

lib.symulowane_wyzarzanie.argtypes = [
    ctypes.POINTER(c_int), # kolejnosc_zadan
    c_int,                 # liczba_zadan
    c_int,                 # liczba_maszyn
    ctypes.POINTER(c_int), # czasy_przetwarzania
    ctypes.POINTER(c_int), # typy_zadan
    ctypes.POINTER(c_int), # czasy_przezbrojen
    ctypes.POINTER(c_int), # najlepsze_rozwiazanie
    ctypes.POINTER(c_int)  # wynik_makespan
]
lib.symulowane_wyzarzanie.restype = None

lib.brute_force.argtypes = [
    ctypes.POINTER(c_int), # kolejnosc_zadan
    c_int,                 # start
    c_int,                 # liczba_zadan
    c_int,                 # liczba_maszyn
    ctypes.POINTER(c_int), # czasy_przetwarzania
    ctypes.POINTER(c_int), # typy_zadan
    ctypes.POINTER(c_int), # czasy_przezbrojen
    ctypes.POINTER(c_int), # najlepszy_makespan
    ctypes.POINTER(c_int)  # najlepsze_rozwiazanie
]
lib.brute_force.restype = None

lib.generuj_dane_harmonogramu.argtypes = [
    ctypes.POINTER(c_int), # kolejnosc_zadan
    c_int,                 # liczba_zadan
    c_int,                 # liczba_maszyn
    ctypes.POINTER(c_int), # czasy_przetwarzania
    ctypes.POINTER(c_int), # typy_zadan
    ctypes.POINTER(c_int), # czasy_przezbrojen
    ctypes.POINTER(Operacja)
]
lib.generuj_dane_harmonogramu.restype = c_int

##
## ZMIENNE GLOBALNE
##
liczba_zadan = 0
liczba_maszyn = 0
czasy_przetwarzania = None
typy_zadan = None
czasy_przezbrojen = None
kolejnosc_zadan = None
najlepsze_rozwiazanie_symulowane = None
najlepsze_rozwiazanie_brute = None

##
## DIALOG do ręcznego wprowadzenia danych (max 3×3)
##
class ManualDataDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ręczne dane (max 3 zadania, 3 maszyny)")

        layout = QVBoxLayout()

        # Pola: liczba zadań, liczba maszyn
        row_params = QHBoxLayout()
        row_params.addWidget(QLabel("Liczba zadań (max 3):"))
        self.line_zadania = QLineEdit("3")
        row_params.addWidget(self.line_zadania)

        row_params.addWidget(QLabel("Liczba maszyn (max 3):"))
        self.line_maszyny = QLineEdit("3")
        row_params.addWidget(self.line_maszyny)
        layout.addLayout(row_params)

        # Macierz czasów przetwarzania 3x3 (QGridLayout)
        grid_proc = QGridLayout()
        grid_proc.addWidget(QLabel("Czasy przetwarzania:"), 0,0,1,4)
        self.edits_czasy = []
        for i in range(3):
            row_edits = []
            for m in range(3):
                le = QLineEdit("1")  # domyślna wartość
                le.setFixedWidth(40)
                grid_proc.addWidget(QLabel(f"Z{i},M{m}:"), i+1, m*2)
                grid_proc.addWidget(le, i+1, m*2+1)
                row_edits.append(le)
            self.edits_czasy.append(row_edits)
        layout.addLayout(grid_proc)

        # Czasy przezbrojenia (3)
        row_przez = QHBoxLayout()
        row_przez.addWidget(QLabel("Czasy przezbrojenia maszyn:"))
        self.edits_przezbrojen = []
        for m in range(3):
            le = QLineEdit("2")
            le.setFixedWidth(30)
            row_przez.addWidget(QLabel(f"M{m}:"))
            row_przez.addWidget(le)
            self.edits_przezbrojen.append(le)
        layout.addLayout(row_przez)

        # Typy zadań (3)
        row_tz = QHBoxLayout()
        row_tz.addWidget(QLabel("Typy zadań:"))
        self.edits_typy_zadan = []
        for i in range(3):
            le = QLineEdit("0")
            le.setFixedWidth(30)
            row_tz.addWidget(QLabel(f"Z{i}:"))
            row_tz.addWidget(le)
            self.edits_typy_zadan.append(le)
        layout.addLayout(row_tz)

        # Przyciski OK / Cancel
        row_btn = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        row_btn.addWidget(btn_ok)
        row_btn.addWidget(btn_cancel)
        layout.addLayout(row_btn)

        self.setLayout(layout)
        self.resize(500,300)

    def getData(self):
        """
        Zwraca: (lz, lm, macierzCzasow, przezbrojen, typZadan)
        """
        lz = int(self.line_zadania.text())
        if lz>3: lz=3
        lm = int(self.line_maszyny.text())
        if lm>3: lm=3

        # macierz czasów przetwarzania
        macierz = []
        for i in range(lz):
            rowi = []
            for m in range(lm):
                val = int(self.edits_czasy[i][m].text())
                rowi.append(val)
            macierz.append(rowi)

        # czasy przezbrojenia
        przez = []
        for m in range(lm):
            val = int(self.edits_przezbrojen[m].text())
            przez.append(val)

        # typy zadan
        tZ = []
        for i in range(lz):
            val = int(self.edits_typy_zadan[i].text())
            tZ.append(val)

        return (lz, lm, macierz, przez, tZ)


##
## DIALOG/WINDOW wykresu
##
class WykresDialog(QDialog):
    def __init__(self, fig, title):
        super().__init__()
        self.setWindowTitle(title)
        self.canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.resize(800,600)

##
## Funkcja do wczytywania CSV z dodatkowymi polami
##  --- TU GŁÓWNA POPRAWA  ---
def wczytaj_parametry_i_macierz(nazwa_pliku):
    """
    Szukamy w pliku CSV kluczy:
      - Liczba zadan
      - Liczba maszyn
      - Typy zadan
      - Czasy przezbrojenia
      - Linia 'Czasy przetwarzania', a potem macierz
    """
    parametry = {}
    macierz_czasow = []

    with open(nazwa_pliku, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        naglowek = next(reader, None)  # "Parameter,Value" (możemy ignorować)

        for row in reader:
            if not row:
                continue
            # Jeśli linia to ['Czasy przetwarzania'], koniec parametrów
            if len(row) == 1 and row[0].strip() == "Czasy przetwarzania":
                break
            else:
                # GŁÓWNA ZMIANA:
                # scal wszystkie elementy row[1:] w jeden łańcuch
                if len(row) >= 2:
                    k = row[0].strip()
                    # v = row[1].strip()  # stara wersja
                    v = ",".join(x.strip() for x in row[1:])
                    parametry[k] = v

        # teraz czytamy wiersze macierzy
        for row in reader:
            if row:
                w = [int(x) for x in row]
                macierz_czasow.append(w)

    return parametry, macierz_czasow


def rysuj_gantta_matplotlib(harmonogram, tytul):
    global liczba_zadan, liczba_maszyn
    global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
    global lib

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
    lista = [operacje[i] for i in range(liczba_operacji)]

    fig, ax = plt.subplots(figsize=(8,4))
    if liczba_operacji == 0:
        return fig

    num_zadan_local = max(op.zadanie for op in lista) + 1
    cmap = plt.get_cmap('tab20', num_zadan_local)
    kolory = [cmap(i) for i in range(num_zadan_local)]

    for op in lista:
        y = liczba_maszyn - op.maszyna - 1
        czas_przezbrojenia = op.przezbrojenie_koniec - op.przezbrojenie_start
        if czas_przezbrojenia > 0:
            ax.broken_barh([(op.przezbrojenie_start, czas_przezbrojenia)],
                           (y-0.4,0.8),
                           facecolors='gray', alpha=0.5)

        czas_operacji = op.koniec - op.start
        ax.broken_barh([(op.start, czas_operacji)],
                       (y-0.4,0.8),
                       facecolors=kolory[op.zadanie])
        ax.text(op.start + czas_operacji/2, y,
                f'Z{op.zadanie+1}',
                va='center', ha='center', color='white', fontsize=8)

    ax.set_ylim(-1, liczba_maszyn)
    ax.set_xlim(0, max(op.koniec for op in lista) + 10)
    ax.set_xlabel('Czas')
    ax.set_ylabel('Maszyna')
    ax.set_yticks(range(liczba_maszyn))
    ax.set_yticklabels([f'M{m+1}' for m in range(liczba_maszyn)][::-1])
    ax.grid(True)
    plt.title(tytul)
    plt.tight_layout()
    return fig


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Harmonogramowanie: Ręczne/CSV + max 3x3")

        layout = QVBoxLayout()

        # Pola do wprowadzenia (liczba_zadan, liczba_maszyn)
        row = QHBoxLayout()
        row.addWidget(QLabel("Zadania:"))
        self.ed_zadania = QLineEdit("3")
        row.addWidget(self.ed_zadania)

        row.addWidget(QLabel("Maszyny:"))
        self.ed_maszyny = QLineEdit("3")
        row.addWidget(self.ed_maszyny)
        layout.addLayout(row)

        # Przycisk - Ręczne wprowadzenie
        btn_manual = QPushButton("Ręcznie (max 3x3)")
        btn_manual.clicked.connect(self.recznie_dane)
        layout.addWidget(btn_manual)

        # Przycisk - Wczytaj CSV
        btn_csv = QPushButton("Wczytaj z CSV")
        btn_csv.clicked.connect(self.wczytaj_csv)
        layout.addWidget(btn_csv)

        # Przycisk - generuj losowo
        btn_losowo = QPushButton("Generuj dane (losowo z DLL)")
        btn_losowo.clicked.connect(self.generuj_losowo)
        layout.addWidget(btn_losowo)

        # Przycisk - SA
        btn_sa = QPushButton("Symulowane Wyżarzanie")
        btn_sa.clicked.connect(self.uruchom_sa)
        layout.addWidget(btn_sa)

        # Przycisk - brute
        btn_bf = QPushButton("Brute force")
        btn_bf.clicked.connect(self.uruchom_brute)
        layout.addWidget(btn_bf)

        # Przycisk - wykres SA
        btn_wsa = QPushButton("Wykres SA")
        btn_wsa.clicked.connect(self.wykres_sa)
        layout.addWidget(btn_wsa)

        # Przycisk - wykres brute
        btn_wbf = QPushButton("Wykres brute")
        btn_wbf.clicked.connect(self.wykres_brute)
        layout.addWidget(btn_wbf)

        self.setLayout(layout)
        self.resize(400,200)


    def recznie_dane(self):
        """
        Otwiera dialog ManualDataDialog, wprowadza dane max 3x3.
        Zapisuje je do globalnych tablic c_int, tak samo jak w generuj_losowo/wczytaj_csv.
        """
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
        global kolejnosc_zadan
        global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

        dlg = ManualDataDialog()
        if dlg.exec_() == QDialog.Accepted:
            (lz, lm, macierz, przez, tz) = dlg.getData()

            liczba_zadan = lz
            liczba_maszyn = lm
            self.ed_zadania.setText(str(lz))
            self.ed_maszyny.setText(str(lm))

            czasy_przetwarzania = (c_int * (lz*lm))()
            typy_zadan = (c_int * lz)()
            czasy_przezbrojen = (c_int * lm)()
            kolejnosc_zadan = (c_int * lz)(*range(lz))

            najlepsze_rozwiazanie_symulowane = (c_int * lz)()
            najlepsze_rozwiazanie_brute = (c_int * lz)()

            idx = 0
            for i in range(lz):
                for m in range(lm):
                    czasy_przetwarzania[idx] = macierz[i][m]
                    idx += 1

            for m in range(lm):
                czasy_przezbrojen[m] = przez[m]

            for i in range(lz):
                typy_zadan[i] = tz[i]

            QMessageBox.information(self, "Ręczne", "Dane wprowadzone ręcznie OK")


    def wczytaj_csv(self):
        """
        Wczytuje z CSV parametry + macierz do globalnych tablic.
        """
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
        global kolejnosc_zadan
        global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

        fname, _ = QFileDialog.getOpenFileName(self, "Wybierz plik CSV", "", "CSV Files (*.csv)")
        if not fname:
            return

        parametry, macierz = wczytaj_parametry_i_macierz(fname)
        print("DEBUG parametry =", parametry)  # debug
        print("DEBUG macierz =", macierz)      # debug

        liczba_zadan = int(parametry.get("Liczba zadan","3"))
        liczba_maszyn = int(parametry.get("Liczba maszyn","3"))

        self.ed_zadania.setText(str(liczba_zadan))
        self.ed_maszyny.setText(str(liczba_maszyn))

        czasy_przetwarzania = (c_int * (liczba_zadan * liczba_maszyn))()
        typy_zadan = (c_int * liczba_zadan)()
        czasy_przezbrojen = (c_int * liczba_maszyn)()
        kolejnosc_zadan = (c_int * liczba_zadan)(*range(liczba_zadan))

        najlepsze_rozwiazanie_symulowane = (c_int * liczba_zadan)()
        najlepsze_rozwiazanie_brute = (c_int * liczba_zadan)()

        # typy zadan
        if "Typy zadan" in parametry:
            arr = parametry["Typy zadan"].split(',')
            for i, val in enumerate(arr):
                if i < liczba_zadan:
                    typy_zadan[i] = int(val)

        # czasy przezbrojenia
        if "Czasy przezbrojenia" in parametry:
            arr = parametry["Czasy przezbrojenia"].split(',')
            for m, val in enumerate(arr):
                if m < liczba_maszyn:
                    czasy_przezbrojen[m] = int(val)

        # macierz czasów przetwarzania
        idx = 0
        for i in range(liczba_zadan):
            if i < len(macierz):
                row_i = macierz[i]
                for m, val in enumerate(row_i):
                    if m < liczba_maszyn:
                        czasy_przetwarzania[idx] = val
                        idx+=1

        # Debug
        dbg_typy = [typy_zadan[i] for i in range(liczba_zadan)]
        dbg_przez = [czasy_przezbrojen[m] for m in range(liczba_maszyn)]
        dbg_czasy = [czasy_przetwarzania[i] for i in range(liczba_zadan * liczba_maszyn)]
        print("DEBUG: final typy_zadan =", dbg_typy)
        print("DEBUG: final czasy_przezbrojen =", dbg_przez)
        print("DEBUG: final czasy_przetwarzania =", dbg_czasy)

        QMessageBox.information(self, "CSV", f"Wczytano dane z pliku: {fname}")


    def generuj_losowo(self):
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen, kolejnosc_zadan
        global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

        liczba_zadan = int(self.ed_zadania.text())
        liczba_maszyn = int(self.ed_maszyny.text())

        czasy_przetwarzania = (c_int * (liczba_zadan * liczba_maszyn))()
        typy_zadan = (c_int * liczba_zadan)()
        czasy_przezbrojen = (c_int * liczba_maszyn)()
        kolejnosc_zadan = (c_int * liczba_zadan)(*range(liczba_zadan))

        najlepsze_rozwiazanie_symulowane = (c_int * liczba_zadan)()
        najlepsze_rozwiazanie_brute = (c_int * liczba_zadan)()

        lib.generuj_dane(
            liczba_zadan,
            liczba_maszyn,
            czasy_przetwarzania,
            typy_zadan,
            czasy_przezbrojen
        )
        QMessageBox.information(self,"Losowe",
            f"Wygenerowano dane losowo dla {liczba_zadan}x{liczba_maszyn}")

    def uruchom_sa(self):
        wynik = c_int()
        lib.symulowane_wyzarzanie(
            kolejnosc_zadan,
            liczba_zadan,
            liczba_maszyn,
            czasy_przetwarzania,
            typy_zadan,
            czasy_przezbrojen,
            najlepsze_rozwiazanie_symulowane,
            ctypes.byref(wynik)
        )
        QMessageBox.information(self, "SA", 
            f"SA OK, makespan={wynik.value}")

    def uruchom_brute(self):
        wynik = c_int()
        lib.brute_force(
            kolejnosc_zadan,
            0,
            liczba_zadan,
            liczba_maszyn,
            czasy_przetwarzania,
            typy_zadan,
            czasy_przezbrojen,
            ctypes.byref(wynik),
            najlepsze_rozwiazanie_brute
        )
        QMessageBox.information(self, "Brute",
            f"Brute OK, makespan={wynik.value}")

    def wykres_sa(self):
        fig = rysuj_gantta_matplotlib(najlepsze_rozwiazanie_symulowane, "Wykres SA")
        dlg = WykresDialog(fig, "Wykres SA")
        dlg.exec_()

    def wykres_brute(self):
        fig = rysuj_gantta_matplotlib(najlepsze_rozwiazanie_brute, "Wykres Brute")
        dlg = WykresDialog(fig, "Wykres Brute")
        dlg.exec_()


if __name__=="__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
