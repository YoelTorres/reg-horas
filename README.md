# 📋 RegHoras - Integración Firebase Firestore

## Descripción

Proyecto mejorado para gestionar registros de horas con soporte para **CSV** y **Firebase Firestore**.

### Características
✅ Carga/Guarda en CSV (compatibilidad existente)  
✅ Carga/Guarda en Firebase Firestore  
✅ Cambio dinámico de backend  
✅ Misma lógica y estructura, solo cambio de almacenamiento  
✅ Fallback automático a CSV si Firestore falla  

---

## 🚀 Instalación

### 1. Instalar dependencias de Firebase

```bash
pip install firebase-admin
```

O si usas `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 2. Configurar credenciales de Firebase

Obtén tu clave de servicio desde [Firebase Console](https://console.firebase.google.com/):

1. Ir a **Proyecto → Configuración → Cuentas de servicio**
2. Descargar archivo JSON de clave privada
3. Guardar como `firebase-key.json` en la raíz del proyecto

### 3. Configurar variables de entorno

Crear archivo `.env` en la raíz del proyecto:

```env
# Activar Firestore
USAR_FIRESTORE=true

# ID del proyecto Firebase
FIREBASE_PROJECT_ID=tu-proyecto-id

# (Opcional) Nombre de la colección
FIREBASE_COLLECTION_NAME=transacciones

# (Opcional) Ruta de credenciales
FIREBASE_KEY_PATH=firebase-key.json
```

O establecer variables de entorno directamente:

```bash
export USAR_FIRESTORE=true
export FIREBASE_PROJECT_ID=tu-proyecto-id
```

---

## 📦 Dependencias

### Librerías Externas Requeridas

| Librería | Versión | Propósito |
|----------|---------|----------|
| **streamlit** | 1.28.1 | Framework web para la interfaz interactiva |
| **pandas** | 2.1.3 | Manipulación y análisis de datos |
| **firebase-admin** | 6.1.0 | Cliente oficial de Firebase/Firestore |
| **python-dotenv** | 1.0.0 | Gestión segura de variables de entorno |
| **Pillow** | 10.1.0 | Procesamiento de imágenes (firmas) |
| **fpdf2** | 2.7.0 | Generación de documentos PDF |
| **streamlit-drawable-canvas** | 0.2.3 | Componente para captura de firmas |
| **numpy** | 1.24.3 | Computación numérica |

### Instalar todas las dependencias

```bash
pip install -r requirements.txt
```

### Librerías Estándar (incluidas con Python)

- `datetime` - Manejo de fechas y horas
- `os` - Operaciones del sistema operativo
- `json` - Procesamiento de JSON
- `pathlib` - Rutas del sistema de archivos
- `typing` - Anotaciones de tipos
- `io` - Operaciones de entrada/salida

### Verificar instalación

```bash
# Ver todas las dependencias instaladas
pip freeze

# Verificar una dependencia específica
python -c "import streamlit; print(streamlit.__version__)"
python -c "import firebase_admin; print(firebase_admin.__version__)"
```

---

## 📁 Estructura de archivos

```
RegHoras/
├── clases/
│   ├── __pycache__/
│   ├── Transaccion.py           # Modelo de transacción
│   ├── GestorTransacciones.py   # Gestor (CSV + Firestore)
│   ├── FirestoreManager.py      # ✨ NUEVO: Gestor Firestore
│   ├── firebase_config.py       # ✨ NUEVO: Config Firebase
│   ├── InterfazUI.py
│   ├── GestorFirmas.py
│   ├── PlanillaPDF.py
│   └── GestorFirmas.py
├── firmas/
├── app.py
├── transacciones.csv            # CSV fallback
├── firebase-key.json            # ⚠️ NO COMMITEAR (credenciales)
└── .env                         # ⚠️ NO COMMITEAR (variables)
```

---

## 💻 Uso

### Opción 1: Usar CSV (por defecto)

```python
from clases.GestorTransacciones import GestorTransacciones

gestor = GestorTransacciones()  # Usa CSV
gestor.cargar()
```

### Opción 2: Usar Firestore

```python
from clases.GestorTransacciones import GestorTransacciones

# Opción A: Por variable de entorno (USAR_FIRESTORE=true)
gestor = GestorTransacciones()

# Opción B: Directamente en código
gestor = GestorTransacciones(usar_firestore=True)
```

### Opción 3: Cambiar backend dinámicamente

```python
gestor = GestorTransacciones()
gestor.cargar()

# Cambiar a Firestore
gestor.cambiar_backend(usar_firestore=True)
gestor.guardar()

# Volver a CSV
gestor.cambiar_backend(usar_firestore=False)
```

---

## 🔌 API de FirestoreManager

```python
from clases.FirestoreManager import FirestoreManager

fm = FirestoreManager()

# Cargar todas
transacciones = fm.cargar_todas()

# Agregar una
doc_id = fm.agregar_una(transaccion)

# Actualizar
fm.actualizar_una(doc_id, transaccion)

# Eliminar
fm.eliminar_una(doc_id)

# Buscar
fm.obtener_por_fecha(fecha)
fm.buscar_por_descripcion("REYNA")

# Limpiar colección (⚠️ cuidado)
fm.limpiar_coleccion()
```

---

## 🛡️ Seguridad

⚠️ **IMPORTANTE:**

- **Nunca** commitear `firebase-key.json` en Git
- **Nunca** commitear `.env` con variables sensibles
- Agregar a `.gitignore`:

```gitignore
firebase-key.json
.env
.env.local
```

---

## 🧪 Testing

Para probar la integración sin credenciales reales:

```python
# app.py - Desactivar Firestore por defecto
USAR_FIRESTORE = False  # Cambiar a True cuando tengas credenciales
```

---

## 📊 Estructura de datos en Firestore

Cada documento en la colección `transacciones` tiene esta estructura:

```json
{
  "descripcion": "LA REYNA - FUNES",
  "fecha": "2026-09-01",
  "ingreso": "16:00:00",
  "salida": "00:00:00",
  "firma_id": ""
}
```

**ID del documento:** Auto-generado basado en fecha + descripción

---

## ⚡ Funcionalidades futuras

- [ ] Sincronización bidireccional CSV ↔ Firestore
- [ ] Soporte para Realtime Database
- [ ] Panel de administración con cambio de backend
- [ ] Respaldos automáticos
- [ ] Exportación a múltiples formatos (PDF, Excel, JSON)

---

## 🆘 Troubleshooting

### Error: "Archivo de credenciales no encontrado"

```
FileNotFoundError: Archivo de credenciales no encontrado: firebase-key.json
```

**Solución:** Descargar clave de servicio desde Firebase Console y guardar como `firebase-key.json`

### Error: "No se pudo conectar con Firestore"

- Verificar que `FIREBASE_PROJECT_ID` es correcto
- Verificar que las credenciales son válidas
- Verificar conectividad a internet
- El sistema caerá automáticamente a CSV

### Transacciones no se sincronizan

- Verificar permisos de Firestore en Firebase Console
- Revisar logs de Firestore en Firebase Console
- Confirmar que el nombre de la colección es correcto

---

## 📄 Licencia

MIT

---

**Creado con ❤️ para RegHoras**
