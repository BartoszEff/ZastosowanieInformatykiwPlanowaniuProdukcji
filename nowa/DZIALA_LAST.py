import ctypes
import sys
import csv
import math

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from ctypes import Structure, c_int, c_double
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QDialog,
    QFileDialog, QGridLayout, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


dll_path = r"C:\Users\beffe\OneDrive\Desktop\ZastosowanieInformatykiwPlanowaniuProdukcji\nowa\harmonogram.dll"
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

lib.symulowane_wyzarzanie_param.argtypes = [
    ctypes.POINTER(c_int),
    c_int,
    c_int,
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    ctypes.POINTER(c_int),
    c_double,
    c_double,
    c_double,
    c_int,
    c_int,
    c_int
]
lib.symulowane_wyzarzanie_param.restype = None

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
czasy_przetwarzania = None
typy_zadan = None
czasy_przezbrojen = None
kolejnosc_zadan = None
najlepsze_rozwiazanie_symulowane = None
najlepsze_rozwiazanie_brute = None
data_loaded = False  
def wczytaj_parametry_i_macierz(csv_path):
    parametry = {}
    macierz_czasow = []
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f, delimiter=',')
        naglowek = next(reader, None)
        for row in reader:
            if not row:
                continue
            if len(row) == 1 and row[0].strip() == "Czasy przetwarzania":
                break
            else:
                if len(row) >= 2:
                    k = row[0].strip()
                    v = ",".join(x.strip() for x in row[1:])
                    parametry[k] = v

    
        for row in reader:
            if row:
                try:
                    arr = [int(x) for x in row]
                except ValueError:
                    QMessageBox.warning(None, "Błąd w pliku CSV", "Wszystkie wartości w macierzy muszą być liczbami całkowitymi.")
                    return None, None
                macierz_czasow.append(arr)

    return parametry, macierz_czasow


class WykresDialog(QDialog):
    def __init__(self, fig, title):
        super().__init__()
        self.setWindowTitle(title)
        self.canvas = FigureCanvas(fig)
        lay = QVBoxLayout()
        lay.addWidget(self.canvas)
        self.setLayout(lay)
        self.resize(800, 600)


def rysuj_gantta_matplotlib(harmonogram, tytul):
    global liczba_zadan, liczba_maszyn
    global czasy_przetwarzania, typy_zadan, czasy_przezbrojen

    if not harmonogram or liczba_zadan == 0 or liczba_maszyn == 0 or czasy_przetwarzania is None:
        fig = plt.figure()
        plt.title("Brak danych do rysowania.")
        return fig

    max_operacji = liczba_zadan * liczba_maszyn
    OperacjaArr = Operacja * max_operacji
    operacje = OperacjaArr()

    liczba_operacji = lib.generuj_dane_harmonogramu(
        harmonogram,
        liczba_zadan,
        liczba_maszyn,
        czasy_przetwarzania,
        typy_zadan,
        czasy_przezbrojen,
        operacje
    )
    ops = [operacje[i] for i in range(liczba_operacji)]

    fig, ax = plt.subplots(figsize=(8,4))
    if not ops:
        plt.title("Brak operacji w harmonogramie.")
        return fig

    num_zadan_local = max(op.zadanie for op in ops) + 1
    cmap = plt.get_cmap('tab20', num_zadan_local)
    kolory = [cmap(i) for i in range(num_zadan_local)]

    for op in ops:
        y = liczba_maszyn - op.maszyna - 1
        czas_przezbrojenia = op.przezbrojenie_koniec - op.przezbrojenie_start
        if czas_przezbrojenia > 0:
            ax.broken_barh(
                [(op.przezbrojenie_start, czas_przezbrojenia)],
                (y-0.4, 0.8),
                facecolors='gray',
                alpha=0.5
            )
        czas_operacji = op.koniec - op.start
        ax.broken_barh(
            [(op.start, czas_operacji)],
            (y-0.4, 0.8),
            facecolors=kolory[op.zadanie]
        )
        ax.text(
            op.start + czas_operacji/2,
            y,
            f"Z{op.zadanie+1}",
            va='center', ha='center',
            color='white', fontsize=8
        )

    ax.set_ylim(-1, liczba_maszyn)
    ax.set_xlim(0, max(o.koniec for o in ops) + 10)
    ax.set_xlabel("Czas")
    ax.set_ylabel("Maszyna")
    ax.set_yticks(range(liczba_maszyn))
    ax.set_yticklabels([f"M{m+1}" for m in range(liczba_maszyn)][::-1])
    ax.grid(True)
    plt.title(tytul)
    plt.tight_layout()
    return fig


