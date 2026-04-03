# TimeFlow — Visión General del Sistema

> Documento de análisis técnico y funcional. Generado automáticamente a partir del código fuente.  
> Última actualización: 2026-03-18

---

## ¿Qué es TimeFlow?

TimeFlow es una **plataforma de gestión de tiempo, proyectos y recursos humanos** orientada a equipos y empresas. Su propósito central es permitir que organizaciones registren, controlen y analicen cómo se distribuye el tiempo real de trabajo de sus colaboradores dentro de proyectos, con visibilidad financiera integrada.

A diferencia de un simple fichador o timesheet, TimeFlow combina:
- Registro de asistencia con marcado automático
- Gestión de proyectos con colaboradores
- Motor financiero de rentabilidad por proyecto
- Sistema de aprobaciones por períodos
- Trazabilidad de auditoría completa (log inmutable tipo caja negra)
- Arquitectura multi-tenant (múltiples organizaciones independientes)

---

## Stack Tecnológico

| Capa | Tecnología |
|------|-----------|
| Backend | **Flask** (Python) + SQLAlchemy ORM |
| Base de datos | **MySQL** (PyMySQL) |
| Frontend | **Astro** (framework SSG/SSR) + Alpine.js + TailwindCSS |
| Tareas programadas | **APScheduler** (cron interno, proceso aparte) |
| Infraestructura | **Docker** + docker-compose |
| Autenticación | JWT + sesiones con cookie |
| Email | SMTP (servicio de emails de invitación / notificaciones) |

---

## Arquitectura del Sistema

### Estructura de carpetas

```
TimeFlow/
├── backend/
│   ├── app/
│   │   ├── models/       # 23 modelos SQLAlchemy
│   │   ├── routes/       # 21 blueprints Flask (endpoints)
│   │   ├── services/     # 15 servicios de dominio
│   │   └── utils/        # Helpers y decoradores
│   ├── scheduler.py      # Proceso APScheduler autónomo
│   └── main.py
└── frontend/
    └── src/
        ├── pages/        # Rutas Astro (dashboard, proyectos, org...)
        ├── components/   # Componentes reutilizables
        ├── services/     # Llamadas a la API desde el cliente
        ├── handlers/     # Lógica específica por sección
        ├── layouts/      # Layouts base de las páginas
        └── stores/       # Estado global del frontend
```

---

## Fases de Desarrollo

El sistema fue construido en **4 fases incrementales**, cada una registrada como comentarios en el código:

| Fase | Nombre | ¿Qué agrega? |
|------|--------|-------------|
| Fase 1 | **Multi-Tenant** | Organizaciones independientes, registro auto-crea org personal |
| Fase 2 | **RBAC + Auditoría + Aprobaciones** | Roles, log de acciones inmutable, flujo de aprobación de timesheets |
| Fase 3 | **Motor Financiero** | Tarifas, presupuestos, gastos, rentabilidad en tiempo real |
| Fase 4 | **UX Unificada** | Módulos configurables por proyecto, branding, vista pública |

---

## Funcionalidades Implementadas

### 1. Gestión de Organizaciones (Multi-Tenant)

Cada usuario al registrarse obtiene **automáticamente su propia organización personal**. Las organizaciones son universos de datos completamente independientes.

- Tipos: `personal`, `empresa`, `freelance`, `agencia`
- Planes preparados: `free`, `starter`, `professional`, `enterprise` (estructura lista, sin lógica de cobro activa aún)
- Cada organización tiene: zona horaria, moneda, formato de fecha, logo, slug URL
- Un usuario puede pertenecer a múltiples organizaciones con distintos roles

### 2. Proyectos

Los proyectos son el eje central. Cada proyecto lleva:

- **Tipo**: `personal` (solo el dueño) o `empleados` (equipo)
- **Modo de horario**: `corrido` (horario único) o `turnos` (mañana/tarde con horarios propios)
- **Configuración de módulos** por proyecto:
  - `budget` — Activa el motor financiero
  - `time_tracking` — Registro de tiempo (siempre activo)
  - `audit` — Activa logs de auditoría
  - `approvals` — Activa el flujo de aprobación de timesheets
  - `public_view` — Habilita vista pública del proyecto
