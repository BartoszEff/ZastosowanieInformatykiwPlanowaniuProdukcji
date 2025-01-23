import ctypes
import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from ctypes import Structure, c_int

from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QDialog
from PyQt5 import QtCore

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

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

# Zmienne globalne
liczba_zadan = 0
liczba_maszyn = 0
czasy_przetwarzania = None
typy_zadan = None
czasy_przezbrojen = None
kolejnosc_zadan = None
najlepsze_rozwiazanie_symulowane = None
najlepsze_rozwiazanie_brute = None

class WykresDialog(QDialog):
    def __init__(self, fig, title):
        super().__init__()
        self.setWindowTitle(title)
        self.canvas = FigureCanvas(fig)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.resize(800, 600)

def rysuj_gantta_matplotlib(harmonogram, tytul):
    global liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen, lib

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

    fig, ax = plt.subplots(figsize=(8,4))
    if liczba_operacji == 0:
        return fig

    num_zadan = max(op.zadanie for op in lista_operacji) + 1
    cmap = plt.get_cmap('tab20', num_zadan)
    kolory = [cmap(i) for i in range(num_zadan)]

    for op in lista_operacji:
        y = liczba_maszyn - op.maszyna - 1
        czas_przezbrojenia = op.przezbrojenie_koniec - op.przezbrojenie_start
        if czas_przezbrojenia > 0:
            ax.broken_barh([(op.przezbrojenie_start, czas_przezbrojenia)], (y - 0.4, 0.8), facecolors='gray', alpha=0.5)
        czas_operacji = op.koniec - op.start
        ax.broken_barh([(op.start, czas_operacji)], (y - 0.4, 0.8), facecolors=kolory[op.zadanie])
        ax.text(op.start + czas_operacji/2, y, f'Z{op.zadanie+1}', va='center', ha='center', color='white', fontsize=8)

    ax.set_ylim(-1, liczba_maszyn)
    ax.set_xlim(0, max(op.koniec for op in lista_operacji) + 10)
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
        self.setWindowTitle("Harmonogramowanie - PyQt")

        layout = QVBoxLayout()

        # Wiersz dla liczby zadań i maszyn
        row1 = QHBoxLayout()
        row1.addWidget(QLabel("Liczba zadań:"))
        self.entry_zadania = QLineEdit()
        row1.addWidget(self.entry_zadania)

        row1.addWidget(QLabel("Liczba maszyn:"))
        self.entry_maszyny = QLineEdit()
        row1.addWidget(self.entry_maszyny)
        layout.addLayout(row1)

        # Przyciski
        btn_generuj = QPushButton("Generuj dane")
        btn_generuj.clicked.connect(self.generuj)
        layout.addWidget(btn_generuj)

        btn_sa = QPushButton("Symulowane Wyżarzanie")
        btn_sa.clicked.connect(self.uruchom_symulowane_wyzarzanie)
        layout.addWidget(btn_sa)

        btn_brute = QPushButton("Brute force")
        btn_brute.clicked.connect(self.uruchom_brute_force)
        layout.addWidget(btn_brute)

        btn_wykres_sa = QPushButton("Wykres SA")
        btn_wykres_sa.clicked.connect(self.rysuj_wykres_sa)
        layout.addWidget(btn_wykres_sa)

        btn_wykres_brute = QPushButton("Wykres Brute-force")
        btn_wykres_brute.clicked.connect(self.rysuj_wykres_brute)
        layout.addWidget(btn_wykres_brute)

        self.setLayout(layout)

    def generuj(self):
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen, kolejnosc_zadan
        global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

        liczba_zadan = int(self.entry_zadania.text())
        liczba_maszyn = int(self.entry_maszyny.text())

        czasy_przetwarzania = (c_int * (liczba_zadan * liczba_maszyn))()
        typy_zadan = (c_int * liczba_zadan)()
        czasy_przezbrojen = (c_int * liczba_maszyn)()
        kolejnosc_zadan = (c_int * liczba_zadan)(*range(liczba_zadan))
        najlepsze_rozwiazanie_symulowane = (c_int * liczba_zadan)()
        najlepsze_rozwiazanie_brute = (c_int * liczba_zadan)()

        lib.generuj_dane(liczba_zadan, liczba_maszyn, czasy_przetwarzania, typy_zadan, czasy_przezbrojen)
        QMessageBox.information(self, "Info", f"Wygenerowano dane dla {liczba_zadan} zadań i {liczba_maszyn} maszyn")

    def uruchom_symulowane_wyzarzanie(self):
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
        QMessageBox.information(self, "SA", f"Symulowane wyżarzanie wykonane\nMakespan: {wynik_makespan_sa.value}")

    def uruchom_brute_force(self):
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
        QMessageBox.information(self, "Brute Force", f"Brute force wykonane\nMakespan: {wynik_makespan_bf.value}")

    def rysuj_wykres_sa(self):
        fig = rysuj_gantta_matplotlib(najlepsze_rozwiazanie_symulowane, "Wykres SA")
        dlg = WykresDialog(fig, "Wykres SA")
        dlg.exec_()

    def rysuj_wykres_brute(self):
        fig = rysuj_gantta_matplotlib(najlepsze_rozwiazanie_brute, "Wykres Brute-force")
        dlg = WykresDialog(fig, "Wykres Brute-force")
        dlg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
