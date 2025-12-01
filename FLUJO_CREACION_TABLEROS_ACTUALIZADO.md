# Flujo de Creación de Tableros - Estado Actual

## 🎯 Resumen Ejecutivo

El wizard de creación de tableros ha sido simplificado para enfocarse en la configuración esencial inicial. Las configuraciones avanzadas (horarios laborales, horas reales) se realizan post-creación mediante el drawer de configuración.

---

## 📋 Wizard de Creación (5 Pasos)

### **PASO 1: Información Básica** ✅
**Campos obligatorios:**
- Nombre del tablero
- Año
- Mes

**Campos opcionales:**
- Descripción
- Nombre del cliente
- Color de marca (6 presets + custom picker)

**Valores enviados al backend:**
```typescript
{
  nombre: string,
  anio: number,
  mes: number,
  descripcion?: string,
  client_name?: string,
  brand_color?: string  // HEX color (#3B82F6)
}
```

---

### **PASO 2: Módulos del Proyecto** ✅
**Módulos disponibles:**
- ⏱️ **Time Tracking** (activo por defecto)
- 💰 **Gestión de Presupuesto** (condicional: activa Paso 3)
- 📋 **Auditoría**
- 🌐 **Vista Pública**

**Comportamiento:**
- Toggle visual tipo card con checkmark
- `time_tracking` viene activado por defecto
- Si se activa `budget`, el wizard muestra el Paso 3
- Si NO se activa `budget`, el wizard salta al Paso 4

**Valor enviado al backend:**
```typescript
{
  modules_config: {
    time_tracking: true,
    budget: boolean,
    audit: boolean,
    public_view: boolean
  }
}
```

---

### **PASO 3: Configuración Financiera** (Condicional) ✅
**Condición:** Solo se muestra si `modules_config.budget === true`

**Tipos de presupuesto:**
1. **Monto Fijo** (`fixed_price`)
   - Campo: Monto Total (number)
   - Uso: Precio total acordado

2. **Bolsa de Horas** (`hourly_retainer`)
   - Campo: Cantidad de Horas (number)
   - Uso: Horas prepagadas

3. **Por Hora / Time & Materials** (`time_and_materials`)
   - No requiere monto inicial
   - Se factura según horas trabajadas

**Campos adicionales:**
- Moneda (USD, EUR, ARS, etc.)

**Valores enviados al backend:**
```typescript
{
  budget_type: 'fixed_price' | 'hourly_retainer' | 'time_and_materials' | 'none',
  budget_base_amount?: number,  // Solo para fixed_price y hourly_retainer
  currency: string  // Default: 'USD'
}
```

---

### **PASO 4: Tipo de Tablero** ✅
**Opciones:**
- 👤 **Personal** → Crea el proyecto inmediatamente
- 👥 **Empleados** → Avanza al Paso 5

**Navegación:**
```
Personal → Submit formulario → Crear proyecto
Empleados → Paso 5 (Lista de empleados)
```

**Valor enviado:**
```typescript
{
  tipo_proyecto: 'personal' | 'empleados'
}
```

---

### **PASO 5: Lista de Empleados** (Condicional) ✅
**Condición:** Solo si `tipo_proyecto === 'empleados'`

**Funcionalidad:**
- Agregar múltiples empleados
- Nombre obligatorio
- Email opcional (para vincular con usuario existente)
- Mínimo 1 empleado requerido

**Valor enviado:**
```typescript
{
  empleados: string[],  // Nombres limpios
  // Internamente se guardan los emails para mapeo
}
```

---

## 🚫 Configuraciones NO Incluidas en Wizard

Las siguientes configuraciones se realizan **post-creación** desde el drawer de configuración del proyecto:

### Horarios Laborales
- `modo_horarios`: null por defecto
- `horario_inicio`, `horario_fin`: null
- `turno_manana_*`, `turno_tarde_*`: null

### Horas Reales
- `horas_reales_activas`: false por defecto
- Se activa desde configuración de proyecto

**Razón:** Para proyectos personales no se requiere configurar horarios. Para proyectos con empleados, los horarios son opcionales y se configuran según necesidad.

---

## 🎨 Características Visuales

### Color Picker
- **6 presets**: Azul, Verde, Ámbar, Rojo, Púrpura, Rosa
- **Custom picker**: Input HEX con validación
- **Comportamiento**: Los presets se deseleccionan al usar custom

### Módulos Cards
- **Estado activo**: Borde, fondo, checkmark visible
- **Toggle**: Click en card para activar/desactivar
- **Indicador visual**: Checkmark (✓) en esquina superior derecha

### Budget Types Cards
- **Selección única**: Radio-button behavior
- **Campos dinámicos**: Monto aparece según tipo seleccionado
- **Indicador**: Checkmark en card seleccionado

---

