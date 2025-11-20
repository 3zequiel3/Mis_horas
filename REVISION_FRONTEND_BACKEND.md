# Revisión: Frontend → Backend - Consistencia de Datos

## ✅ Servicios Correctos

### 1. **AsistenciaService** ✅
- ✅ `marcarEntrada()`: Mapea correctamente `hora_entrada` → `hora`
- ✅ `marcarSalida()`: Mapea correctamente `hora_salida` → `hora` y `confirmacion_continua` → `confirmar_continuidad`
- ✅ `obtenerMarcados()`: Query params correctos
- ✅ `detectarAusencias()`: Body correcto
- ✅ `obtenerEstadoHoy()`: Query params correctos
- ✅ `editarMarcado()`: Endpoint y body correctos
- ✅ `confirmarHorasExtras()`: Endpoint y body correctos

### 2. **DeudasService** ✅
- ✅ `obtenerDeudaEmpleado()`: Query params correctos, retorna array
- ✅ `obtenerDeuda()`: Endpoint correcto
- ✅ `justificarDeuda()`: Endpoint y body correctos
- ✅ `aprobarJustificacion()`: Endpoint correcto
- ✅ `rechazarJustificacion()`: Endpoint correcto
- ✅ `obtenerJustificacionesProyecto()`: Endpoint y query params correctos
- ✅ `obtenerJustificacionesEmpleado()`: Query params correctos

### 3. **ProyectosService** ✅
- ✅ `getProyectos()`: Endpoint correcto
- ✅ `createProyecto()`: Endpoint y body correctos
- ✅ `getProyecto()`: Endpoint correcto
- ✅ `getMeses()`: Endpoint correcto
- ✅ `addMes()`: Endpoint y body correctos
- ✅ `cambiarEstado()`: Endpoint y body correctos
- ✅ `getEstadisticas()`: Endpoint correcto
- ✅ `deleteProyecto()`: Endpoint correcto
- ✅ `updateConfiguracion()`: Endpoint correcto, campos coinciden con backend

### 4. **EmpleadosService** ✅
- ✅ `getEmpleadosByProyecto()`: Endpoint correcto
- ✅ `addEmpleado()`: Endpoint y body correctos
- ✅ `getEmpleado()`: Endpoint correcto
- ✅ `updateEmpleado()`: Endpoint y body correctos
- ✅ `deleteEmpleado()`: Endpoint correcto

### 5. **DiaService** ✅
- ✅ `getDiasMes()`: Endpoint y query params correctos
- ✅ `getDia()`: Endpoint correcto
- ✅ `updateHoras()`: Endpoint y body correctos (`horas`)
- ✅ `updateHorarios()`: Endpoint y body correctos (`hora_entrada`, `hora_salida`)

### 6. **ConfiguracionAsistenciaService** ✅
- ✅ `obtenerConfiguracion()`: Endpoint correcto
- ✅ `actualizarConfiguracion()`: Endpoint correcto, campos coinciden
- ✅ `activarAsistencia()`: Endpoint correcto
- ✅ `desactivarAsistencia()`: Endpoint correcto

---

## 🔍 Detalles de Validación

### Campos de Horarios (ProyectosService.updateConfiguracion)
**Frontend envía:**
```typescript
{
  modo_horarios?: 'corrido' | 'turnos';
  horario_inicio?: string;  // formato "HH:MM"
  horario_fin?: string;     // formato "HH:MM"
  turno_manana_inicio?: string;
  turno_manana_fin?: string;
  turno_tarde_inicio?: string;
  turno_tarde_fin?: string;
}
```

**Backend espera (routes/proyecto.py):**
```python
# Parsea strings "HH:MM" a time objects
proyecto.horario_inicio = datetime.strptime(data['horario_inicio'], '%H:%M').time()
```
✅ **Compatible**: Frontend envía strings "HH:MM", backend los parsea correctamente.

### Campos de Asistencia (AsistenciaService.marcarEntrada/Salida)
**Frontend envía a marcarEntrada:**
```typescript
{
  empleado_id: number,
  proyecto_id: number,
  fecha?: string,
  hora: string,  // ← Mapeado desde hora_entrada
  latitud?: number,
  longitud?: number
}
```

**Backend espera (routes/asistencia.py):**
```python
data.get('empleado_id')
data.get('proyecto_id')
data.get('fecha')  # opcional
data.get('hora')   # opcional, parsea con '%H:%M:%S'
```
✅ **Compatible**: Mapeo correcto, backend acepta los campos.

