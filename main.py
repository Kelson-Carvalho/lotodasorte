"""
LotoDaSorte - Gerador Inteligente de Apostas Lotofacil
Compativel com Kivy 2.3.1 - Pydroid 3
- Jogos salvos persistem entre sessoes (arquivo JSON)
- Botao Voltar corrigido
"""

import random
import json
import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, RoundedRectangle, Ellipse, Rectangle, Line
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import Clock

Window.clearcolor = (0.05, 0.0, 0.10, 1)

# ── Arquivo de persistência ───────────────────────────────────
SAVE_FILE = os.path.join(
    os.path.expanduser("~"), "lotodasorte_salvos.json"
)

def carregar_salvos():
    try:
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return []

def gravar_salvos(lista):
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(lista, f)
    except Exception:
        pass

# ── Paleta ───────────────────────────────────────────────────
C_FUNDO     = (0.05, 0.00, 0.10, 1)
C_CARD      = (0.12, 0.02, 0.22, 1)
C_ROXO_VIV  = (0.55, 0.10, 0.90, 1)
C_ROXO_ESC  = (0.22, 0.02, 0.40, 1)
C_BORDA     = (0.70, 0.30, 1.00, 1)
C_TEXTO     = (0.93, 0.85, 1.00, 1)
C_SUBTEXTO  = (0.68, 0.50, 0.90, 1)
C_BTN_ESC   = (0.20, 0.02, 0.38, 1)
C_VERDE     = (0.20, 0.90, 0.50, 1)
C_VERMELHO  = (1.00, 0.35, 0.35, 1)

# ── Dados históricos ─────────────────────────────────────────
MAIS_SORTEADOS = [20,10,25,11,13,24,1,4,14,3,
                  12,2,5,22,15,19,9,18,21,7,6,17,23,8,16]
PRIMOS_25 = {2,3,5,7,11,13,17,19,23}
LINHAS    = [{1,2,3,4,5},{6,7,8,9,10},{11,12,13,14,15},
             {16,17,18,19,20},{21,22,23,24,25}]

# ── Lógica ───────────────────────────────────────────────────
def contar_primos(n): return sum(1 for x in n if x in PRIMOS_25)
def contar_pares(n):  return sum(1 for x in n if x % 2 == 0)
def calcular_soma(n): return sum(n)
def tem_sequencia(n):
    s = sorted(n)
    return any(s[i+1] == s[i]+1 for i in range(len(s)-1))
def linhas_cobertas(n):
    return sum(1 for l in LINHAS if set(n) & l)

def validar(nums, fp, fpa, fs, fse, fl):
    if fp  and not (4 <= contar_primos(nums) <= 6): return False
    if fpa and not (6 <= contar_pares(nums)  <= 9): return False
    if fs  and not (170 <= calcular_soma(nums) <= 230): return False
    if fse and not tem_sequencia(nums): return False
    if fl  and linhas_cobertas(nums) < 5: return False
    return True

def gerar_jogo(fp, fpa, fs, fse, fl, ff):
    universo = list(range(1, 26))
    pesos = [25 - MAIS_SORTEADOS.index(n) for n in universo] if ff else [1]*25
    for _ in range(10000):
        escolhidos, pool = [], list(zip(universo, pesos))
        random.shuffle(pool)
        while len(escolhidos) < 15 and pool:
            total = sum(p for _, p in pool)
            r = random.uniform(0, total)
            acc = 0
            for num, p in pool:
                acc += p
                if r <= acc:
                    escolhidos.append(num)
                    pool = [(n, w) for n, w in pool if n != num]
                    break
        if len(escolhidos) == 15 and validar(escolhidos, fp, fpa, fs, fse, fl):
            return sorted(escolhidos)
    return sorted(random.sample(universo, 15))

def info_jogo(nums):
    return (contar_primos(nums), contar_pares(nums),
            15 - contar_pares(nums), calcular_soma(nums),
            tem_sequencia(nums), linhas_cobertas(nums))