- **Tipo de presupuesto**: `fixed_price`, `hourly_retainer`, `time_and_materials`, `none`
- Campo `client_name` y `brand_color` para personalización

### 3. Registro de Tiempo y Asistencia

Los colaboradores registran su tiempo día a día. El sistema soporta:

- **Marcado manual** (entrada/salida del empleado)
- **Marcado automático** (APScheduler lo procesa cada hora: si un empleado olvidó marcar salida, el sistema lo hace automáticamente)
- **Horas reales** vs horas estimadas (configurable a nivel usuario y proyecto)
- **Deuda de horas**: si un empleado trabaja menos horas de las requeridas, el sistema lo detecta y lo registra en `DeudaHoras`
- **Justificaciones**: los empleados pueden justificar ausencias o diferencias de horas

### 4. Sistema de Períodos y Aprobaciones

El modelo `TimePeriod` permite que los timesheets mensuales sigan un **flujo formal de aprobación**:

```
draft → pending (enviado para revisar) → approved / rejected
approved → locked (bloqueado permanentemente)
rejected → draft (volver a editar)
```

- Un período agrupa todos los días trabajados de un empleado en un mes
- Solo se puede editar en estado `draft` o `rejected`
- Solo Owner/Admin puede reabrirlo si ya está `approved` o `locked`
- Registra quién envió, quién aprobó/rechazó y las notas de la revisión

### 5. Motor Financiero (Fase 3)

El servicio `ProfitabilityService` calcula en tiempo real:

- **Horas totales y facturables** por proyecto
- **Costo interno** (horas × tarifa interna del empleado)
- **Ingresos facturables** (horas × tarifa de billing)
- **Gastos adicionales** (no humanos: herramientas, licencias, etc.)
- **Ganancia neta** y **margen de rentabilidad**
- Estado de salud del proyecto: `healthy` (>30%), `warning` (10-30%), `critical` (0-10%), `losing_money` (<0%)

El modelo `Budget` maneja los límites de gasto:
- Tipos: `monetary` (dinero), `hours` (bolsa de horas), `fixed_price`, `none`
- Calcula el **burn rate** (% consumido) en tiempo real
- Alerta configurable (por defecto al 80% de consumo)
- Puede bloquearse automáticamente al exceder el límite

### 6. Sistema de Tarifas (Rates)

El modelo `Rate` permite tarifas en cascada:
- Tarifa a nivel organización (global)
- Tarifa a nivel proyecto (sobreescribe la global)
- Tarifa a nivel usuario dentro de un proyecto (sobreescribe la de proyecto)

Cada tarifa tiene: `internal_cost` (costo interno) y `billing_rate` (precio al cliente).

### 7. Gastos de Proyecto

El modelo `ProjectExpense` registra gastos no humanos:
- Categorizados (herramientas, servicios, viajes, etc.)
- Clasificados como `billable` o `non_billable`
- Flujo de aprobación de gastos

### 8. Sistema de Invitaciones y Colaboradores

El flujo para sumar un empleado a un proyecto es:

```
Admin crea empleado en el proyecto →
Admin envía invitación por email →
Usuario registrado (o nuevo) recibe email con token →
Usuario acepta → se vincula automáticamente al empleado →
Notificación al admin
```

- Si el usuario aún no existe en el sistema, se lo invita a registrarse
- Las invitaciones tienen expiración configurable y contador de reenvíos
- Al aceptar, se crea la relación `EmpleadoUsuario` con rol `empleado`

### 9. Auditoría y Trazabilidad (Caja Negra)

El modelo `AuditLog` registra **todas las acciones críticas** del sistema:

- Quién hizo la acción (usuario, email, rol en ese momento)
- Qué hizo (acción + categoría + descripción)
- A qué recurso afectó (tipo + ID + nombre)
- Valores anteriores y nuevos (old_value / new_value en JSON)
- IP address y user agent del cliente
- Severidad: `info`, `warning`, `critical`

Acciones auditadas: login/logout, crear/eliminar proyectos, cambios de rol, aprobar/rechazar timesheets, bloquear períodos, ver costos, exportar reportes, entre otras.