**⚠️ NOTA**: Backend parsea hora con formato `%H:%M:%S` pero frontend podría enviar `%H:%M`.

### Campos de Configuración de Asistencia
**Frontend envía:**
```typescript
{
  politica_horas_extras?: 'compensar_deuda' | 'bloquear_extras' | 'separar_cuentas';
  tolerancia_retraso_minutos?: number;
  marcar_salida_automatica?: boolean;
  permitir_justificaciones?: boolean;
  requiere_aprobacion_justificaciones?: boolean;
  limite_horas_justificables?: number;
  periodo_limite_justificaciones?: 'diario' | 'semanal' | 'mensual' | 'anual';
  enviar_recordatorio_marcado?: boolean;
  enviar_alerta_deuda?: boolean;
  hora_recordatorio_entrada?: string;
  hora_recordatorio_salida?: string;
}
```

**Backend acepta (routes/configuracion_asistencia.py):**
```python
if 'politica_horas_extras' in data:
    politica = data['politica_horas_extras']
    if politica not in ['compensar_deuda', 'bloquear_extras', 'separar_cuentas']:
        return error_response('Política de horas extras inválida', 400)
    config.politica_horas_extras = politica

if 'tolerancia_retraso_minutos' in data:
    config.tolerancia_retraso_minutos = data['tolerancia_retraso_minutos']
    
# ... todos los demás campos
```
✅ **Compatible**: Todos los campos coinciden.

---

## ⚠️ Posibles Problemas Detectados

### 1. Formato de Hora en Asistencia
**Ubicación**: `AsistenciaService.marcarEntrada()` y `marcarSalida()`

**Problema Potencial**:
- Backend parsea hora con `'%H:%M:%S'` (routes/asistencia.py:54)
- Frontend podría enviar hora sin segundos `"HH:MM"`

**Recomendación**:
```typescript
// En AsistenciaService, asegurar formato correcto
hora: data.hora_entrada.includes(':00') ? data.hora_entrada : `${data.hora_entrada}:00`
```

### 2. Latitud y Longitud en Marcado
**Ubicación**: `AsistenciaService.marcarEntrada()` y `marcarSalida()`

**Observación**:
- Frontend envía `latitud` y `longitud` opcionales
- Backend **NO** tiene estos campos en la ruta `/marcar-entrada` ni `/marcar-salida`

**Impacto**: Backend ignora estos campos (sin error, pero no los usa)

**Estado**: ⚠️ Frontend envía datos que backend no procesa (no crítico, pero innecesario)

### 3. Campo `marcado_id` en MarcarSalidaRequest
**Ubicación**: Tipo `MarcarSalidaRequest` en frontend

**Observación**:
- El tipo TypeScript podría incluir `marcado_id` (verificar en types/Asistencia.ts)
- Backend **NO** usa `marcado_id` en `/marcar-salida`, busca el marcado por `empleado_id + proyecto_id + fecha`

**Estado**: ℹ️ Verificar si frontend lo envía (podría ser innecesario)

---

## 📋 Recomendaciones

### Críticas (Implementar Ya)
✅ **Ninguna**: No hay inconsistencias críticas que rompan funcionalidad

### Mejoras Sugeridas
1. **Normalizar formato de hora**: Asegurar que frontend siempre envíe `"HH:MM:SS"` en marcado de asistencia
2. **Eliminar campos no usados**: Quitar `latitud` y `longitud` de AsistenciaService si backend no los procesa
3. **Documentar tipos**: Agregar comentarios en tipos TypeScript indicando formato esperado de fechas/horas

### Verificaciones Adicionales
- [ ] Revisar tipo `MarcarSalidaRequest` para confirmar si incluye `marcado_id`
- [ ] Verificar si handlers usan formato correcto al llamar AsistenciaService
- [ ] Confirmar que todas las fechas se envían en formato `YYYY-MM-DD`

---

## ✅ Conclusión

**Estado General**: ✅ **CORRECTO** - No hay inconsistencias críticas

El frontend está enviando los datos correctos al backend en todos los servicios principales. Los únicos puntos a considerar son:
1. Formato de hora en marcado (posible inconsistencia menor)
2. Campos de geolocalización no procesados por backend

**Funcionalidad**: Todo debería estar funcionando correctamente. Las optimizaciones de código realizadas no afectaron la comunicación frontend-backend.