class ParamSA_Dialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Parametry Wyżarzania (param)")

        lay = QVBoxLayout()
        self.edTemp = QLineEdit("1000")
        self.edTemp.editingFinished.connect(
            lambda: validate_number_input(self.edTemp, self.edTemp.text(), 100, 1e9)
        )

        self.edChlodz = QLineEdit("0.95")
        self.edChlodz.editingFinished.connect(
            lambda: validate_number_input_float(self.edChlodz, self.edChlodz.text(), 0.01, 0.9999)
        )

        self.edMinTemp = QLineEdit("0.05")
        self.edMinTemp.editingFinished.connect(
            lambda: validate_number_input_float(self.edMinTemp, self.edMinTemp.text(), 0.01, 999999)
        )

        self.edMaxIter = QLineEdit("1000")
        self.edMaxIter.editingFinished.connect(
            lambda: validate_number_input(self.edMaxIter, self.edMaxIter.text(), 500, 9999999)
        )

        self.edBrakPop = QLineEdit("0")
        self.edBrakPop.editingFinished.connect(
            lambda: validate_number_input(self.edBrakPop, self.edBrakPop.text(), 0, 9999999)
        )

        self.edMaxBrak = QLineEdit("500")
        self.edMaxBrak.editingFinished.connect(
            lambda: validate_number_input(self.edMaxBrak, self.edMaxBrak.text(), 1, 9999999)
        )

        form = QHBoxLayout()
        colL = QVBoxLayout()
        colR = QVBoxLayout()

        colL.addWidget(QLabel("Temp (≥100):"))
        colL.addWidget(QLabel("Chłodzenie (≥0.01):"))
        colL.addWidget(QLabel("Min. Temp (≥0.01):"))
        colL.addWidget(QLabel("Maks iter (≥500):"))
        colL.addWidget(QLabel("Brak poprawy (≥0):"))
        colL.addWidget(QLabel("Maks brak poprawy (≥1):"))

        colR.addWidget(self.edTemp)
        colR.addWidget(self.edChlodz)
        colR.addWidget(self.edMinTemp)
        colR.addWidget(self.edMaxIter)
        colR.addWidget(self.edBrakPop)
        colR.addWidget(self.edMaxBrak)

        form.addLayout(colL)
        form.addLayout(colR)
        lay.addLayout(form)

        row_btn = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        row_btn.addWidget(btn_ok)
        row_btn.addWidget(btn_cancel)
        lay.addLayout(row_btn)

        self.setLayout(lay)
        self.resize(320, 250)

    def accept(self):
        try:
            tempVal = float(self.edTemp.text())
            minVal = float(self.edMinTemp.text())
        except ValueError:
            QMessageBox.warning(self, "Błąd parametrów", "Pola Temp i Min.Temp muszą być liczbami.")
            return
        if minVal >= tempVal:
            QMessageBox.warning(
                self,
                "Błąd parametrów",
                "Minimalna temperatura nie może być większa ani równa temperaturze początkowej."
            )
            return

        super().accept()

    def getParams(self):
        return (
            float(self.edTemp.text()),
            float(self.edChlodz.text()),
            float(self.edMinTemp.text()),
            int(self.edMaxIter.text()),
            int(self.edBrakPop.text()),
            int(self.edMaxBrak.text())
        )



