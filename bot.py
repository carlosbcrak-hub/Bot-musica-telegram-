import os
import random
import threading
import time
import requests
from flask import Flask

app = Flask(__name__)

# --- CONFIGURACIÓN ---
TELEGRAM_BOT_TOKEN = "8947376375:AAFv7JReSZ_liPoo7N9f9q_gXrMjiYNbz0I"
TELEGRAM_CHAT_ID = "2112255259"

GENEROS = ["salsa", "merengue", "trap latino", "reggaeton", "bachata"]


def enviar_alerta_telegram(mensaje):
  url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
  payload = {
      "chat_id": TELEGRAM_CHAT_ID,
      "text": mensaje,
      "parse_mode": "Markdown",
  }
  try:
    requests.post(url, json=payload)
  except Exception as e:
    print(f"Error enviando mensaje a Telegram: {e}")


def buscar_y_notificar():
  genre_elegido = random.choice(GENEROS)
  url_itunes = f"https://itunes.apple.com/search?term={genre_elegido}+2026&entity=album&limit=50&country=CO"

  try:
    response = requests.get(url_itunes)
    if response.status_code == 200:
      data = response.json()
      resultados = data.get("results", [])

      resultados_filtrados = [
          d
          for d in resultados
          if "various artists" not in d.get("artistName", "").lower()
      ]
      if not resultados_filtrados:
        resultados_filtrados = resultados

      resultados_recientes = sorted(
          resultados_filtrados,
          key=lambda x: x.get("releaseDate", ""),
          reverse=True,
      )

      if resultados_recientes:
        disco = resultados_recientes[0]
        nombre_album = disco.get("collectionName")
        artista = disco.get("artistName")
        url_disco = disco.get("collectionViewUrl")
        fecha = disco.get("releaseDate", "")[:10]

        mensaje = (
            f"🔥 *¡Estreno 24/7 ({genre_elegido.capitalize()})!*\n\n🎵"
            f" *Álbum/Single:* {nombre_album}\n👤 *Artista:* {artista}\n📅"
            f" *Lanzamiento:* {fecha}\n🎧 [Escuchar / Ver]({url_disco})"
        )

        enviar_alerta_telegram(mensaje)
        print(f"Alerta enviada: {nombre_album} - {artista}")
  except Exception as e:
    print(f"Error en la búsqueda: {e}")


# --- BUCLE EN SEGUNDO PLANO ---
def ciclo_automatico():
  time.sleep(60)
  while True:
    buscar_y_notificar()
    time.sleep(3 * 3600)  # Revisa cada 3 horas


@app.route("/")
def home():
  return "¡El Bot de Música Latino 24/7 está activo y funcionando!"


if __name__ == "__main__":
  hilo = threading.Thread(target=ciclo_automatico)
  hilo.daemon = True
  hilo.start()

  port = int(os.environ.get("PORT", 5000))
  app.run(host="0.0.0.0", port=port)