# ── Helpers UI ───────────────────────────────────────────────
def make_label(txt, size=13, cor=None, bold=False,
               halign='left', markup=False, height=None):
    cor = cor or C_TEXTO
    h   = height or dp(size * 2.2)
    l   = Label(text=txt, font_size=dp(size), color=cor, bold=bold,
                halign=halign, valign='middle', markup=markup,
                size_hint_y=None, height=h)
    l.bind(size=lambda i, v: setattr(i, 'text_size', v))
    return l

def make_btn(txt, cor=None, h=dp(50), size=14):
    cor = cor or (0.40, 0.06, 0.68, 1)
    b   = Button(text=txt, font_size=dp(size), color=(0.95, 0.85, 1, 1),
                 bold=True, background_normal='', background_color=(0,0,0,0),
                 size_hint_y=None, height=h)
    def _draw(*a):
        b.canvas.before.clear()
        with b.canvas.before:
            Color(*cor)
            RoundedRectangle(pos=b.pos, size=b.size, radius=[dp(12)])
            Color(0.7, 0.3, 1.0, 0.5)
            Line(rounded_rectangle=[b.x, b.y, b.width, b.height, dp(12)],
                 width=dp(1))
    b.bind(pos=_draw, size=_draw)
    return b

def sep():
    w = Widget(size_hint_y=None, height=dp(1))
    with w.canvas:
        Color(0.5, 0.15, 0.8, 0.5)
        w._r = Rectangle(pos=w.pos, size=w.size)
    w.bind(pos=lambda i, v: setattr(i._r, 'pos', v),
           size=lambda i, v: setattr(i._r, 'size', v))
    return w

class CardBox(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw)
    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*C_CARD)
            RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(14)])
            Color(0.55, 0.15, 0.85, 0.5)
            Line(rounded_rectangle=[self.x, self.y,
                                     self.width, self.height, dp(14)],
                 width=dp(1.2))

class FundoBox(BoxLayout):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._draw, size=self._draw)
    def _draw(self, *a):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*C_FUNDO)
            Rectangle(pos=self.pos, size=self.size)

# ── Bola numérica ────────────────────────────────────────────
class Bola(FloatLayout):
    def __init__(self, numero, destaque=False, **kw):
        sz = dp(36)
        super().__init__(size_hint=(None, None), size=(sz, sz), **kw)
        self.numero   = numero
        self.destaque = destaque
        self._lbl = Label(
            text=str(numero).zfill(2),
            font_size=dp(13), bold=True,
            color=(1, 1, 1, 1),
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0},
            halign='center', valign='middle',
        )
        self._lbl.bind(size=lambda i, v: setattr(i, 'text_size', v))
        self.add_widget(self._lbl)
        self.bind(pos=self._draw, size=self._draw)

    def _draw(self, *a):
        self.canvas.before.clear()
        borda = C_BORDA if self.destaque else (0.50, 0.15, 0.80, 0.9)
        inner = C_ROXO_VIV if self.destaque else C_ROXO_ESC
        with self.canvas.before:
            Color(0, 0, 0, 0.4)
            Ellipse(pos=(self.x+dp(2), self.y-dp(2)), size=self.size)
            Color(*borda)
            Ellipse(pos=self.pos, size=self.size)
            Color(*inner)
            Ellipse(pos=(self.x+dp(2.5), self.y+dp(2.5)),
                    size=(self.width-dp(5), self.height-dp(5)))
            Color(1, 1, 1, 0.12)
            Ellipse(pos=(self.x+dp(8), self.y+self.height*0.55),
                    size=(self.width*0.4, self.height*0.22))