class ManualDataDialog(QDialog):
    def __init__(self, liczba_zadan, liczba_maszyn):
        super().__init__()
        self.setWindowTitle("Ręczne wpisanie danych")

        self.liczba_zadan = liczba_zadan
        self.liczba_maszyn = liczba_maszyn

        layout = QVBoxLayout()
        grid_proc = QGridLayout()
        grid_proc.addWidget(QLabel("Czasy przetwarzania:"), 0, 0, 1, 2*self.liczba_maszyn)
        self.edits_czasy = []
        for i in range(self.liczba_zadan):
            row_edits = []
            for m in range(self.liczba_maszyn):
                le = QLineEdit("1")
                le.setFixedWidth(40)
                le.editingFinished.connect(lambda le=le: validate_number_input(le, le.text(), 1, 100))
                label = QLabel(f"Z{i},M{m}:")
                grid_proc.addWidget(label, i+1, m*2)
                grid_proc.addWidget(le, i+1, m*2+1)
                row_edits.append(le)
            self.edits_czasy.append(row_edits)
        layout.addLayout(grid_proc)
        grid_przez = QGridLayout()
        grid_przez.addWidget(QLabel("Czasy przezbrojenia maszyn:"), 0, 0, 1, 2*self.liczba_maszyn)
        self.edits_przezbrojen = []
        for m in range(self.liczba_maszyn):
            le = QLineEdit("2")
            le.setFixedWidth(40)
            le.editingFinished.connect(lambda le=le: validate_number_input(le, le.text(), 1, 100))
            label = QLabel(f"M{m}:")
            grid_przez.addWidget(label, 1, m*2)
            grid_przez.addWidget(le, 1, m*2+1)
            self.edits_przezbrojen.append(le)
        layout.addLayout(grid_przez)
        grid_tz = QGridLayout()
        grid_tz.addWidget(QLabel("Typy zadań (0 lub 1):"), 0, 0, 1, 2*self.liczba_zadan)
        self.edits_typy_zadan = []
        for i in range(self.liczba_zadan):
            le = QLineEdit("0")
            le.setFixedWidth(30)
            le.editingFinished.connect(lambda le=le: validate_number_input(le, le.text(), 0, 1))
            label = QLabel(f"Z{i}:")
            grid_tz.addWidget(label, 1, i*2)
            grid_tz.addWidget(le, 1, i*2+1)
            self.edits_typy_zadan.append(le)
        layout.addLayout(grid_tz)
        row_btn = QHBoxLayout()
        btn_ok = QPushButton("OK")
        btn_ok.clicked.connect(self.accept)
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        row_btn.addWidget(btn_ok)
        row_btn.addWidget(btn_cancel)
        layout.addLayout(row_btn)
        self.setLayout(layout)
        self.resize(400, 300)

    def getData(self):
        lz = self.liczba_zadan
        lm = self.liczba_maszyn

        macierz = []
        for i in range(lz):
            rowi = []
            for m in range(lm):
                val = int(self.edits_czasy[i][m].text())
                rowi.append(val)
            macierz.append(rowi)

        przez = []
        for m in range(lm):
            val = int(self.edits_przezbrojen[m].text())
            przez.append(val)

        tZ = []
        for i in range(lz):
            val = int(self.edits_typy_zadan[i].text())
            if val not in (0,1):
                QMessageBox.warning(self,"Błąd","Typ zadania może być tylko 0 lub 1. Ustawiam 0.")
                val = 0
            tZ.append(val)

        return (lz, lm, macierz, przez, tZ)

def validate_number_input(widget, text, min_value, max_value):
    if not text.isdigit() or not (min_value <= int(text) <= max_value):
        widget.setText(str(min_value))
        QMessageBox.warning(widget, "Niepoprawne dane", f"Dozwolone są tylko liczby całkowite od {min_value} do {max_value}.")

