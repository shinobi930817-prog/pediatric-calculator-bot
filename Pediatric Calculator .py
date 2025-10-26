import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Configuración profesional
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ⚠️ REEMPLAZA CON TU TOKEN
BOT_TOKEN = os.getenv('BOT_TOKEN', '8275484473:AAE7KivrQhlj7JMhpRHQHdl3zVbc3bYu32M')

# BASE DE DATOS DE MEDICAMENTOS (tu código original optimizado)
MEDICAMENTOS = {
    "Antibióticos": {
        "Amoxicilina (Susp 250mg/5mL)": {
            "dosis": 80, "max_dosis": 1000, "intervalo": "cada 8h",
            "presentacion": "250mg/5mL", "notas": "Agitar bien\nDosis otitis: 80-90mg/kg/día",
            "tipo_dosis": "diaria"
        },
        "Cefixima (Susp 100mg/5mL)": {
            "dosis": 8, "max_dosis": 400, "intervalo": "cada 12h",
            "presentacion": "100mg/5mL", "notas": "UTI: 8mg/kg/día\nOTITIS: 16mg/kg/día\nAgitar bien",
            "tipo_dosis": "diaria"
        },
        "Azitromicina (Susp 200mg/5mL)": {
            "dosis": 10, "max_dosis": 500, "intervalo": "cada 24h",
            "presentacion": "200mg/5mL", "notas": "Tomar 1h antes/2h después alimentos",
            "tipo_dosis": "diaria"
        }
    },
    "Antipiréticos/Analgésicos": {
        "Paracetamol (Susp 120mg/5mL)": {
            "dosis": 15, "max_dosis": 1000, "intervalo": "cada 6h",
            "presentacion": "120mg/5mL", "notas": "No exceder 1g/dosis\nMáx 4g/día",
            "tipo_dosis": "por_toma"
        },
        "Ibuprofeno (Susp 100mg/5mL)": {
            "dosis": 10, "max_dosis": 400, "intervalo": "cada 6-8h",
            "presentacion": "100mg/5mL", "notas": "Contraindicado <6 meses\nEvitar en varicela",
            "tipo_dosis": "por_toma"
        }
    },
    "Respiratorio": {
        "Salbutamol (Solución 2mg/5mL)": {
            "dosis": 0.3, "max_dosis": 5, "intervalo": "cada 6-8h",
            "presentacion": "2mg/5mL", "notas": "Dosis aguda: 0.1mg/kg cada 4-6h",
            "tipo_dosis": "por_toma"
        }
    }
}

def calcular_dosis_pediatricas(peso_kg, medicamento_key):
    """Calcula dosis basado en tu lógica original optimizada"""
    # Buscar medicamento en toda la base de datos
    for categoria, medicamentos in MEDICAMENTOS.items():
        if medicamento_key in medicamentos:
            datos = medicamentos[medicamento_key]
            break
    else:
        return None

    peso = float(peso_kg)
    
    if datos['tipo_dosis'] == "diaria":
        dosis_total = peso * datos['dosis']
        dosis_total = min(dosis_total, datos['max_dosis'])
        
        # Dividir según intervalo (tu lógica original)
        if "8" in datos['intervalo']:
            dosis_por_toma = dosis_total / 3
            intervalo = "3 tomas al día (cada 8 horas)"
        elif "12" in datos['intervalo']:
            dosis_por_toma = dosis_total / 2
            intervalo = "2 tomas al día (cada 12 horas)"
        elif "24" in datos['intervalo']:
            dosis_por_toma = dosis_total
            intervalo = "1 toma al día (cada 24 horas)"
        else:
            dosis_por_toma = dosis_total
            intervalo = datos['intervalo']
            
        texto_dosis = f"Dosis diaria total: {dosis_total:.2f} mg\nDosis por toma: {dosis_por_toma:.2f} mg"
        
    elif datos['tipo_dosis'] == "por_toma":
        dosis_por_toma = peso * datos['dosis']
        dosis_por_toma = min(dosis_por_toma, datos['max_dosis'])
        intervalo = datos['intervalo']
        texto_dosis = f"Dosis por aplicación: {dosis_por_toma:.2f} mg"
    
    # Cálculo de mL para formulaciones líquidas (tu lógica original)
    ml_info = ""
    try:
        if "mg" in datos['presentacion'] and "mL" in datos['presentacion']:
            partes = datos['presentacion'].split("mg")[0]
            mg = float(partes.split("(")[-1] if "(" in partes else partes)
            ml_part = datos['presentacion'].split("/")[1].split("mL")[0]
            ml = float(ml_part.split("(")[0] if "(" in ml_part else ml_part)
            
            ml_por_toma = (dosis_por_toma * ml) / mg
            ml_info = f"\n💧 Volumen por toma: {ml_por_toma:.2f} mL"
    except:
        pass

    return {
        'medicamento': medicamento_key,
        'presentacion': datos['presentacion'],
        'dosis_calculada': texto_dosis,
        'intervalo': intervalo,
        'ml_info': ml_info,
        'notas': datos['notas'],
        'peso': peso
    }

