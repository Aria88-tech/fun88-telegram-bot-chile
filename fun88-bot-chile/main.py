from telegram import Update
from telegram.ext import (
    ApplicationBuilder, MessageHandler, filters, ContextTypes,
)
import nest_asyncio
import asyncio

nest_asyncio.apply()

# === TU TOKEN DE TELEGRAM ===
TOKEN = '7570667087:AAH3RiTfYblEzX5PK3QYTgkhkfk3Ts3tBtk'

# === ESTADOS DE USUARIOS PARA LA ENCUESTA ===
user_states = {}

# === MENSAJE DE BIENVENIDA AL GRUPO ===
async def bienvenida(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        user_id = member.id
        user_states[user_id] = "pregunta_1"

        # Bienvenida inicial
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=(
                "🙌 ¡Qué bueno tenerte aquí!\n"
                "Este grupo es para jugadores que quieren aprovechar todos los beneficios de Fun88 Chile.\n"
                "💬 Comparte tus jugadas\n"
                "🎁 Reclama tus bonos\n"
                "📲 Revisa nuestras promociones\n"
                "¡Vamos con todo!"
            )
        )

        # Comienzo de encuesta
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="👉 Para empezar, ¿qué te interesa más?\nResponde con: *Deportes* / *Tragamonedas* / *Casino en vivo* / *Juegos de mesa*",
            parse_mode="Markdown"
        )

# === MANEJAR MENSAJES DEL GRUPO ===
async def manejar_respuestas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    mensaje = update.message.text.lower()

    # --- RESPUESTA AUTOMÁTICA SI PIDEN BONOS ---
    palabras_bonos = ["bono", "bonos", "bono de bienvenida", "quiero bono", "promoción", "promociones"]
    if any(p in mensaje for p in palabras_bonos):
        await update.message.reply_text(
            "🎁 ¡Sí tenemos bonos disponibles!\n"
            "👉 Revisa todas nuestras promociones activas aquí:\n"
            "https://www.fun88chile.com/promotions\n\n"
            "Además, si aún no has depositado, puedes aprovechar nuestro bono de bienvenida.\n"
            "¡Suerte y que ganes mucho! 🍀",
            parse_mode="Markdown"
        )
        return

    # --- RESPUESTAS AUTOMÁTICAS A DEPÓSITO Y RETIRO ---
    if "cómo retirar" in mensaje or "retiro" in mensaje:
        await update.message.reply_text(
            "💸 *Cómo retirar tus ganancias de Fun88 Chile en 5 pasos:*\n\n"
            "1. Inicia sesión en tu cuenta.\n"
            "2. Ve a “Mi Cuenta” y selecciona “Retirar”.\n"
            "3. Elige tu método de retiro.\n"
            "4. Ingresa los datos y la cantidad (hasta CLP 9.000.000).\n"
            "5. Confirma y espera el procesamiento.\n\n"
            "🔐 Si se solicita verificación KYC, envíala cuanto antes para evitar demoras.",
            parse_mode="Markdown"
        )
        return

    if "cómo depositar" in mensaje or "deposito" in mensaje or "depositar" in mensaje:
        await update.message.reply_text(
            "💰 *¿Cómo hacer un depósito en Fun88 Chile?*\n\n"
            "1. Inicia sesión en tu cuenta.\n"
            "2. Ve a la sección de “Depósito”.\n"
            "3. Elige tu método de pago favorito (tarjeta, AstroPay, transferencia, etc.).\n"
            "4. Ingresa la cantidad que desees (no hay monto mínimo).\n"
            "5. Completa el pago y el saldo se acreditará al instante.\n\n"
            "🎁 ¡Aprovecha el bono de bienvenida en tu primer depósito!",
            parse_mode="Markdown"
        )
        return

    # --- RESPUESTAS A USUARIOS INCONFORMES + ALERTA PRIVADA A ADMINS ---
    palabras_inconformidad = [
        "no me llegó", "no funciona", "me robaron", "fraude", "pérdida",
        "problema", "injusto", "estafa", "reclamo", "ayuda", "soporte"
    ]
    if any(p in mensaje for p in palabras_inconformidad):
        # Responde al usuario en público
        await update.message.reply_text(
            "😞 Lamentamos mucho lo que estás experimentando.\n"
            "Queremos ayudarte lo antes posible.\n\n"
            "📩 Por favor, contacta a nuestro equipo de soporte para una atención personalizada:\n"
            "🔗 https://www.fun88chile.com/help\n\n"
            "También puedes enviarnos un mensaje privado y con gusto te asistiremos.",
            parse_mode="Markdown"
        )

        # Alerta privada a admins
        try:
            admins = await context.bot.get_chat_administrators(update.effective_chat.id)
            texto_alerta = (
                f"🚨 *ALERTA DE USUARIO INCONFORME*\n"
                f"👤 Usuario: {update.effective_user.first_name} ({update.effective_user.id})\n"
                f"🗨️ Mensaje: _{update.message.text}_\n"
                f"📍 Grupo: {update.effective_chat.title}\n\n"
                f"🔎 Atención recomendada."
            )
            for admin in admins:
                admin_id = admin.user.id
                if not admin.user.is_bot:
                    try:
                        await context.bot.send_message(chat_id=admin_id, text=texto_alerta, parse_mode="Markdown")
                    except:
                        pass
        except Exception as e:
            print("Error al alertar a administradores:", e)
        return

    # --- FLUJO DE ENCUESTA ---
    if user_id not in user_states:
        return
    estado = user_states[user_id]

    if estado == "pregunta_1":
        if any(p in mensaje for p in ["deportes", "tragamonedas", "casino", "mesa"]):
            user_states[user_id] = "pregunta_2"
            await update.message.reply_text("🕒 ¿Con qué frecuencia juegas en línea?\nResponde con: Diario / Fines de semana / Soy nuevo")
        else:
            await update.message.reply_text("Responde con: Deportes / Tragamonedas / Casino en vivo / Juegos de mesa")

    elif estado == "pregunta_2":
        if any(p in mensaje for p in ["diario", "fines", "nuevo"]):
            user_states[user_id] = "pregunta_3"
            await update.message.reply_text("💸 ¿Qué tipo de bonos te gustan más?\nResponde con: Sin depósito / Por recarga / Giros gratis / Cashback")
        else:
            await update.message.reply_text("Responde con: Diario / Fines de semana / Soy nuevo")

    elif estado == "pregunta_3":
        if any(p in mensaje for p in ["depósito", "recarga", "giros", "cashback"]):
            user_states[user_id] = "finalizado"
            await update.message.reply_text(
                "🎁 ¡Gracias por responder! Muy pronto te llegarán promociones exclusivas 😎\n"
                "🔗 Revisa las ofertas actuales aquí 👉 https://www.fun88chile.com/promotions"
            )
        else:
            await update.message.reply_text("Responde con: Sin depósito / Por recarga / Giros gratis / Cashback")

# === CONFIGURAR EL BOT ===
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, bienvenida))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), manejar_respuestas))

# === INICIAR EL BOT ===
if __name__ == '__main__':
    app.run_polling()