def validate_number_input_float(widget, text, min_value, max_value):
    try:
        value = float(text)
        if not (min_value <= value <= max_value):
            raise ValueError
    except ValueError:
        widget.setText(str(min_value))
        QMessageBox.warning(widget, "Niepoprawne dane", f"Dozwolone są tylko liczby od {min_value} do {max_value}.")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pełna funkcjonalność: CSV, Wyżarzanie param, Ręczne, Brute, itp.")

        global data_loaded
        data_loaded = False
        main_layout = QVBoxLayout()
        row = QHBoxLayout()
        row.addWidget(QLabel("Zadania:"))
        self.edZad = QLineEdit("3")
        self.edZad.editingFinished.connect(lambda: validate_number_input(self.edZad, self.edZad.text(), 2, 30))
        row.addWidget(self.edZad)

        row.addWidget(QLabel("Maszyny:"))
        self.edMasz = QLineEdit("3")
        self.edMasz.editingFinished.connect(lambda: validate_number_input(self.edMasz, self.edMasz.text(), 2, 30))
        row.addWidget(self.edMasz)

        main_layout.addLayout(row)
        btn_r = QPushButton("Ręcznie")
        btn_r.clicked.connect(self.akcja_recznie)
        main_layout.addWidget(btn_r)

        btn_c = QPushButton("Wczytaj CSV")
        btn_c.clicked.connect(self.akcja_csv)
        main_layout.addWidget(btn_c)

        btn_g = QPushButton("Generuj dane (losowo)")
        btn_g.clicked.connect(self.akcja_gen_losowo)
        main_layout.addWidget(btn_g)

        self.btn_sa_stare = QPushButton("SA (stare param)")
        self.btn_sa_stare.clicked.connect(self.sa_stare)
        main_layout.addWidget(self.btn_sa_stare)

        self.btn_sa_param = QPushButton("SA (param)")
        self.btn_sa_param.clicked.connect(self.sa_param)
        main_layout.addWidget(self.btn_sa_param)

        self.btn_bf = QPushButton("Brute force")
        self.btn_bf.clicked.connect(self.bf_run)
        main_layout.addWidget(self.btn_bf)

        self.btn_wykres_sa = QPushButton("Wykres SA")
        self.btn_wykres_sa.clicked.connect(self.wykres_sa)
        main_layout.addWidget(self.btn_wykres_sa)

        self.btn_wykres_bf = QPushButton("Wykres BruteForce")
        self.btn_wykres_bf.clicked.connect(self.wykres_bf)
        main_layout.addWidget(self.btn_wykres_bf)

        self.setLayout(main_layout)
        self.resize(500, 300)
        self.sa_makespan = None
        self.bf_makespan = None
        self.btn_sa_stare.setEnabled(False)
        self.btn_sa_param.setEnabled(False)
        self.btn_bf.setEnabled(False)
        self.btn_wykres_sa.setEnabled(False)
        self.btn_wykres_bf.setEnabled(False)


    def odblokuj_przyciski(self):
        self.btn_sa_stare.setEnabled(True)
        self.btn_sa_param.setEnabled(True)
        self.btn_bf.setEnabled(True)
        self.btn_wykres_sa.setEnabled(False)
        self.btn_wykres_bf.setEnabled(False)

    def odblokuj_przyciski_sa(self):
        self.btn_sa_stare.setEnabled(True)
        self.btn_sa_param.setEnabled(True)
        self.btn_bf.setEnabled(True)
        self.btn_wykres_sa.setEnabled(True)

    def odblokuj_przyciski_bf(self):
        self.btn_sa_stare.setEnabled(True)
        self.btn_sa_param.setEnabled(True)
        self.btn_bf.setEnabled(True)
        self.btn_wykres_bf.setEnabled(True)


    def akcja_recznie(self):
        global data_loaded
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen, kolejnosc_zadan
        global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

        lz = int(self.edZad.text())
        lm = int(self.edMasz.text())
        dlg = ManualDataDialog(lz, lm)
        if dlg.exec_() == QDialog.Accepted:
            data = dlg.getData()
            if data is None:
                return
            (lz, lm, macierz, przez, tz) = data
            liczba_zadan = lz
            liczba_maszyn = lm
            self.edZad.setText(str(lz))
            self.edMasz.setText(str(lm))
            czasy_przetwarzania = (c_int * (lz*lm))()
            typy_zadan = (c_int * lz)()
            czasy_przezbrojen = (c_int * lm)()
            kolejnosc_zadan = (c_int * lz)(*range(lz))

            idx=0
            for i in range(lz):
                for m in range(lm):
                    czasy_przetwarzania[idx] = macierz[i][m]
                    idx+=1
            for m in range(lm):
                czasy_przezbrojen[m] = przez[m]
            for i in range(lz):
                typy_zadan[i] = tz[i]

            najlepsze_rozwiazanie_symulowane = (c_int * lz)()
            najlepsze_rozwiazanie_brute = (c_int * lz)()

            data_loaded = True
            self.odblokuj_przyciski()

            QMessageBox.information(self,"Ręcznie","Dane wprowadzone OK.")

    def akcja_csv(self):
        global data_loaded
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
        global kolejnosc_zadan, najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute

        fname, _ = QFileDialog.getOpenFileName(self, "CSV", "", "CSV Files (*.csv)")
        if not fname:
            return

        parametry, macierz = wczytaj_parametry_i_macierz(fname)
        if parametry is None or macierz is None:
            QMessageBox.warning(self, "Błąd w pliku CSV", "Nie udało się wczytać parametrów lub macierzy z pliku CSV.")
            return
        liczba_zadan_str = parametry.get("Liczba zadan", "3")
        liczba_maszyn_str = parametry.get("Liczba maszyn", "3")

        if not liczba_zadan_str.isdigit() or not liczba_maszyn_str.isdigit():
            QMessageBox.warning(self, "Błąd w pliku CSV", "Liczba zadań/maszyn musi być liczbą.")
            return

        lz = int(parametry.get("Liczba zadan", "3"))
        lm = int(parametry.get("Liczba maszyn", "3"))
        self.edZad.setText(str(lz))
        self.edMasz.setText(str(lm))

        if not (1 <= lz <= 30):
            QMessageBox.warning(self, "Błąd w pliku CSV", "Liczba zadań musi być w zakresie od 1 do 10.")
            return

        if not (1 <= lm <= 30):
            QMessageBox.warning(self, "Błąd w pliku CSV", "Liczba maszyn musi być w zakresie od 1 do 10.")
            return

        if len(macierz) != lz:
            QMessageBox.warning(self, "Błąd w pliku CSV", "Liczba zadań nie zgadza się z liczbą wierszy macierzy.")
            return
        rzeczywista_liczba_kolumn = len(macierz[0]) if macierz else 0
        if rzeczywista_liczba_kolumn != lm:
            QMessageBox.warning(
                self,
                "Błąd w pliku CSV",
                f"Zadeklarowana liczba maszyn ({lm}) nie zgadza się z liczbą kolumn w macierzy ({rzeczywista_liczba_kolumn})."
            )
            return

        czasy_przetwarzania = (c_int * (lz * lm))()
        typy_zadan = (c_int * lz)()
        czasy_przezbrojen = (c_int * lm)()
        kolejnosc_zadan = (c_int * lz)(*range(lz))

        idx = 0
        for i in range(lz):
            for m in range(lm):
                try:
                    val = macierz[i][m]
                    if not isinstance(val, (int, float)):
                        QMessageBox.warning(self, "Błąd w pliku CSV", "Wszystkie wartości w macierzy muszą być liczbami.")
                        return
                    if not (1 <= val <= 100):
                        QMessageBox.warning(self, "Błąd w pliku CSV", "Czasy przetwarzania muszą być w zakresie od 1 do 100.")
                        return
                    czasy_przetwarzania[idx] = val
                    idx += 1
                except IndexError:
                    QMessageBox.warning(self, "Błąd w pliku CSV", f"Brak danych dla zadania {i + 1}, maszyny {m + 1}.")
                    return

        if "Typy zadan" in parametry:
            arr = parametry["Typy zadan"].split(',')
            for i, val in enumerate(arr):
                if i < lz:
                    if not val.isdigit():
                        QMessageBox.warning(self, "Błąd w pliku CSV", "Typy zadań mogą być tylko 0 lub 1.")
                        return
                    val = int(val)
                    if int(val) not in (0, 1):
                        QMessageBox.warning(self, "Błąd w pliku CSV", "Typy zadań mogą być tylko 0 lub 1.")
                        return
                    typy_zadan[i] = val

        if "Czasy przezbrojenia" in parametry:
            arr = parametry["Czasy przezbrojenia"].split(',')
            for m, val in enumerate(arr):
                if m < lm:
                    if not val.isdigit():
                        QMessageBox.warning(self, "Błąd w pliku CSV", "Typy zadań mogą być tylko 0 lub 1.")
                        return
                    val = int(val)
                    if not (1 <= int(val) <= 100):
                        QMessageBox.warning(self, "Błąd w pliku CSV", "Czasy przezbrojenia muszą być w zakresie od 1 do 100.")
                        return
                    czasy_przezbrojen[m] = val

        liczba_zadan = lz
        liczba_maszyn = lm
        najlepsze_rozwiazanie_symulowane = (c_int * lz)()
        najlepsze_rozwiazanie_brute = (c_int * lz)()
        data_loaded = True
        self.odblokuj_przyciski()
        QMessageBox.information(self, "CSV", f"Wczytano plik {fname}")


    def akcja_gen_losowo(self):
        global data_loaded
        global liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen, kolejnosc_zadan
        global najlepsze_rozwiazanie_symulowane, najlepsze_rozwiazanie_brute
        lz = int(self.edZad.text())
        lm = int(self.edMasz.text())
        czasy_przetwarzania = (c_int * (lz*lm))()
        typy_zadan = (c_int * lz)()
        czasy_przezbrojen = (c_int * lm)()
        kolejnosc_zadan = (c_int * lz)(*range(lz))

        lib.generuj_dane(lz, lm,
                         czasy_przetwarzania,
                         typy_zadan,
                         czasy_przezbrojen)

        najlepsze_rozwiazanie_symulowane = (c_int * lz)()
        najlepsze_rozwiazanie_brute = (c_int * lz)()
        liczba_zadan = lz
        liczba_maszyn = lm
        data_loaded = True
        self.odblokuj_przyciski()
        QMessageBox.information(self,"Losowo","Dane losowe wygenerowane.")


    def sa_stare(self):
        global data_loaded
        if not data_loaded:
            QMessageBox.warning(self,"Brak danych","Najpierw wczytaj/generuj dane.")
            return
        global kolejnosc_zadan, liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
        global najlepsze_rozwiazanie_symulowane
        wyn = c_int()
        lib.symulowane_wyzarzanie(
            kolejnosc_zadan,
            liczba_zadan,
            liczba_maszyn,
            czasy_przetwarzania,
            typy_zadan,
            czasy_przezbrojen,
            najlepsze_rozwiazanie_symulowane,
            ctypes.byref(wyn)
        )
        self.odblokuj_przyciski_sa()
        QMessageBox.information(self,"SA(stare)",f"Makespan={wyn.value}")
        self.sa_makespan = wyn.value

  
    def sa_param(self):
        global data_loaded
        if not data_loaded:
            QMessageBox.warning(self,"Brak danych","Najpierw wczytaj/generuj dane.")
            return

        dlg = ParamSA_Dialog()
        if dlg.exec_() == QDialog.Accepted:
            (temp, chlodz, minT, maxIter, brakPop, maxBrak) = dlg.getParams()
            global kolejnosc_zadan, liczba_zadan, liczba_maszyn
            global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
            global najlepsze_rozwiazanie_symulowane

            wyn = c_int()
            lib.symulowane_wyzarzanie_param(
                kolejnosc_zadan,
                liczba_zadan,
                liczba_maszyn,
                czasy_przetwarzania,
                typy_zadan,
                czasy_przezbrojen,
                najlepsze_rozwiazanie_symulowane,
                ctypes.byref(wyn),
                c_double(temp),
                c_double(chlodz),
                c_double(minT),
                c_int(maxIter),
                c_int(brakPop),
                c_int(maxBrak)
            )
            self.odblokuj_przyciski_sa()
            QMessageBox.information(self,"SA(param)",f"Makespan={wyn.value}")
            self.sa_makespan = wyn.value

    def bf_run(self):
        global data_loaded
        if not data_loaded:
            QMessageBox.warning(self,"Brak danych","Najpierw wczytaj/generuj dane.")
            return

        global kolejnosc_zadan, liczba_zadan, liczba_maszyn
        global czasy_przetwarzania, typy_zadan, czasy_przezbrojen
        global najlepsze_rozwiazanie_brute

        wyn = c_int()
        lib.brute_force(
            kolejnosc_zadan,
            0,
            liczba_zadan,
            liczba_maszyn,
            czasy_przetwarzania,
            typy_zadan,
            czasy_przezbrojen,
            ctypes.byref(wyn),
            najlepsze_rozwiazanie_brute
        )
        if liczba_maszyn >= 9 or liczba_zadan >= 6:
                QMessageBox.warning(self, "Za dużo zadań/maszyn", "Za dużo zadań/maszyn dla metody brute-force(maks 5 maszyn i 8 zadan)")
                return
        self.odblokuj_przyciski_bf()
        QMessageBox.information(self,"BruteForce",f"Makespan={wyn.value}")
        self.bf_makespan = wyn.value

    def wykres_sa(self):
        global data_loaded
        if not data_loaded:
            QMessageBox.warning(self,"Brak danych","Najpierw wczytaj/generuj dane.")
            return

        if not hasattr(self,"sa_makespan"):
            QMessageBox.warning(self,"Brak wyniku","Najpierw uruchom SA.")
            return

        fig = rysuj_gantta_matplotlib(najlepsze_rozwiazanie_symulowane,
                                      f"Wykres SA (makespan={self.sa_makespan})")
        dlg = WykresDialog(fig,"Wykres SA")
        dlg.exec_()

    def wykres_bf(self):
        global data_loaded
        if not data_loaded:
            QMessageBox.warning(self,"Brak danych","Najpierw wczytaj/generuj dane.")
            return

        if not hasattr(self,"bf_makespan"):
            QMessageBox.warning(self,"Brak wyniku","Najpierw uruchom BF.")
            return

        fig = rysuj_gantta_matplotlib(najlepsze_rozwiazanie_brute,
                                      f"Wykres BF (makespan={self.bf_makespan})")
        dlg = WykresDialog(fig,"Wykres BF")
        dlg.exec_()


if __name__=="__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