# --- HANDLERS PARA TELEGRAM ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Menú principal"""
    keyboard = [
        [InlineKeyboardButton("💊 Calcular Dosis", callback_data="menu_calcular")],
        [InlineKeyboardButton("📚 Categorías", callback_data="menu_categorias")],
        [InlineKeyboardButton("ℹ️ Instrucciones", callback_data="menu_help")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🩺 *Pediatric Calculator Bot* 📊\n\n"
        "¡Hola Doctor! Soy su asistente para cálculo de dosis pediátricas.\n\n"
        "*Funciones disponibles:*\n"
        "• 💊 Cálculo preciso de dosis\n"
        "• 📚 Base de datos de medicamentos\n"
        "• ⚠️ Advertencias de seguridad\n\n"
        "Seleccione una opción:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja todos los botones inline"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "menu_calcular":
        await mostrar_categorias(query, context)
    
    elif query.data == "menu_categorias":
        await mostrar_categorias_detalladas(query)
    
    elif query.data == "menu_help":
        await mostrar_ayuda(query)
    
    elif query.data.startswith("categoria_"):
        categoria = query.data.replace("categoria_", "")
        await mostrar_medicamentos_categoria(query, categoria)
    
    elif query.data.startswith("medicamento_"):
        medicamento_key = query.data.replace("medicamento_", "")
        context.user_data['medicamento_seleccionado'] = medicamento_key
        context.user_data['paso'] = 'peso'
        
        await query.edit_message_text(
            f"💊 *{medicamento_key}*\n\n"
            "👶 Ingrese el peso del paciente en *KILOGRAMOS*:\n"
            "Ejemplo: 12.5",
            parse_mode='Markdown'
        )
    
    elif query.data == "volver_menu":
        await start(update, context)

async def mostrar_categorias(query, context):
    """Muestra las categorías disponibles"""
    keyboard = []
    for categoria in MEDICAMENTOS.keys():
        keyboard.append([InlineKeyboardButton(f"📁 {categoria}", callback_data=f"categoria_{categoria}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Menú Principal", callback_data="volver_menu")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "💊 *SELECCIÓN DE CATEGORÍA*\n\n"
        "Elija la categoría del medicamento:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def mostrar_categorias_detalladas(query):
    """Muestra información detallada de categorías"""
    texto = "📚 *CATEGORÍAS DISPONIBLES*\n\n"
    for categoria, medicamentos in MEDICAMENTOS.items():
        texto += f"• *{categoria}:* {len(medicamentos)} medicamentos\n"
    
    texto += "\nUse /start para calcular dosis"
    
    keyboard = [[InlineKeyboardButton("🔙 Menú Principal", callback_data="volver_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(texto, reply_markup=reply_markup, parse_mode='Markdown')

async def mostrar_medicamentos_categoria(query, categoria):
    """Muestra medicamentos de una categoría específica"""
    if categoria not in MEDICAMENTOS:
        await query.edit_message_text("❌ Categoría no encontrada")
        return
    
    keyboard = []
    for medicamento in MEDICAMENTOS[categoria].keys():
        # Acortar nombre si es muy largo para el botón
        nombre_boton = medicamento[:25] + "..." if len(medicamento) > 25 else medicamento
        keyboard.append([InlineKeyboardButton(f"💊 {nombre_boton}", callback_data=f"medicamento_{medicamento}")])
    
    keyboard.append([InlineKeyboardButton("🔙 Volver a Categorías", callback_data="menu_calcular")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        f"📁 *{categoria.upper()}*\n\n"
        "Seleccione el medicamento:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def mostrar_ayuda(query):
    """Muestra instrucciones de uso"""
    ayuda_texto = """
ℹ️ *INSTRUCCIONES DE USO*

*Flujo de cálculo:*
1. Seleccione *💊 Calcular Dosis*
2. Elija la *categoría* del medicamento  
3. Seleccione el *medicamento* específico
4. Ingrese el *peso* en kilogramos
5. Reciba el *cálculo preciso* con advertencias

*Ejemplo:*
• Peso: 15 kg
• Medicamento: Amoxicilina
• Resultado: Dosis diaria + volumen en mL

*⚠️ IMPORTANTE:*
• Verifique siempre con protocolos actualizados
• Confirme dosis con supervisión
• Considere condiciones del paciente

*Comandos:*
/start - Menú principal
/calcular - Iniciar cálculo rápido
    """
    
    keyboard = [[InlineKeyboardButton("🚀 Comenzar Cálculo", callback_data="menu_calcular")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(ayuda_texto, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto para entrada de peso"""
    user_data = context.user_data
    paso = user_data.get('paso')
    texto = update.message.text
    
    if paso == 'peso':
        try:
            peso = float(texto)
            if peso <= 0 or peso > 150:
                await update.message.reply_text("❌ Peso debe ser entre 0.1 y 150 kg")
                return
            
            medicamento_key = user_data.get('medicamento_seleccionado')
            
            # Calcular dosis usando tu lógica original
            resultado = calcular_dosis_pediatricas(peso, medicamento_key)
            
            if resultado:
                respuesta = f"""
📋 *RESULTADO DEL CÁLCULO*

👶 *Peso:* {resultado['peso']} kg
💊 *Medicamento:* {resultado['medicamento']}
💊 *Presentación:* {resultado['presentacion']}

📏 *DOSIS CALCULADA:*
{resultado['dosis_calculada']}
🕐 *Frecuencia:* {resultado['intervalo']}
{resultado['ml_info']}

⚠️ *NOTAS IMPORTANTES:*
{resultado['notas']}

*🔔 RECUERDE:*
• Verificar con protocolos actualizados
• Considerar condiciones del paciente
• Confirmar con supervisión médica
                """
                
                keyboard = [
                    [InlineKeyboardButton("🔄 Nuevo Cálculo", callback_data="menu_calcular")],
                    [InlineKeyboardButton("🏠 Menú Principal", callback_data="volver_menu")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await update.message.reply_text(respuesta, reply_markup=reply_markup, parse_mode='Markdown')
                
                # Limpiar datos para próximo cálculo
                user_data.clear()
            else:
                await update.message.reply_text("❌ Error: Medicamento no encontrado")
        
        except ValueError:
            await update.message.reply_text("❌ Ingrese un peso válido. Ejemplo: 12.5")
        except Exception as e:
            await update.message.reply_text("❌ Error en el cálculo. Intente nuevamente.")

async def calcular_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /calcular - Acceso rápido"""
    context.user_data.clear()
    await mostrar_categorias(update, context)

def main():
    """Función principal"""
    try:
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("calcular", calcular_command))
        application.add_handler(CallbackQueryHandler(button_handler))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Iniciar bot
        print("🩺 Pediatric Calculator Bot iniciado correctamente")
        application.run_polling()
        
    except Exception as e:
        logging.error(f"Error al iniciar bot: {e}")

if __name__ == '__main__':
    main()