# ── Card de jogo ─────────────────────────────────────────────
def make_card(idx, nums, salvo=False):
    primos, pares, impares, soma, seq, lins = info_jogo(nums)
    top10 = set(MAIS_SORTEADOS[:10])

    card = CardBox(orientation='vertical', padding=dp(14),
                   spacing=dp(6), size_hint_y=None, height=dp(170))

    prefixo = "[SALVO] " if salvo else ""
    card.add_widget(make_label(f"{prefixo}Jogo {idx:02d}", size=15,
                               cor=C_BORDA, bold=True, height=dp(30)))

    sv = ScrollView(size_hint_y=None, height=dp(44),
                    do_scroll_y=False, do_scroll_x=True, bar_width=0)
    row = BoxLayout(orientation='horizontal',
                    size_hint=(None, None), height=dp(40),
                    spacing=dp(4))
    row.width = len(nums) * dp(40)
    for n in sorted(nums):
        row.add_widget(Bola(n, destaque=(n in top10)))
    sv.add_widget(row)
    card.add_widget(sv)

    card.add_widget(make_label(
        f"Primos: {primos}   Pares: {pares}   "
        f"Impares: {impares}   Soma: {soma}",
        size=12, cor=C_SUBTEXTO, height=dp(26)))

    seq_txt = "SIM" if seq else "NAO"
    card.add_widget(make_label(
        f"Sequencia: {seq_txt}   Linhas: {lins}/5   "
        f"Top10: {sum(1 for n in nums if n in top10)}",
        size=12, cor=C_SUBTEXTO, height=dp(26)))

    return card

# ── Tela Home ────────────────────────────────────────────────
class HomeScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='home', **kw)
        self.app = app
        self._build()

    def _build(self):
        root = FundoBox(orientation='vertical', padding=dp(14), spacing=dp(10))

        # Logo
        logo = CardBox(orientation='vertical', padding=dp(16), spacing=dp(2),
                       size_hint_y=None, height=dp(110))
        logo.add_widget(make_label("LOTO DA SORTE", size=24, cor=C_BORDA,
                                    bold=True, halign='center', height=dp(46)))
        logo.add_widget(make_label("Gerador Inteligente de Apostas",
                                    size=12, cor=C_SUBTEXTO,
                                    halign='center', height=dp(24)))
        logo.add_widget(make_label("Lotofacil  |  Filtros Matematicos",
                                    size=11, cor=(0.5, 0.3, 0.8, 0.8),
                                    halign='center', height=dp(22)))
        root.add_widget(logo)

        sv = ScrollView()
        sv_box = BoxLayout(orientation='vertical', size_hint_y=None,
                           spacing=dp(12), padding=[0, 0, 0, dp(20)])
        sv_box.bind(minimum_height=sv_box.setter('height'))

        # Card quantidade
        c_qtd = CardBox(orientation='vertical', padding=dp(14), spacing=dp(8),
                        size_hint_y=None, height=dp(118))
        c_qtd.add_widget(make_label("Quantidade de Jogos", size=14,
                                     cor=C_BORDA, bold=True, height=dp(28)))
        c_qtd.add_widget(sep())
        row_qtd = BoxLayout(size_hint_y=None, height=dp(46), spacing=dp(6))
        for n in [1, 3, 5, 10]:
            b = make_btn(str(n), h=dp(46))
            b.bind(on_release=lambda x, v=n: self.app.set_qtd(v, self))
            row_qtd.add_widget(b)
        c_qtd.add_widget(row_qtd)
        self.qtd_lbl = make_label("Selecionado: 5 jogos", size=11,
                                   cor=C_SUBTEXTO, height=dp(22))
        c_qtd.add_widget(self.qtd_lbl)
        sv_box.add_widget(c_qtd)

        # Card filtros
        c_fil = CardBox(orientation='vertical', padding=dp(14), spacing=dp(2),
                        size_hint_y=None, height=dp(310))
        c_fil.add_widget(make_label("Filtros Matematicos", size=14,
                                     cor=C_BORDA, bold=True, height=dp(28)))
        c_fil.add_widget(sep())
        self.switches = {}
        for key, txt in [
            ('primos', "Primos por jogo (4 a 6)"),
            ('pares',  "Pares / Impares (6 a 9p)"),
            ('soma',   "Soma total (170 a 230)"),
            ('seq',    "Sequencias (minimo 1)"),
            ('linhas', "Linhas do volante (5/5)"),
            ('freq',   "Priorizar mais sorteados"),
        ]:
            row = BoxLayout(size_hint_y=None, height=dp(40))
            row.add_widget(make_label(txt, size=12, cor=C_TEXTO, height=dp(40)))
            sw = Switch(active=True, size_hint=(None, None), size=(dp(62), dp(32)))
            sw.pos_hint = {'center_y': .5}
            row.add_widget(sw)
            self.switches[key] = sw
            c_fil.add_widget(row)
        sv_box.add_widget(c_fil)

        b_gerar = make_btn("GERAR JOGOS", cor=C_ROXO_VIV, h=dp(58), size=17)
        b_gerar.bind(on_release=lambda x: self.app.gerar_jogos())
        sv_box.add_widget(b_gerar)

        b_salvos = make_btn("Ver Jogos Salvos", cor=C_BTN_ESC, h=dp(46), size=13)
        b_salvos.bind(on_release=lambda x: self.app.ir_salvos())
        sv_box.add_widget(b_salvos)

        sv.add_widget(sv_box)
        root.add_widget(sv)
        self.add_widget(root)

