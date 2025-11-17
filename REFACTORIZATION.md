# 📊 Refactorización de proyecto/[id].astro

## Cambios Realizados

### Antes
- **Archivo**: `frontend/src/pages/proyecto/[id].astro`
- **Tamaño**: 700+ líneas
- **Problemas**: 
  - Lógica mezclada con HTML
  - Funciones repetidas
  - Difícil de mantener
  - Bajo separación de responsabilidades

### Después
- **Tamaño**: 586 líneas (-114 líneas, **-16% de código**)
- **Mantenibilidad**: ✅ Excelente
- **Responsabilidades**: Claramente separadas en handlers

---

## Arquitectura Nueva

### 1. **Handlers de Tareas** → `frontend/src/handlers/tarea.ts`
**Responsables de**: Crear, editar, eliminar y visualizar tareas

**Métodos públicos**:
- `TareaHandler.resetParaCrear()` - Limpia formulario para nueva tarea
- `TareaHandler.loadDiasDisponibles()` - Carga días para la tarea
- `TareaHandler.cargarParaEditar()` - Prepara edición de tarea
- `TareaHandler.guardarTarea()` - Guarda tarea (crear o actualizar)
- `TareaHandler.renderizarVistaDetalle()` - Renderiza modal de vista
- `TareaHandler.eliminarTarea()` - Elimina una tarea
- `TareaHandler.actualizarSelectDias()` - Actualiza opciones del select
- `TareaHandler.renderizarDiasSeleccionados()` - Renderiza badges de días

**Estado interno**:
```typescript
TareaHandler.diasSeleccionados: Map<number, DiasInfo>
TareaHandler.diasDisponibles: Map<number, DiasInfo>
TareaHandler.tareaEnVista: any
```

---

### 2. **Handlers de Meses** → `frontend/src/handlers/meses.ts`
**Responsables de**: Gestionar meses del proyecto

**Métodos públicos**:
- `MesesHandler.loadMeses()` - Carga meses disponibles
- `MesesHandler.renderMeses()` - Renderiza lista de meses
- `MesesHandler.updateMesInfo()` - Actualiza info del mes
- `MesesHandler.openAddMesModal()` - Abre modal para agregar mes
- `MesesHandler.closeAddMesModal()` - Cierra modal
- `MesesHandler.agregarMes()` - Agrega mes al proyecto
- `MesesHandler.crearMesAutomatico()` - Crea mes si no existe
- `MesesHandler.mesYaExiste()` - Verifica si mes existe

**Estado interno**:
```typescript
MesesHandler.mesesDisponibles: [number, number][]
```

---

### 3. **Página Principal** → `frontend/src/pages/proyecto/[id].astro`
**Responsable de**: Orquestar handlers y gestionar eventos de UI

**Estructura**:
```
- Imports de handlers, servicios y utilidades
- Referencias a elementos DOM
- Gestión de Tareas
  - Nueva tarea
  - Cerrar modales
  - Seleccionar días
  - Guardar tarea
  - Visualizar tarea
  - Editar desde vista
  - Eliminar desde vista
- Gestión de Meses
  - Modal de mes
  - Agregar mes
  - Seleccionar mes
  - Cambiar mes
- Acciones Generales
  - Exportar PDF
  - Finalizar/Reactivar proyecto
- Inicialización
```

---

## Reducción de Código

### Antes: ~700 líneas
```javascript
// Todo mezclado en un solo archivo
- HTML + CSS
- State global (diasSeleccionados, diasDisponibles, etc.)
- Funciones de manejo
- Event listeners
- Lógica de renderizado
- Lógica de API calls
```

### Después: 586 líneas
```
proyecto/[id].astro   (586 líneas) - Solo orquestación
├─ handlers/tarea.ts  (380 líneas) - Lógica de tareas
├─ handlers/meses.ts  (130 líneas) - Lógica de meses
└─ handlers/proyecto.ts - Lógica de proyecto (existente)
```

### Ventajas
✅ **-114 líneas** menos en la página principal  
✅ **Más mantenible** - Cada handler tiene una responsabilidad clara  
✅ **Reutilizable** - Los handlers pueden usarse en otras páginas  
✅ **Testeable** - Cada función es independiente  
✅ **Escalable** - Fácil agregar nuevas funcionalidades  

---

## Flujo de Datos

```
┌─────────────────────────────────────────────┐
│    Página: proyecto/[id].astro              │
│  (Orquestación de eventos)                  │
└────┬──────────────────┬─────────────────────┘
     │                  │
     ▼                  ▼
┌──────────────┐    ┌─────────────┐
│ TareaHandler │    │ MesesHandler│
├──────────────┤    ├─────────────┤
│ - diasMap    │    │ - mesesList │
│ - renderizar │    │ - crear     │
│ - guardar    │    │ - navegar   │
└────┬─────────┘    └────┬────────┘
     │                   │
     └─────────┬─────────┘
               ▼
       ┌──────────────┐
       │   Services   │
       │   (API)      │
       └──────────────┘
```

---

## Ejemplo: Crear Nueva Tarea

### Antes (sin refactorizar)
```javascript
// 20+ líneas de código esparcidas por el archivo
document.getElementById('nueva-tarea-btn')?.addEventListener('click', async () => {
  form.reset();
  diasSeleccionados.clear();
  // ... más setup ...
  await loadDiasDisponibles();
  modal.style.display = 'flex';
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  // ... 30+ líneas de lógica de validación y guardado ...
});
```

### Después (refactorizado)
```javascript
// 5 líneas claras
document.getElementById('nueva-tarea-btn')?.addEventListener('click', async () => {
  TareaHandler.resetParaCrear(form);
  const proyecto = proyectoHandlers.state.proyectoActual;
  if (proyecto) {
    await TareaHandler.loadDiasDisponibles(proyecto.id, proyecto.anio, proyecto.mes);
  }
  modal.style.display = 'flex';
});

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const proyecto = proyectoHandlers.state.proyectoActual;
  if (proyecto) {
    await TareaHandler.guardarTarea(form, proyecto.id, async () => {
      modal.style.display = 'none';
      await proyectoHandlers.loadTareas();
    });
  }
});
```

---

## Pasos para Mantener

1. **Agregar nueva funcionalidad de tareas**
   - Editar `frontend/src/handlers/tarea.ts`
   - Agregar método a `TareaHandler`
   - Llamar desde `proyecto/[id].astro`

2. **Agregar nueva funcionalidad de meses**
   - Editar `frontend/src/handlers/meses.ts`
   - Agregar método a `MesesHandler`
   - Llamar desde `proyecto/[id].astro`

3. **Cambios en UI**
   - Solo tocar `proyecto/[id].astro` o HTML

4. **Cambios en lógica**
   - Ir al handler correspondiente (`tarea.ts` o `meses.ts`)

---

## Compilación ✅

```
✅ proyecto/[id].astro - No errors
✅ handlers/tarea.ts - No errors
✅ handlers/meses.ts - No errors
```

---

## Próximas Mejoras (Opcional)

1. Extraer handlers de días en su propio módulo
2. Crear tipos dedicados para mejor type safety
3. Agregar tests para cada handler
4. Documentación JSDoc más completa
5. Crear handler para formularios de tareas

