# TimeFlow — Visión General del Sistema

## ¿Qué es TimeFlow?

TimeFlow es una plataforma integral de gestión de tiempo, proyectos y recursos humanos. Permite a equipos y organizaciones trackear horas trabajadas, gestionar proyectos con tareas granulares, administrar colaboradores, y controlar presupuestos y rentabilidad — todo desde una interfaz web unificada con soporte multi-tenant.

---

## Stack Tecnológico

| Capa | Tecnología | Versión | Notas |
|------|-----------|---------|-------|
| **Frontend** | Astro (SSR) | 6.1.3 | Server-side rendering con `@astrojs/node` |
| **Interactividad** | Alpine.js | 3.15+ | Reactividad declarativa en HTML, sin framework SPA |
| **Estilos** | Tailwind CSS | 4.2 | Configuración nativa con `@import "tailwindcss"` + `@theme` |
| **Design Tokens** | CSS Custom Properties | — | Namespace `--tf-*` en `tokens.css` |
| **State Management** | Nanostores | 1.2 | Store de organizaciones global |
| **Backend** | Flask (Python) | — | API REST con blueprints |
| **ORM** | SQLAlchemy | — | Modelos declarativos, migraciones SQL manuales |
| **Base de Datos** | MySQL | 8.0 | UTF-8 mb4, `mysql_native_password` |
| **Auth** | JWT | — | httpOnly cookies, middleware server-side |
| **Infraestructura** | Docker + docker-compose | — | 3 servicios: db, backend, frontend |
| **Scheduler** | APScheduler | — | Tareas programadas (cierre de períodos, etc.) |
| **PDF** | jsPDF + html2canvas | — | Exportación de reportes |
| **Alertas** | SweetAlert2 | 11.x | Confirmaciones y notificaciones UI |

> **Nota:** React fue integrado en una iteración anterior y posteriormente **eliminado por completo** (Fase 5). Alpine.js maneja TODA la interactividad del frontend.

---

## Arquitectura

### Estructura General

```
TimeFlow/
├── docker-compose.yml          # Orquestación de servicios
├── Makefile                    # Comandos de desarrollo
├── .env                        # Variables de entorno (no versionado)
│
├── backend/
│   ├── main.py                 # Entry point Flask
│   ├── scheduler.py            # APScheduler — tareas programadas
│   ├── requirements.txt        # Dependencias Python
│   ├── Dockerfile
│   ├── app/
│   │   ├── config.py           # Configuración Flask/DB
│   │   ├── decorators.py       # Decoradores de auth y permisos
│   │   ├── models/             # 23 modelos SQLAlchemy
│   │   ├── routes/             # 21 blueprints de API
│   │   ├── services/           # Lógica de negocio
│   │   └── utils/              # Utilidades compartidas
│   ├── migrations/             # SQL de migraciones (versionadas)
│   └── scripts/                # Scripts de mantenimiento
│
├── frontend/
│   ├── astro.config.mjs        # Config Astro + Tailwind 4 vite plugin
│   ├── package.json            # Dependencias (pnpm)
│   ├── Dockerfile
│   └── src/
│       ├── middleware.ts        # Entry de middleware Astro
│       ├── middleware/auth.ts   # Validación JWT server-side
│       ├── components/         # 15 componentes .astro
│       ├── handlers/           # 22 módulos Alpine.js (lógica de página)
│       ├── layouts/            # BaseLayout + BrandedLayout
│       ├── pages/              # ~20 páginas (file-based routing)
│       ├── services/           # 18 servicios API (fetch al backend)
│       ├── stores/             # Nanostores (organizationStore)
│       ├── styles/             # 18 archivos CSS (tokens + global + por feature)
│       ├── types/              # 17 archivos TypeScript de tipos
│       └── utils/              # 24 utilidades (auth, formatters, modals, etc.)
│
└── docs/                       # Documentación del sistema
```

### Flujo de Datos

```
Browser → Astro SSR (middleware auth) → Página .astro → Alpine.js handler
                                                             ↓
                                                      fetch API (service)
                                                             ↓
                                              Flask API (blueprint → service → model)
                                                             ↓
                                                        MySQL 8.0
```

### Docker Services

| Servicio | Container | Puerto |
|----------|-----------|--------|
| MySQL 8.0 | `timeflow_db_dev` | `${DB_PUBLIC_PORT}:3306` |
| Flask Backend | `timeflow_backend_dev` | `${BACKEND_PUBLIC_PORT}:5000` |
| Astro Frontend | `timeflow_frontend_dev` | `${FRONTEND_PUBLIC_PORT}:3000` |

Los 3 servicios están en la red `timeflow-network-dev`. El backend depende del healthcheck de la DB.

---

## Fases de Desarrollo

### Fase 1 — MVP Core
- Autenticación (registro, login, JWT httpOnly)
- CRUD de proyectos con color de marca
- Sistema de tareas con posicionamiento drag & preparado
- Registro de horas diarias por tarea
- Dashboard con métricas de resumen

### Fase 2 — Gestión de Colaboradores y Equipos
- Invitaciones a proyectos por email
- Roles de colaborador (owner, admin, collaborator, viewer)
- Tablero de seguimiento de equipo
- Separación de vistas: tablero-empleado vs tablero-proyecto

### Fase 3 — Motor Financiero y Presupuestos
- Rates (tarifas) por proyecto, colaborador y tipo
- Budgets (presupuesto total del proyecto)
- Budget Addons (ajustes adicionales al presupuesto)
- Expenses (gastos del proyecto)
- Cálculo de rentabilidad en tiempo real (BurnBar, ProfitabilityMeter)
- Exportación de proyectos a PDF

