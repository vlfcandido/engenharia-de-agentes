"""Templates do site gerado (usados no MODO DEMO).

Em modo real, e o LLM que escreve o HTML/CSS. No demo, geramos um site bonito e
deterministico aqui pra voce ver o resultado sem gastar token. O nome do negocio
vem dos DADOS (entrada de formulario) e e injetado com seguranca.
"""

from __future__ import annotations

import html


def css() -> str:
    return """\
:root { --cafe:#5b3a29; --creme:#f5efe6; --dourado:#c69c6d; --texto:#2e2218; }
* { margin:0; padding:0; box-sizing:border-box; }
body { font-family:'Segoe UI',system-ui,sans-serif; color:var(--texto); background:var(--creme); line-height:1.6; }
.container { max-width:1080px; margin:0 auto; padding:0 24px; }
header { position:sticky; top:0; background:rgba(245,239,230,.9); backdrop-filter:blur(8px); border-bottom:1px solid #e3d8c8; z-index:10; }
nav { display:flex; justify-content:space-between; align-items:center; padding:18px 24px; max-width:1080px; margin:0 auto; }
nav .logo { font-weight:800; color:var(--cafe); font-size:1.3rem; }
nav a { color:var(--texto); text-decoration:none; margin-left:22px; font-weight:500; }
nav a:hover { color:var(--cafe); }
.hero { background:linear-gradient(135deg,var(--cafe),#3a2417); color:#fff; padding:110px 0; text-align:center; }
.hero h1 { font-size:3rem; margin-bottom:16px; }
.hero p { font-size:1.25rem; opacity:.92; max-width:620px; margin:0 auto 28px; }
.btn { display:inline-block; background:var(--dourado); color:#2e2218; padding:14px 34px; border-radius:40px; font-weight:700; text-decoration:none; transition:transform .15s; }
.btn:hover { transform:translateY(-2px); }
section { padding:80px 0; }
section h2 { font-size:2rem; color:var(--cafe); margin-bottom:14px; text-align:center; }
.sub { text-align:center; color:#7a6a55; margin-bottom:48px; }
.cards { display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:24px; }
.card { background:#fff; border-radius:16px; padding:32px; box-shadow:0 6px 24px rgba(91,58,41,.08); text-align:center; }
.card .ico { font-size:2.4rem; }
.card h3 { margin:14px 0 8px; color:var(--cafe); }
.contato { background:#fff; text-align:center; }
.contato a.email { color:var(--cafe); font-weight:700; font-size:1.2rem; text-decoration:none; }
footer { background:var(--cafe); color:#e9ddcd; text-align:center; padding:28px; font-size:.9rem; }
@media(max-width:600px){ .hero h1{font-size:2.1rem;} nav a{margin-left:12px;} }
"""


def _base(nome: str, email: str, secoes: str) -> str:
    nome = html.escape(nome)
    return f"""<!DOCTYPE html>
<html lang="pt-br">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{nome}</title>
  <link rel="stylesheet" href="style.css">
</head>
<body>
  <header><nav class="container-nav">
    <span class="logo">☕ {nome}</span>
    <div><a href="#sobre">Sobre</a><a href="#servicos">Cardapio</a><a href="#contato">Contato</a></div>
  </nav></header>
{secoes}
  <footer>© {nome} — feito por um time de agentes de IA 🤖</footer>
</body>
</html>
"""


def pagina_html(nome: str, email: str, completo: bool) -> str:
    """Gera o index.html. `completo=False` = versao do round 1 (sem contato/cardapio)."""
    hero = f"""  <section class="hero">
    <div class="container">
      <h1>Bem-vindo ao {html.escape(nome)}</h1>
      <p>O cafe artesanal que aquece o seu dia. Graos selecionados, ambiente aconchegante.</p>
      <a class="btn" href="#contato">Venha tomar um cafe</a>
    </div>
  </section>
"""
    sobre = """  <section id="sobre" class="container">
    <h2>Sobre nos</h2>
    <p class="sub">Uma cafeteria de bairro com alma. Torramos nossos proprios graos e servimos com carinho desde o primeiro gole.</p>
  </section>
"""
    if not completo:
        # Round 1: faltam cardapio e contato de proposito (o revisor vai reprovar).
        return _base(nome, email, hero + sobre)

    servicos = """  <section id="servicos" style="background:#efe6d8;">
    <div class="container">
      <h2>Cardapio</h2>
      <p class="sub">Do espresso ao bolo da casa.</p>
      <div class="cards">
        <div class="card"><div class="ico">☕</div><h3>Cafes especiais</h3><p>Espresso, coado, cappuccino e mais.</p></div>
        <div class="card"><div class="ico">🥐</div><h3>Quitutes</h3><p>Paes, bolos e doces fresquinhos.</p></div>
        <div class="card"><div class="ico">🌱</div><h3>Opcoes veganas</h3><p>Leites vegetais e doces sem lactose.</p></div>
      </div>
    </div>
  </section>
"""
    contato = f"""  <section id="contato" class="contato">
    <div class="container">
      <h2>Contato</h2>
      <p class="sub">Quer reservar uma mesa ou pedir um orcamento de evento?</p>
      <a class="email" href="mailto:{html.escape(email)}">{html.escape(email)}</a>
      <p style="margin-top:24px;"><a class="btn" href="mailto:{html.escape(email)}">Fale com a gente</a></p>
    </div>
  </section>
"""
    return _base(nome, email, hero + sobre + servicos + contato)
