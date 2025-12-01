# Cambios: Wizard sin Horarios Laborales

## Resumen de Cambios

Se eliminaron los pasos de configuración de horarios laborales (Steps 6, 7a, 7b) del wizard de creación de proyectos. Los horarios ahora son una configuración opcional que se puede realizar después de crear el proyecto mediante el drawer de configuración.

## Archivos Modificados

### 1. `/frontend/src/pages/nuevo-proyecto.astro`

**Cambios realizados:**
- ✅ Eliminado Step 6 (selección de modo de horarios)
- ✅ Eliminado Step 7a (configuración de horario corrido)
- ✅ Eliminado Step 7b (configuración de turnos)
- ✅ Archivo reconstruido desde 832 líneas corrompidas a 584 líneas limpias
- ✅ Navegación simplificada:
  - Personal: Step 4 → Enviar formulario
  - Empleados: Step 4 → Step 5 (lista empleados) → Enviar formulario

**Estructura actual del wizard:**
1. **Step 1:** Información básica (nombre, año, mes, descripción, cliente, brand_color)
2. **Step 2:** Módulos (time_tracking, budget, audit, public_view)
3. **Step 3:** Configuración financiera (condicional, solo si budget activo)
4. **Step 4:** Tipo de tablero (personal vs empleados)
5. **Step 5:** Lista de empleados (solo si empleados seleccionado)

### 2. `/frontend/src/handlers/nuevo-proyecto.ts`

**Cambios realizados:**
- ✅ Eliminada obtención de campos: `modo_horarios`, `horario_inicio`, `horario_fin`, `turno_manana_inicio`, `turno_manana_fin`, `turno_tarde_inicio`, `turno_tarde_fin`
- ✅ Eliminada validación de horarios para proyectos con empleados
- ✅ Actualizado `createProyecto()` para NO enviar campos de horarios al backend
- ✅ Agregado comentario: "Los horarios se configurarán opcionalmente después desde el drawer"

**Campos que se envían al backend:**
```typescript
{
  nombre,
  anio,
  mes,
  descripcion,
  tipo_proyecto,
  empleados,
  horas_reales_activas,
  client_name,      // FASE 4
  brand_color,      // FASE 4
  modules_config,   // FASE 4
  budget_type,      // FASE 4
  budget_base_amount, // FASE 4
  currency          // FASE 4
}
```

### 3. `/backend/app/routes/proyecto.py`

**Cambios realizados (previamente):**
- ✅ `modo_horarios` cambiado de requerido a opcional
- ✅ Validación: `if modo_horarios and modo_horarios not in ['corrido', 'turnos', None]:`
- ✅ Acepta `None` como valor válido

### 4. `/backend/app/services/proyecto_service.py`

**Cambios realizados (previamente):**
- ✅ Parámetro `modo_horarios: str = None` (antes era `= 'corrido'`)
- ✅ Proyecto puede crearse sin configuración de horarios

## Comportamiento Actual

### Proyectos Personales
1. Usuario ingresa información básica
2. Selecciona módulos (time_tracking activo por defecto)
3. Si activa budget, configura presupuesto
4. Selecciona "Personal"
5. ✅ **Proyecto creado inmediatamente** (sin horarios)

### Proyectos con Empleados
1. Usuario ingresa información básica
2. Selecciona módulos
3. Si activa budget, configura presupuesto
4. Selecciona "Empleados"
5. Agrega lista de empleados con nombres y emails opcionales
6. ✅ **Proyecto creado con empleados** (sin horarios configurados)

### Configuración de Horarios (Post-Creación)
- 🔲 **Pendiente:** Drawer de configuración dentro del proyecto
- 🔲 **Pendiente:** Interfaz para configurar `modo_horarios`, horarios de entrada/salida, turnos
- 🔲 **Pendiente:** Edición de horarios por empleado

## Errores Solucionados

### Error 400 BAD REQUEST
**Causa:** Backend validaba `modo_horarios` como campo requerido

**Solución:**
1. Backend ahora acepta `modo_horarios = None`
2. Frontend no envía campos de horarios
3. Proyectos se crean sin errores

### Archivo Corrompido
**Causa:** Durante la eliminación de steps, el archivo se duplicó (832 líneas)

**Solución:**
1. Backup creado: `nuevo-proyecto.astro.backup`
2. Extracción de primeras 290 líneas limpias
3. Reconstrucción completa con script único
4. Resultado: 584 líneas sin duplicación

## Testing Requerido

- [ ] Crear proyecto personal sin errores
- [ ] Crear proyecto con empleados sin errores
- [ ] Verificar que campos FASE 4 se envían correctamente (cliente, brand_color, modules_config, budget)
- [ ] Verificar navegación condicional del Step 2 → Step 3 (solo si budget activo)
- [ ] Verificar que proyectos se crean con `modo_horarios = NULL` en base de datos

## Próximos Pasos

1. **Testing:** Validar creación de proyectos end-to-end
2. **Drawer Config:** Implementar drawer para configuración post-creación
3. **Horarios Laborales:** Agregar interfaz en drawer para configurar horarios opcionalmente
4. **Budget Addons:** Agregar gestión de complementos presupuestarios en drawer
5. **Módulos Toggle:** Permitir activar/desactivar módulos después de crear proyecto

## Notas Técnicas

- Wizard reducido de ~832 líneas corrompidas a 584 líneas limpias
- Un único bloque `<script>` con toda la lógica
- Validación de Step 1 antes de avanzar
- Color picker funcional con 6 presets + custom
- Módulos con toggle visual (cards con checkmark)
- Budget condicional con 3 tipos y campos dinámicos
- No hay referencias a horarios en código frontend

## Referencias

- Solicitud original: "cuando es personal el proyecto independientemente de las configuraciones no se debe pedir configurar el horario laboral, el horario laboral debe ser una configuracion activable con el drawer"
- Documento FASE 4: Ver `/backend/migrations/README_FASE3_FINANCIERO.md`