### Fase 4 — Multi-Tenant, Asistencia y HR
- Organizaciones con planes (free, starter, professional, enterprise)
- Gestión de miembros con roles organizacionales (owner, admin, manager, member, viewer)
- Sistema de asistencia con marcados (entrada/salida)
- Configuración de horarios y turnos
- Sistema de deuda de horas y justificativos
- Aprobaciones workflow (pendiente → aprobado/rechazado)
- Sistema de notificaciones in-app
- Auditoría (audit log)

### Fase 5 — Modernización Frontend
- **Eliminación completa de React** (dependencias, componentes .tsx, configuración)
- Migración de Tailwind CSS v3 → v4 nativo (`@import "tailwindcss"` + `@theme`)
- Sistema de design tokens (`tokens.css` con namespace `--tf-*`)
- Reescritura de 16+ archivos CSS con `@layer components`
- Eliminación de 40+ gradientes hardcodeados → colores sólidos flat
- Accesibilidad ARIA en todos los componentes (roles, landmarks, aria-live)
- Limpieza de 8 archivos muertos
- Corrección de errores TypeScript pre-existentes

---

## Secciones Funcionales

### 1. Autenticación y Usuarios
- Registro con validación de campos
- Login con JWT almacenado en httpOnly cookie
- Middleware server-side que protege rutas
- Perfil de usuario editable
- Logout con limpieza de cookie

### 2. Organizaciones (Multi-Tenant)
- Crear/editar organizaciones
- Invitar miembros con roles
- Selector de organización en el Header
- Contexto organizacional global (Nanostores)
- Planes con límites de features
- Configuración de zona horaria, moneda y formato de fecha

### 3. Proyectos
- CRUD completo con metadatos (nombre, descripción, presupuesto, color de marca)
- Vista de lista con tarjetas y métricas
- Vista detallada con sidebar de meses navegable
- Configuración de proyecto (drawer lateral)
- Color de marca que aplica theming dinámico (BrandedLayout)

### 4. Tareas
- CRUD dentro de proyecto con posición ordenable
- Asignación de horas por día con input especializado (TimeInput)
- Períodos mensuales (mes/año) con cierre automático
- Vista de tabla con totales y promedios

### 5. Colaboradores
- Invitación por email a proyectos
- Roles: owner, admin, collaborator, viewer
- Vista de equipo por proyecto
- Gestión de permisos por rol

### 6. Dashboard
- Resumen de horas del período actual
- Proyectos activos con métricas
- Accesos rápidos a funciones frecuentes

### 7. Motor Financiero
- **Rates**: tarifas configurables por proyecto/colaborador/tipo
- **Budgets**: presupuesto base del proyecto
- **Budget Addons**: ajustes incrementales al presupuesto
- **Expenses**: gastos asociados al proyecto
- **Rentabilidad**: cálculo en tiempo real (ingreso vs costo vs gasto)
- **BurnBar**: visualización de consumo de presupuesto
- **ProfitabilityMeter**: indicador de margen de ganancia

### 8. Exportación PDF
- Exportación de vista de proyecto a PDF
- Template personalizado (PDFTemplate.astro)
- Generación client-side con jsPDF + html2canvas

### 9. Sistema de Asistencia
- Marcado de entrada/salida
- Configuración de horarios por empleado
- Turnos (mañana, tarde, noche, flexible)
- Registro histórico de asistencia

### 10. Deuda de Horas y Justificativos
- Cálculo automático de horas debidas
- Sistema de justificativos (enfermedad, vacaciones, etc.)
- Workflow de aprobación de justificativos

### 11. Aprobaciones
- Historial de aprobaciones (ApprovalHistoryTimeline)
- Estados: pendiente → aprobado / rechazado
- Notificación al usuario del resultado

### 12. Auditoría
- Registro de acciones del sistema (audit log)
- Filtrado por tipo de acción, usuario y fecha
- Vista dedicada con tabla paginada

---

## Features Preparadas (no activas)

| Feature | Estado | Detalle |
|---------|--------|---------|
| Drag & Drop de tareas | Modelo preparado (`position`) | UI no implementada |
| Notificaciones push | Modelo + rutas | Sin service worker |
| Modo personal (sin org) | Utility preparada | Flag `personalMode` |
| Exportación masiva | Ruta backend | Sin UI |

---

## Flujo de Uso Completo

```
1. Usuario se registra → login → JWT cookie
2. Crea u organización (o usa modo personal)
3. Invita miembros a la organización
4. Crea un proyecto con presupuesto y color de marca
5. Agrega tareas al proyecto
6. Invita colaboradores al proyecto
7. Colaboradores registran horas diarias por tarea
8. El sistema calcula rentabilidad en tiempo real
9. Owner puede exportar reportes a PDF
10. Sistema de asistencia trackea entradas/salidas
11. Deuda de horas se calcula automáticamente
12. Justificativos pasan por workflow de aprobación
13. Auditoría registra todas las acciones relevantes
```

---

## Ventajas Técnicas

- **SSR con Astro**: SEO-friendly, carga rápida, auth seguro server-side
- **Alpine.js sin SPA**: Interactividad sin bundle pesado ni hidratación compleja
- **Tailwind CSS 4 nativo**: Sin config JS, todo en CSS con `@theme`
- **Design Tokens centralizados**: Un solo archivo (`tokens.css`) como fuente de verdad
- **Multi-tenant real**: Aislamiento por organización con RBAC granular
- **Docker-compose**: Setup de desarrollo reproducible en un comando
- **Migraciones SQL explícitas**: Control total sobre el schema, sin magic de frameworks
- **JWT httpOnly**: Auth seguro sin localStorage, protegido contra XSS