### 10. Notificaciones Internas

Sistema de notificaciones en tiempo real dentro de la plataforma:
- Invitación aceptada/rechazada
- Timesheet enviado para aprobación
- Período aprobado/rechazado
- Alertas de presupuesto excedido

### 11. Scheduler Automático (Proceso Separado)

`scheduler.py` corre como un proceso aparte con dos trabajos cron:

| Tarea | Frecuencia | Función |
|-------|-----------|---------|
| Marcado automático de salida | Cada hora en punto | Si un empleado no marcó salida, el sistema lo hace |
| Procesamiento de horas extras | Cada 2 horas | Detecta y registra horas extra con confirmación |

### 12. Exportación de Proyectos

Endpoint dedicado (`proyecto_export_bp`) para exportar la información de proyectos colaborativos (detalles + horas trabajadas).

---

## Funcionalidades Modeladas / Preparadas (no completamente activas)

| Funcionalidad | Estado | Descripción |
|--------------|--------|-------------|
| Planes de suscripción | Estructurado | El modelo `Organization` tiene `plan_type` (free/starter/professional/enterprise) y límites de proyectos/miembros, pero la lógica de cobro y restricción no está activa |
| Vista pública de proyecto | Preparado | El proyecto tiene `public_view` en `modules_config`, pero la lógica de renderizado público no está completa |
| Límites por plan | Estructurado | `limite_proyectos`, `limite_miembros`, `limite_almacenamiento_mb` en el modelo, sin enforcement en código |
| RBAC granular | Parcial | `OrganizationMember` maneja roles, pero permisos granulares por módulo están en proceso |
| Alertas de presupuesto por email | Parcial | La lógica de `should_send_alert()` existe en el modelo, pero el trigger de email automático al superar el umbral puede estar pendiente |

---

## Flujo Completo de Uso (Caso típico)

```
1. El usuario se registra
   └── Se crea automáticamente su Organización personal

2. Crea una Organización para su empresa
   └── Configura nombre, moneda, zona horaria

3. Crea un Proyecto dentro de la organización
   └── Define tipo (personal/empleados), modo horario, presupuesto, módulos

4. Agrega Empleados al proyecto (tipo: empleados)
   └── Envía invitación por email a cada uno

5. Los empleados aceptan y se vinculan con sus cuentas de usuario

6. Los empleados marcan asistencia diariamente
   └── El scheduler procesa marcados olvidados automáticamente

7. Al fin del mes, los empleados envían su período para aprobación
   │  Estado: draft → pending
   └── El admin aprueba o rechaza con notas

8. El admin visualiza la rentabilidad del proyecto en tiempo real
   └── Horas, costos internos, ingresos facturables, burn rate

9. Todas las acciones quedan registradas en el AuditLog (caja negra)
```

---

## Ventajas Técnicas del Sistema

1. **Multi-tenant nativo desde la base**: cada organización es un universo de datos completamente isolado. No hay contaminación de datos entre clientes.

2. **Escalabilidad por fases**: cada fase agrega funcionalidad sin romper la anterior. El código usa feature flags en `modules_config` por proyecto.

3. **Marcado automático resiliente**: si el empleado se olvida de marcar salida, el scheduler lo cubre, evitando registros inconsistentes.

4. **Rentabilidad en tiempo real**: no hay reports de fin de mes; los cálculos de costo, margen y burn rate son instantáneos con los datos actuales.

5. **Auditoría inmutable como caja negra**: cada acción crítica es registrada con estado anterior y nuevo, IP y rol del usuario en ese momento. Útil para compliance y disputas internas.

6. **Tarifas en cascada**: la lógica de `Rate.get_effective_rate()` resuelve automáticamente si se usa la tarifa del usuario, del proyecto o de la organización, en ese orden de prioridad.

7. **Sistema de invitaciones robusto**: maneja usuarios existentes y nuevos, reenvíos, expiración, y no falla si el email no se puede enviar (la invitación igual se crea).

8. **Separación clara de responsabilidades**: `models/` (datos), `services/` (dominio), `routes/` (HTTP), `utils/` (helpers). El frontend tiene la misma separación con `services/`, `handlers/` y `stores/`.