# ── Tela Jogos Gerados ───────────────────────────────────────
class GerarScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='gerar', **kw)
        self.app = app
        self._build()

    def _build(self):
        root = FundoBox(orientation='vertical', padding=dp(14), spacing=dp(8))

        hdr = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        b_back = make_btn("< Voltar", cor=C_BTN_ESC, h=dp(44), size=13)
        b_back.size_hint_x = None
        b_back.width = dp(100)
        b_back.bind(on_release=self._voltar)        # <-- método direto
        hdr.add_widget(b_back)
        hdr.add_widget(make_label("Jogos Gerados", size=17,
                                   cor=C_BORDA, bold=True, height=dp(50)))
        root.add_widget(hdr)
        root.add_widget(sep())

        self.info_lbl = make_label("", size=12, cor=C_SUBTEXTO, height=dp(26))
        root.add_widget(self.info_lbl)

        self.sv = ScrollView()
        self.jogos_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                    spacing=dp(10),
                                    padding=[0, dp(4), 0, dp(16)])
        self.jogos_box.bind(minimum_height=self.jogos_box.setter('height'))
        self.sv.add_widget(self.jogos_box)
        root.add_widget(self.sv)

        btns = BoxLayout(size_hint_y=None, height=dp(54), spacing=dp(8))
        self.b_salvar = make_btn("SALVAR", cor=C_BTN_ESC, h=dp(50), size=15)
        self.b_salvar.bind(on_release=self._salvar)
        b_novo = make_btn("NOVO JOGO", cor=C_ROXO_VIV, h=dp(50), size=15)
        b_novo.bind(on_release=self._novo)
        btns.add_widget(self.b_salvar)
        btns.add_widget(b_novo)
        root.add_widget(btns)
        self.add_widget(root)

    def _voltar(self, *a):
        self.app.sm.transition = SlideTransition(direction='right')
        self.app.sm.current = 'home'

    def _salvar(self, *a):
        self.app.salvar_jogos(self)

    def _novo(self, *a):
        self.app.gerar_jogos()

    def renderizar(self, jogos, filtros_ativos):
        self.jogos_box.clear_widgets()
        self.info_lbl.text = (f"{len(jogos)} jogo(s)  |  "
                              f"{filtros_ativos} filtro(s) ativo(s)")
        self.info_lbl.color = C_SUBTEXTO
        for i, nums in enumerate(jogos, 1):
            self.jogos_box.add_widget(make_card(i, nums))
        # Volta scroll ao topo
        Clock.schedule_once(lambda dt: setattr(self.sv, 'scroll_y', 1), 0.1)

