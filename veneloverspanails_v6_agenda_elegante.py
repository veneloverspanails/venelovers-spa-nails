import streamlit as st
import sqlite3
from datetime import date, datetime, timedelta
import pandas as pd

st.set_page_config(page_title="VeneLovers Spa Nails", page_icon="Icono dorado de belleza con corazón y manicura.png", layout="wide")
DB = "venelovers_v3.db"
# Contraseña SOLO para esta prueba local. Antes de publicar se moverá a secretos seguros.
ADMIN_PASSWORD = "venelovers2026"

ACRILICAS = ["Maria Patrón", "Gina Mestra", "Leydimar Rodríguez", "Veneluz V."]
BASICAS = ["María A. Salas", "Marbelis Jimenez", "Carolina Paut"]
TODAS = ACRILICAS + BASICAS

SERVICIOS = {
    "Manicure tradicional": (25000, "Básico"),
    "Manicure semipermanente": (45000, "Básico"),
    "Pedicure tradicional": (35000, "Básico"),
    "Pedicure semipermanente": (50000, "Básico"),
    "Manos + pies semipermanente": (80000, "Básico"),
    "Base Rubber": (55000, "Básico"),
    "Retiro de semipermanente": (15000, "Básico"),
    "Uñas acrílicas": (100000, "Acrílico"),
    "Polygel": (100000, "Acrílico"),
    "Mantenimiento acrílicas / Polygel": (75000, "Acrílico"),
    "Retiro de acrílicas / gel": (25000, "Acrílico"),
}
HORAS = ["08:00","09:30","11:00","12:30","14:00","15:30","17:00"]

def conn():
    c=sqlite3.connect(DB)
    c.execute("""CREATE TABLE IF NOT EXISTS citas(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT NOT NULL, hora TEXT NOT NULL, profesional TEXT NOT NULL,
        servicio TEXT NOT NULL, cliente TEXT NOT NULL, telefono TEXT NOT NULL,
        notas TEXT DEFAULT '', origen TEXT DEFAULT 'App cliente',
        estado TEXT DEFAULT 'Reservada', creada TEXT NOT NULL,
        recordatorio_enviado INTEGER DEFAULT 0,
        UNIQUE(fecha,hora,profesional)
    )""")
    c.commit()
    return c

def profs(servicio):
    return ACRILICAS if SERVICIOS[servicio][1]=="Acrílico" else TODAS

def ocupada(fecha,hora,p):
    c=conn()
    n=c.execute("""SELECT COUNT(*) FROM citas
                   WHERE fecha=? AND hora=? AND profesional=? AND estado='Reservada'""",
                (str(fecha),hora,p)).fetchone()[0]
    c.close()
    return n>0

def hora_fmt(h):
    hh,mm=map(int,h.split(":"))
    suf="a. m." if hh<12 else "p. m."
    x=hh if 1<=hh<=12 else hh-12
    return f"{x}:{mm:02d} {suf}"

def crear_cita(fecha,hora,p,servicio,cliente,tel,notas,origen):
    c=conn()
    try:
        c.execute("""INSERT INTO citas(fecha,hora,profesional,servicio,cliente,telefono,notas,origen,creada)
                     VALUES(?,?,?,?,?,?,?,?,?)""",
                  (str(fecha),hora,p,servicio,cliente.strip(),tel.strip(),notas.strip(),origen,
                   datetime.now().isoformat(timespec="seconds")))
        c.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        c.close()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@500;600;700&family=Montserrat:wght@300;400;500;600&family=Great+Vibes&display=swap');