## 🔧 Backend - Valores por Defecto

Cuando se crea un proyecto sin ciertas configuraciones:

```python
{
  'horas_reales_activas': False,
  'modo_horarios': None,  # Antes era 'corrido'
  'horario_inicio': None,
  'horario_fin': None,
  'turno_manana_inicio': None,
  'turno_manana_fin': None,
  'turno_tarde_inicio': None,
  'turno_tarde_fin': None,
  'modules_config': {
    'time_tracking': True,
    'budget': False,
    'audit': False,
    'public_view': False
  },
  'budget_type': 'none',
  'budget_base_amount': None,
  'currency': 'USD',
  'brand_color': None,
  'client_name': None
}
```

---

## 📊 Flujos de Navegación

### Flujo Personal Básico (Mínimo)
```
Step 1 (info básica) 
  → Step 2 (módulos - solo time_tracking) 
  → Step 4 (personal) 
  → ✅ CREAR
```

### Flujo Personal con Presupuesto
```
Step 1 (info + cliente + color) 
  → Step 2 (módulos - activar budget) 
  → Step 3 (financiero) 
  → Step 4 (personal) 
  → ✅ CREAR
```

### Flujo Empleados sin Presupuesto
```
Step 1 (info básica) 
  → Step 2 (módulos - solo time_tracking) 
  → Step 4 (empleados) 
  → Step 5 (lista empleados) 
  → ✅ CREAR
```

### Flujo Empleados Completo
```
Step 1 (info + cliente + color) 
  → Step 2 (módulos - todos activos) 
  → Step 3 (financiero) 
  → Step 4 (empleados) 
  → Step 5 (lista empleados) 
  → ✅ CREAR
```

---

## ⚙️ Configuración Post-Creación (Drawer)

**Ubicación:** `/organizaciones/[id]/settings.astro` o drawer dentro de proyecto

### Configuraciones Disponibles:

#### 1. Horarios Laborales ⏰
- Activar/configurar `modo_horarios`
- Definir horarios de entrada/salida
- Configurar turnos (mañana/tarde)
- **Ubicación actual:** `ConfigHorariosHandler.mostrar(proyecto)`

#### 2. Horas Reales ✅
- Toggle `horas_reales_activas`
- Muestra columna adicional en tablero
- **Ubicación actual:** Dentro de modal de horarios

#### 3. Módulos 🔧
- Activar/desactivar módulos post-creación
- Actualizar `modules_config`
- **Estado:** Pendiente implementar

#### 4. Budget Addons 💰
- Agregar complementos presupuestarios
- Ajustes/extensiones de presupuesto
- **Estado:** Pendiente implementar

---

## 🐛 Errores Solucionados

### ✅ Error 400 BAD REQUEST
**Causa:** Backend validaba `modo_horarios` como obligatorio
**Solución:** 
- Backend acepta `None` como valor válido
- Frontend no envía campos de horarios en wizard
- Proyectos se crean sin configuración de horarios

### ✅ Archivo Corrompido (832 líneas duplicadas)
**Causa:** Edición masiva durante eliminación de steps
**Solución:**
- Backup creado
- Reconstrucción desde primeras 290 líneas limpias
- Resultado: 584 líneas sin duplicación

---

## 📝 Archivos del Sistema

### Frontend
- **Wizard:** `/frontend/src/pages/nuevo-proyecto.astro` (584 líneas)
- **Handler:** `/frontend/src/handlers/nuevo-proyecto.ts`
- **Estilos:** `/frontend/src/styles/nuevo-proyecto.css`
- **Config Horarios:** `/frontend/src/handlers/config-horarios.ts`

### Backend
- **Route:** `/backend/app/routes/proyecto.py`
- **Service:** `/backend/app/services/proyecto_service.py`
- **Model:** `/backend/app/models/proyecto.py`

---

## 🎯 Próximos Pasos

1. ✅ **Creación de proyectos funcional**
2. 🔲 **Implementar drawer unificado de configuración**
3. 🔲 **Mover configuración de horarios a drawer**
4. 🔲 **Agregar gestión de budget addons**
5. 🔲 **Habilitar toggle de módulos post-creación**
6. 🔲 **Integrar auditoría con módulo audit**
7. 🔲 **Implementar vista pública con módulo public_view**

---

## 🔍 Notas Técnicas

- **Validación Step 1:** Nombre, año y mes obligatorios
- **Navegación condicional:** Basada en estado de módulos y tipo de proyecto
- **Script único:** 1 bloque `<script>` con toda la lógica
- **Sin horarios:** 0 referencias a horarios en código frontend del wizard
- **Compatibilidad:** Backend acepta todos los campos FASE 4

---

**Última actualización:** 1 de diciembre de 2025
**Estado:** ✅ Wizard funcional - Drawer de config pendiente