# ── Tela Jogos Salvos ────────────────────────────────────────
class JogosScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(name='jogos', **kw)
        self.app = app
        self._build()

    def _build(self):
        root = FundoBox(orientation='vertical', padding=dp(14), spacing=dp(8))

        hdr = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        b_back = make_btn("< Voltar", cor=C_BTN_ESC, h=dp(44), size=13)
        b_back.size_hint_x = None
        b_back.width = dp(100)
        b_back.bind(on_release=self._voltar)        # <-- método direto
        hdr.add_widget(b_back)
        hdr.add_widget(make_label("Jogos Salvos", size=17,
                                   cor=C_BORDA, bold=True, height=dp(50)))
        b_del = make_btn("Limpar", cor=(0.5, 0, 0.1, 1), h=dp(44), size=12)
        b_del.size_hint_x = None
        b_del.width = dp(90)
        b_del.bind(on_release=lambda x: self.app.limpar_salvos(self))
        hdr.add_widget(b_del)
        root.add_widget(hdr)
        root.add_widget(sep())

        self.total_lbl = make_label("", size=11, cor=C_SUBTEXTO, height=dp(22))
        root.add_widget(self.total_lbl)

        self.sv = ScrollView()
        self.salvos_box = BoxLayout(orientation='vertical', size_hint_y=None,
                                     spacing=dp(10),
                                     padding=[0, dp(4), 0, dp(16)])
        self.salvos_box.bind(minimum_height=self.salvos_box.setter('height'))
        self.sv.add_widget(self.salvos_box)
        root.add_widget(self.sv)
        self.add_widget(root)

    def _voltar(self, *a):
        self.app.sm.transition = SlideTransition(direction='right')
        self.app.sm.current = 'home'

    def renderizar(self, jogos):
        self.salvos_box.clear_widgets()
        self.total_lbl.text = f"Total salvo: {len(jogos)} jogo(s)"
        if not jogos:
            self.salvos_box.add_widget(
                make_label("Nenhum jogo salvo ainda.\n"
                           "Gere jogos e toque em SALVAR!",
                           size=14, cor=C_SUBTEXTO,
                           halign='center', height=dp(80)))
            return
        for i, nums in enumerate(jogos, 1):
            self.salvos_box.add_widget(make_card(i, nums, salvo=True))
        Clock.schedule_once(lambda dt: setattr(self.sv, 'scroll_y', 1), 0.1)

# ── App principal ────────────────────────────────────────────
class LotoDaSorteApp(App):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.qtd          = 5
        self.gerados      = []
        self._ultima_cfg  = (True, True, True, True, True, True)
        # Carrega salvos do arquivo ao iniciar
        self.salvos = carregar_salvos()

    def build(self):
        self.sm = ScreenManager()
        self.sm.transition = SlideTransition(direction='left')
        self.home_scr  = HomeScreen(self)
        self.gerar_scr = GerarScreen(self)
        self.jogos_scr = JogosScreen(self)
        for s in (self.home_scr, self.gerar_scr, self.jogos_scr):
            self.sm.add_widget(s)
        return self.sm

    def set_qtd(self, n, home):
        self.qtd = n
        home.qtd_lbl.text = f"Selecionado: {n} jogo{'s' if n > 1 else ''}"

    def gerar_jogos(self):
        """Lê switches da home e gera os jogos."""
        sw = self.home_scr.switches
        fp  = sw['primos'].active
        fpa = sw['pares'].active
        fs  = sw['soma'].active
        fse = sw['seq'].active
        fl  = sw['linhas'].active
        ff  = sw['freq'].active
        self._ultima_cfg = (fp, fpa, fs, fse, fl, ff)
        fativos = sum([fp, fpa, fs, fse, fl, ff])
        self.gerados = [gerar_jogo(fp, fpa, fs, fse, fl, ff)
                        for _ in range(self.qtd)]
        self.gerar_scr.renderizar(self.gerados, fativos)
        self.sm.transition = SlideTransition(direction='left')
        self.sm.current = 'gerar'

    def salvar_jogos(self, scr):
        if not self.gerados:
            scr.info_lbl.text  = "Gere jogos primeiro!"
            scr.info_lbl.color = C_VERMELHO
            return
        self.salvos.extend(self.gerados)
        gravar_salvos(self.salvos)          # <-- persiste no arquivo
        scr.info_lbl.text  = (f"Salvos! Total na carteira: "
                               f"{len(self.salvos)} jogo(s)")
        scr.info_lbl.color = C_VERDE

    def ir_salvos(self):
        self.jogos_scr.renderizar(self.salvos)
        self.sm.transition = SlideTransition(direction='left')
        self.sm.current = 'jogos'

    def limpar_salvos(self, scr):
        self.salvos = []
        gravar_salvos([])
        scr.renderizar([])

    def on_stop(self):
        # Salva automaticamente ao fechar o app
        gravar_salvos(self.salvos)


if __name__ == '__main__':
    LotoDaSorteApp().run()