.stApp {
    background:
      radial-gradient(circle at 50% -10%, rgba(205,164,83,.16), transparent 32%),
      radial-gradient(circle at 10% 35%, rgba(160,112,38,.08), transparent 25%),
      linear-gradient(180deg,#050505 0%,#0a0907 48%,#11100d 100%);
    color:#f4ead0;
}
[data-testid="stHeader"] {background:rgba(0,0,0,0);}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#090806,#12100b);
    border-right:1px solid rgba(210,170,83,.25);
}
html, body, [class*="css"] {font-family:'Montserrat',sans-serif;}
h1,h2,h3 {
    font-family:'Cormorant Garamond',serif !important;
    color:#e8c878 !important;
    letter-spacing:.4px;
}
.brand {
    position:relative;
    border:1px solid rgba(224,188,101,.52);
    border-radius:24px;
    padding:34px 20px 29px;
    background:linear-gradient(145deg,rgba(25,21,13,.96),rgba(5,5,5,.98));
    text-align:center;
    margin:4px 0 25px;
    box-shadow:0 12px 45px rgba(0,0,0,.48), inset 0 0 35px rgba(201,156,61,.045);
    overflow:hidden;
}
.brand:before {
    content:"";
    position:absolute; left:12%; right:12%; top:10px; height:1px;
    background:linear-gradient(90deg,transparent,#d9b45e,transparent);
}
.brand-title {
    font-family:'Cormorant Garamond',serif;
    font-size:3.25rem;
    font-weight:700;
    letter-spacing:.18em;
    line-height:1;
    background:linear-gradient(180deg,#fff1b8 0%,#d6a947 48%,#8f6424 100%);
    -webkit-background-clip:text;
    -webkit-text-fill-color:transparent;
    text-shadow:0 0 24px rgba(232,190,91,.12);
}
.brand-script {
    font-family:'Great Vibes',cursive;
    font-size:2rem;
    color:#e6c56f;
    margin-top:8px;
}
.brand-sub {
    font-size:.83rem;
    letter-spacing:.30em;
    color:#d9c28a;
    margin-top:7px;
}
.brand-tag {
    font-family:'Cormorant Garamond',serif;
    font-size:1rem;
    letter-spacing:.18em;
    color:#ad9765;
    margin-top:13px;
}
div[data-baseweb="select"] > div,
div[data-baseweb="input"] > div,
textarea {
    background-color:rgba(18,16,12,.92) !important;
    border-color:rgba(210,170,83,.34) !important;
    border-radius:12px !important;
}
div.stButton > button {
    background:linear-gradient(135deg,#f0d68a,#bd8b32);
    color:#100c05;
    border:1px solid #efd98e;
    border-radius:14px;
    font-family:'Montserrat',sans-serif;
    font-weight:700;
    min-height:46px;
    box-shadow:0 7px 22px rgba(173,126,41,.18);
}
div.stButton > button:hover {
    border-color:#fff0b8;
    box-shadow:0 8px 28px rgba(214,171,77,.30);
}
[data-testid="stDataFrame"] {
    border:1px solid rgba(210,170,83,.28);
    border-radius:14px;
    overflow:hidden;
}
hr {border-color:rgba(210,170,83,.22);}
.note {color:#cbbd96;}
.agenda-day {
    font-family:'Cormorant Garamond',serif;
    font-size:1.45rem;
    font-weight:700;
    color:#e9c66f;
    margin:18px 0 8px;
    border-bottom:1px solid rgba(214,171,77,.28);
    padding-bottom:5px;
}
.appt-card {
    background:linear-gradient(135deg,rgba(28,24,17,.98),rgba(10,10,9,.98));
    border:1px solid rgba(215,174,78,.34);
    border-left:4px solid #d7ae4e;
    border-radius:14px;
    padding:12px 15px;
    margin:7px 0;
    box-shadow:0 7px 22px rgba(0,0,0,.25);
}
.appt-time {color:#d9bd78;font-size:.84rem;font-weight:600;letter-spacing:.04em;}
.appt-client {
    color:#fff4d3;
    font-family:'Cormorant Garamond',serif;
    font-size:1.34rem;
    font-weight:700;
    line-height:1.08;
    margin-top:2px;
}
.appt-service {color:#e2c36f;font-size:.92rem;font-weight:600;margin-top:3px;}
.appt-pro {color:#b9ad8e;font-size:.80rem;margin-top:3px;}
.free-slot {
    color:#776f5e;
    font-size:.80rem;
    border:1px dashed rgba(193,162,91,.18);
    border-radius:10px;
    padding:8px 10px;
    margin:6px 0;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="brand">
  <div class="brand-title">♡ VENELOVERS ♡</div>
  <div class="brand-script">by Veneluz Villamil</div>
  <div class="brand-sub">SPA NAILS &amp; BEAUTY</div>
  <div class="brand-tag">TU BELLEZA, NUESTRA PASIÓN</div>
</div>
""", unsafe_allow_html=True)

# Área pública y acceso privado separados. El área pública nunca consulta datos de otras clientas.
modo=st.sidebar.radio("VeneLovers", ["Reservar cita", "Acceso del spa"])

if modo=="Reservar cita":
    st.header("Reserva tu cita")
    st.caption("Solo verás disponibilidad. Los datos de otras clientas son privados.")

    servicio=st.selectbox("1. Servicio", list(SERVICIOS))
    _,_=SERVICIOS[servicio]
    st.write("Duración estimada: **1 h 30 min**")

    permitidas=profs(servicio)
    eleccion=st.selectbox("2. Manicurista", ["Cualquier manicurista disponible"]+permitidas)
    fecha=st.date_input("3. Fecha", min_value=date.today())

    if eleccion=="Cualquier manicurista disponible":
        horas=[h for h in HORAS if any(not ocupada(fecha,h,p) for p in permitidas)]
    else:
        horas=[h for h in HORAS if not ocupada(fecha,h,eleccion)]

    if not horas:
        st.warning("No hay horarios disponibles para esa selección.")
        hora=None
    else:
        hora=st.selectbox("4. Hora disponible",horas,format_func=hora_fmt)

    cliente=st.text_input("5. Nombre y apellido")
    tel=st.text_input("6. WhatsApp / teléfono")
    notas=st.text_area("Notas (opcional)")

    if st.button("Confirmar mi cita",use_container_width=True,disabled=hora is None):
        if not cliente.strip() or not tel.strip():
            st.error("Completa nombre y WhatsApp.")
        else:
            if eleccion=="Cualquier manicurista disponible":
                libres=[p for p in permitidas if not ocupada(fecha,hora,p)]
                p=libres[0] if libres else None
            else:
                p=eleccion if not ocupada(fecha,hora,eleccion) else None
            if p and crear_cita(fecha,hora,p,servicio,cliente,tel,notas,"App cliente"):
                st.success(f"✅ Cita confirmada para {fecha.strftime('%d/%m/%Y')} a las {hora_fmt(hora)} con {p}.")
                st.info("Tu horario quedó reservado. En la versión publicada podrás recibir el recordatorio por WhatsApp 30 minutos antes.")
            else:
                st.error("Ese horario acaba de ocuparse. Selecciona otro.")

else:
    if "admin_ok" not in st.session_state:
        st.session_state.admin_ok=False

    if not st.session_state.admin_ok:
        st.header("Acceso privado del spa")
        pwd=st.text_input("Contraseña",type="password")
        if st.button("Entrar"):
            if pwd==ADMIN_PASSWORD:
                st.session_state.admin_ok=True
                st.rerun()
            else:
                st.error("Contraseña incorrecta.")
    else:
        col1,col2=st.columns([4,1])
        with col1: st.header("Panel privado del spa")
        with col2:
            if st.button("Cerrar sesión"):
                st.session_state.admin_ok=False
                st.rerun()

        t1,t2,t3=st.tabs(["📅 Agenda semanal","➕ Agendar manualmente","🛠️ Administrar citas"])

        with t1:
            ref=st.date_input("Semana",value=date.today(),key="sem_admin")
            lunes=ref-timedelta(days=ref.weekday())
            dias=[lunes+timedelta(days=i) for i in range(7)]
            filtro=st.selectbox("Agenda de",["Todas"]+TODAS,key="filtro_admin")
            c=conn()
            df=pd.read_sql_query("SELECT * FROM citas WHERE estado='Reservada'",c)
            c.close()
            if filtro!="Todas" and not df.empty:
                df=df[df.profesional==filtro]
            # Agenda visual por día: nombre y servicio resaltados.
            nombres_dias=["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
            for idx,d in enumerate(dias):
                st.markdown(f'<div class="agenda-day">{nombres_dias[idx]} · {d.strftime("%d/%m/%Y")}</div>',
                            unsafe_allow_html=True)
                qdia=df[df.fecha==str(d)] if not df.empty else pd.DataFrame()
                for h in HORAS:
                    q=qdia[qdia.hora==h] if not qdia.empty else pd.DataFrame()
                    if len(q):
                        for _,r in q.iterrows():
                            st.markdown(
                                f"""<div class="appt-card">
                                <div class="appt-time">{hora_fmt(h)}</div>
                                <div class="appt-client">{r.cliente}</div>
                                <div class="appt-service">{r.servicio}</div>
                                <div class="appt-pro">con {r.profesional} · {r.telefono}</div>
                                </div>""",
                                unsafe_allow_html=True
                            )
                    else:
                        st.markdown(f'<div class="free-slot">{hora_fmt(h)} · Disponible</div>',
                                    unsafe_allow_html=True)

        with t2:
            st.subheader("Nueva cita registrada por el spa")
            s2=st.selectbox("Servicio",list(SERVICIOS),key="s2")
            p2=st.selectbox("Manicurista",profs(s2),key="p2")
            f2=st.date_input("Fecha",min_value=date.today(),key="f2")
            hd=[h for h in HORAS if not ocupada(f2,h,p2)]
            if hd:
                h2=st.selectbox("Hora",hd,format_func=hora_fmt,key="h2")
            else:
                h2=None; st.warning("Esta manicurista no tiene horarios disponibles.")
            n2=st.text_input("Nombre de la clienta",key="n2")
            w2=st.text_input("WhatsApp de la clienta",key="w2")
            no2=st.text_area("Notas",key="no2")
            if st.button("Guardar cita manual",disabled=h2 is None):
                if not n2.strip() or not w2.strip():
                    st.error("Completa nombre y WhatsApp.")
                elif crear_cita(f2,h2,p2,s2,n2,w2,no2,"Spa manual"):
                    st.success("✅ Cita manual guardada y horario bloqueado.")
                else:
                    st.error("Ese horario ya está ocupado.")

        with t3:
            c=conn()
            all_df=pd.read_sql_query("SELECT * FROM citas WHERE estado='Reservada' ORDER BY fecha,hora",c)
            c.close()
            if all_df.empty:
                st.info("No hay citas activas.")
            else:
                st.dataframe(all_df[["id","fecha","hora","profesional","servicio","cliente","telefono","origen"]],
                             use_container_width=True,hide_index=True)
                cid=st.selectbox("Cita a cancelar",all_df["id"].tolist(),
                                 format_func=lambda x: f"#{x} - "+all_df.loc[all_df.id==x,"cliente"].iloc[0])
                if st.button("Cancelar cita"):
                    c=conn(); c.execute("UPDATE citas SET estado='Cancelada' WHERE id=?",(int(cid),)); c.commit(); c.close()
                    st.success("Cita cancelada. El horario volvió a quedar disponible.")
                    st.rerun()

st.caption("V6 elegante · Agenda privada visual. WhatsApp automático se conectará al publicar.")
