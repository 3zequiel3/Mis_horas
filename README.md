# TimeFlow — Sistema de Gestión de Tiempo y Proyectos

> Plataforma multi-tenant para el seguimiento de horas, gestión de proyectos colaborativos, control de asistencia de empleados y análisis financiero.

---

## Tabla de Contenidos

1. [Descripción General](#descripción-general)
2. [Stack Tecnológico](#stack-tecnológico)
3. [Arquitectura](#arquitectura)
4. [Requisitos Previos](#requisitos-previos)
5. [Instalación Rápida](#instalación-rápida)
6. [Variables de Entorno](#variables-de-entorno)
7. [Comandos Make](#comandos-make)
8. [Backend](#backend)
   - [Estructura de Archivos](#estructura-de-archivos-backend)
   - [Autenticación y Autorización](#autenticación-y-autorización)
   - [Modelos de Base de Datos](#modelos-de-base-de-datos)
   - [API Endpoints](#api-endpoints)
   - [Servicios](#servicios-backend)
9. [Frontend](#frontend)
   - [Estructura de Archivos](#estructura-de-archivos-frontend)
   - [Páginas](#páginas)
   - [Servicios](#servicios-frontend)
   - [Handlers](#handlers)
   - [Utilidades](#utilidades)
   - [Stores](#stores)
   - [Componentes](#componentes)
10. [Tipos de Proyectos](#tipos-de-proyectos)
11. [Sistema de Colaboradores](#sistema-de-colaboradores)
12. [Motor Financiero](#motor-financiero)
13. [Sistema de Asistencia](#sistema-de-asistencia)
14. [Generación de PDF](#generación-de-pdf)
15. [Multi-tenant](#multi-tenant)
16. [Migraciones de Base de Datos](#migraciones-de-base-de-datos)

---

## Descripción General

TimeFlow es una aplicación web full-stack diseñada para el seguimiento de tiempo y la gestión de proyectos. Permite a los usuarios registrar horas trabajadas por día y tarea, gestionar proyectos de forma personal o colaborativa, administrar equipos de empleados con control de asistencia, y analizar la rentabilidad financiera mediante presupuestos, tarifas y gastos.

El sistema soporta **múltiples organizaciones** (multi-tenant): cada usuario puede pertenecer a una o más organizaciones y todos los datos están aislados por organización.

---

## Stack Tecnológico

### Backend
| Tecnología | Versión | Uso |
|---|---|---|
| Python | 3.x | Lenguaje principal |
| Flask | 3.0.0 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| PyMySQL | 1.1.1 | Driver MySQL |
| Flask-CORS | 4.0.0 | Cross-Origin Resource Sharing |
| PyJWT | 2.10.1 | Autenticación JWT |
| APScheduler | 3.10.4 | Tareas programadas (marcado automático de asistencia) |
| Pillow | 10.0.0 | Procesamiento de imágenes |
| python-dotenv | — | Variables de entorno |

### Frontend
| Tecnología | Versión | Uso |
|---|---|---|
| Astro | 5.x | Framework SSR/SSG |
| TypeScript | 5.9 | Lenguaje principal |
| Tailwind CSS | 3.4 | Estilos |
| Alpine.js | 3.x | Interactividad declarativa |
| Nanostores | — | Gestión de estado global |
| jsPDF | 3.x | Generación de PDF en el cliente |
| SweetAlert2 | 11.x | Modales y alertas |
| html2canvas | — | Capturas de pantalla para PDF |

### Infraestructura
| Servicio | Tecnología | Puerto interno | Puerto público |
|---|---|---|---|
| Base de datos | MySQL 8.0 | 3306 | 21100 (solo dev) |
| Backend (API) | Flask | 5000 | 22000 |
| Frontend | Astro | 4321 | 21000 |

---

## Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Compose                          │
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   frontend   │    │   backend    │    │      db      │  │
│  │  (Astro SSR) │───▶│  (Flask API) │───▶│  (MySQL 8.0) │  │
│  │  :4321→21000 │    │  :5000→22000 │    │  :3306→21100 │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                             │
│              Red interna: mishoras-network                  │
│              Volumen persistente: mysql_data                │
└─────────────────────────────────────────────────────────────┘
```

**Comunicación:**
- El navegador del usuario accede al frontend en `http://localhost:21000`
- El frontend (tanto SSR como cliente) llama al backend en `http://localhost:22000`
- El backend se conecta a la base de datos usando el nombre de servicio Docker `db:3306`
- La base de datos **no tiene puerto público** en producción

---

## Requisitos Previos

- [Docker](https://docs.docker.com/get-docker/) >= 24.x
- [Docker Compose](https://docs.docker.com/compose/) >= 2.x
- `make` (incluido en la mayoría de distribuciones Linux/macOS)

---

## Instalación Rápida

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd TimeFlow

# 2. Crear y configurar el archivo de entorno
cp .env.example .env
# Editar .env con los valores apropiados (ver sección Variables de Entorno)

# 3. Construir e iniciar los servicios
make start

# El sistema estará disponible en:
# Frontend:  http://localhost:21000
# Backend:   http://localhost:22000
```

> **Nota:** La primera ejecución puede tardar varios minutos porque Docker descarga las imágenes base y construye los contenedores.

---

## Variables de Entorno

Todas las variables son **obligatorias**. El contenedor no levantará si falta alguna.

Copiar `.env.example` a `.env` y completar todos los valores:

| Variable | Ejemplo | Descripción |
|---|---|---|
| `NODE_ENV` | `development` | Modo del frontend (`production` \| `development`) |
| `FLASK_ENV` | `development` | Modo del backend (`production` \| `development`) |
| `FLASK_DEBUG` | `True` | Debug de Flask (`True` \| `False`) |
| `DB_HOST` | `db` | Host de MySQL (nombre del servicio Docker) |
| `DB_PORT` | `3306` | Puerto interno de MySQL |
| `DB_USER` | `mis_horas` | Usuario de la base de datos |
| `DB_PASSWORD` | `mis_horas` | Contraseña del usuario |
| `DB_NAME` | `mis_horas` | Nombre de la base de datos |
| `DB_ROOT_PASSWORD` | `root` | Contraseña del root de MySQL |
| `FRONTEND_PUBLIC_PORT` | `21000` | Puerto público del frontend |
| `BACKEND_PUBLIC_PORT` | `22000` | Puerto público del backend |
| `API_HOST` | `0.0.0.0` | IP de escucha del servidor Flask |
| `API_PORT` | `5000` | Puerto interno del contenedor Flask |
| `SECRET_KEY` | `...` | Clave secreta para JWT (generar con `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `JWT_EXPIRATION_HOURS` | `720` | Tiempo de expiración del token JWT (horas) |
| `CORS_ORIGINS` | `http://localhost:21000` | Orígenes permitidos para CORS (separados por coma) |
| `VITE_API_URL` | `http://localhost:22000` | URL del backend accesible desde el **navegador del cliente** |

### Configuración por entorno

**Desarrollo (live reload activo):**
```env
NODE_ENV=development
FLASK_ENV=development
FLASK_DEBUG=True
```

**Producción:**
```env
NODE_ENV=production
FLASK_ENV=production
FLASK_DEBUG=False
SECRET_KEY=<clave-aleatoria-segura>
CORS_ORIGINS=https://tu-dominio.com
VITE_API_URL=https://api.tu-dominio.com
```

---

## Comandos Make

| Comando | Descripción |
|---|---|
| `make start` | Construye las imágenes (sin caché) e inicia todos los servicios en segundo plano |
| `make restart` | Reinicia todos los servicios sin reconstruir |
| `make logs` | Muestra los logs en tiempo real de todos los servicios |
| `make logs-backend` | Logs en tiempo real solo del backend |
| `make logs-frontend` | Logs en tiempo real solo del frontend |
| `make logs-db` | Logs en tiempo real solo de la base de datos |
| `make bash-backend` | Abre una shell `bash` dentro del contenedor del backend |
| `make bash-frontend` | Abre una shell `sh` dentro del contenedor del frontend |
| `make bash-db` | Abre una consola MySQL dentro del contenedor de la base de datos |
| `make ps` | Lista el estado de todos los contenedores |
| `make clean` | Detiene y elimina los contenedores y volúmenes (⚠️ borra los datos de la BD) |
| `make rebuild` | Ejecuta `clean` + `start` (reconstrucción completa desde cero) |

---

## Backend

### Estructura de Archivos (Backend)

```
backend/
├── main.py                    # Punto de entrada — crea la app y ejecuta el servidor
├── scheduler.py               # Configuración de APScheduler (tareas automáticas)
├── requirements.txt           # Dependencias Python
├── Dockerfile
└── app/
    ├── __init__.py            # Factory function create_app() — registra blueprints y extensiones
    ├── config.py              # Validación y carga de variables de entorno obligatorias
    ├── decorators.py          # Decoradores de autenticación: @token_required, @organization_required
    ├── models/                # Modelos SQLAlchemy (ver sección Modelos)
    ├── routes/                # Blueprints Flask con los endpoints de la API
    ├── services/              # Lógica de negocio desacoplada de los endpoints
    └── utils/                 # Funciones auxiliares
```

### Autenticación y Autorización

El sistema usa **JWT (JSON Web Tokens)** para la autenticación. Todos los endpoints protegidos requieren:

1. **Header `Authorization`:** `Bearer <token>`
2. **Header `X-Organization-ID`:** ID numérico de la organización activa

#### Decoradores disponibles

| Decorador | Descripción | Contexto inyectado |
|---|---|---|
| `@token_required` | Valida solo el JWT | `{'id': user_id}` |
| `@organization_required` | Valida JWT + membresía activa en la organización | `{'user_id', 'organization_id', 'role', 'membership'}` |
| `@requires_permission('permiso')` | Verifica permiso RBAC del rol (usar después de `@organization_required`) | — |

#### Roles de organización

Los roles determinan los permisos dentro de cada organización. La verificación de permisos se hace mediante `membership.tiene_permiso(permiso)`.

#### Flujo de autenticación

```
Cliente ──▶ POST /api/auth/login
         ◀── { token: "eyJ..." }

Solicitud protegida:
Cliente ──▶ GET /api/proyectos
            Headers:
              Authorization: Bearer eyJ...
              X-Organization-ID: 1
         ◀── [{ proyecto }, ...]
```

---

### Modelos de Base de Datos

#### `Usuario` — tabla `usuarios`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `username` | String(50) | Nombre de usuario único |
| `email` | String(100) | Email único |
| `password_hash` | String(255) | Contraseña hasheada |
| `nombre_completo` | String(100) | Nombre para mostrar |
| `avatar_url` | Text | URL del avatar |
| `activo` | Boolean | Si el usuario está activo |
| `es_admin` | Boolean | Rol de administrador global |
| `email_verificado` | Boolean | Estado de verificación de email |
| `primer_dia_semana` | Integer | 0=Domingo, 1=Lunes |
| `created_at` | DateTime | Fecha de creación (UTC) |
| `last_login` | DateTime | Último inicio de sesión |

---

#### `Proyecto` — tabla `proyectos`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(255) | Nombre del proyecto |
| `descripcion` | Text | Descripción opcional |
| `mes` | Integer | Mes del proyecto |
| `anio` | Integer | Año del proyecto |
| `usuario_id` | FK → `usuarios` | Propietario del proyecto |
| `activo` | Boolean | Si el proyecto está activo |
| `tipo_proyecto` | String(50) | `'personal'` \| `'empleados'` \| `'colaborativo'` |
| `horas_reales_activas` | Boolean | Si usa horas reales en vez de estimadas |
| `modo_horas` | String(20) | `'corrido'` \| `'turnos'` |
| `hora_inicio` / `hora_fin` | Time | Rango de horas (modo corrido) |
| `turno_inicio` / `turno_fin` | Time | Horario del turno (modo turnos) |
| `billing_type` | String(30) | `'fixed_price'` \| `'hourly_retainer'` \| `'time_and_materials'` \| `'none'` |
| `budget_amount` | Numeric(12,2) | Presupuesto total del proyecto |
| `currency` | String(3) | Moneda (ej: `'USD'`) |
| `features` | JSON | Módulos habilitados: `{budget, time_tracking, audit, approvals, public_view}` |
| `color` | String(7) | Color en hex (ej: `#3B82F6`) |
| `icono` | String(255) | Icono del proyecto |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Última actualización |

---

#### `Tarea` — tabla `tareas`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(255) | Nombre de la tarea |
| `descripcion` | Text | Descripción opcional |
| `estado` | String(50) | Estado de la tarea |
| `notas` | Text | Notas adicionales |
| `proyecto_id` | FK → `proyectos` | Proyecto al que pertenece |
| `mes` | Integer | Mes de la tarea |
| `anio` | Integer | Año de la tarea |
| `usuario_colaborador_id` | FK → `usuarios` | Colaborador asignado (nullable) |

**Relación muchos-a-muchos:** `tarea_dias` (tabla asociación `tarea_id` ↔ `dia_id`)

---

#### `Dia` — tabla `dias`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `fecha` | Date | Fecha del día |
| `tipo_dia` | String(20) | Tipo de día (laborable, feriado, etc.) |
| `horas_trabajadas` | Float | Horas del propietario del proyecto |
| `horas_estimadas` | Float | Horas estimadas |
| `hora_inicio` / `hora_fin` | Time | Rango horario (modo corrido) |
| `turno_inicio` / `turno_fin` | Time | Horario de turno |
| `horas_extra` | Float | Horas extra registradas |
| `proyecto_id` | FK → `proyectos` | Proyecto al que pertenece |
| `usuario_id` | FK → `usuarios` | Usuario propietario (nullable en proyectos personales) |
| `tarea_id` | FK → `tareas` | Tarea asociada (nullable) |

> ⚠️ En proyectos **colaborativos**, los días son **compartidos** entre todos los colaboradores. Las horas individuales se almacenan en `DiaColaborador`.

---

#### `DiaColaborador` — tabla `dias_colaboradores`

Almacena las horas trabajadas **por colaborador** en cada día de un proyecto colaborativo.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `dia_id` | FK → `dias` | Día al que pertenece |
| `usuario_id` | FK → `usuarios` | Colaborador |
| `horas_trabajadas` | Float | Horas del colaborador en ese día |
| `hora_inicio` / `hora_fin` | Time | Rango horario del colaborador |
| `created_at` | DateTime | Fecha de creación |
| `updated_at` | DateTime | Última actualización |

---

#### `ProyectoColaborador` — tabla `proyecto_colaboradores`

Registra los miembros de un proyecto colaborativo.

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `proyecto_id` | FK → `proyectos` (CASCADE) | Proyecto |
| `usuario_id` | FK → `usuarios` (CASCADE) | Usuario colaborador |
| `rol` | Enum | `'owner'` \| `'colaborador'` |
| `activo` | Boolean | Si la colaboración está activa |
| `estado` | Enum | `'pendiente'` \| `'aceptado'` \| `'rechazado'` |
| `fecha_union` | DateTime | Cuándo se unió |
| `horas_reales_activas` | Boolean | Configuración de horas reales para este colaborador |

**Constraint:** UNIQUE (`proyecto_id`, `usuario_id`)

---

#### `Empleado` — tabla `empleados`

| Columna | Tipo | Descripción |
|---|---|---|
| `id` | Integer PK | Identificador único |
| `nombre` | String(255) | Nombre del empleado |
| `proyecto_id` | FK → `proyectos` | Proyecto (tablero de empleados) al que pertenece |
| `activo` | Boolean | Si el empleado está activo |
| `usuario_id` | FK → `usuarios` | Vínculo con cuenta de usuario del sistema (opcional) |
| `estado` | Enum | `'activo'` \| `'inactivo'` \| `'suspendido'` |
| `hora_entrada` / `hora_salida` | Time | Horario laboral del empleado |
| `es_visitante` | Boolean | Si es un visitante temporal |
| `created_at` | DateTime | Fecha de creación |

---

#### Otros modelos relevantes

| Modelo | Tabla | Descripción |
|---|---|---|
| `Organization` | `organizations` | Organización (tenant) |
| `OrganizationMember` | `organization_members` | Membresía usuario-organización con rol |
| `Budget` | `budgets` | Presupuestos de proyectos |
| `Rate` | `rates` | Tarifas horarias (por usuario, proyecto u organización) |
| `ProjectExpense` | `project_expenses` | Gastos de proyectos |
| `ProjectBudgetAddon` | `project_budget_addons` | Ajustes de presupuesto |
| `AuditLog` | `audit_logs` | Registro de auditoría |
| `Notificacion` | `notificaciones` | Notificaciones de usuario |
| `InvitacionProyecto` | `invitaciones_proyecto` | Invitaciones a proyectos colaborativos |
| `MarcadoAsistencia` | `marcados_asistencia` | Registro de entradas/salidas de empleados |
| `DeudaHoras` | `deuda_horas` | Deudas de horas de empleados |
| `Justificacion` | `justificaciones` | Justificaciones de ausencias |
| `TimePeriod` | `time_periods` | Períodos de aprobación de tiempo |

---

### API Endpoints

#### Autenticación — `/api/auth`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/auth/login` | Iniciar sesión. Retorna JWT token |
| `POST` | `/api/auth/register` | Registrar nuevo usuario |
| `GET` | `/api/auth/me` | Obtener perfil del usuario actual |
| `PUT` | `/api/auth/me` | Actualizar perfil del usuario |
| `POST` | `/api/auth/logout` | Cerrar sesión |
| `POST` | `/api/auth/refresh` | Renovar token JWT |
| `POST` | `/api/auth/change-password` | Cambiar contraseña |

---

#### Proyectos — `/api/proyectos`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/proyectos` | Listar proyectos del usuario en la organización |
| `POST` | `/api/proyectos` | Crear nuevo proyecto (`tipo_proyecto`: `personal`, `empleados`, `colaborativo`) |
| `GET` | `/api/proyectos/<id>` | Obtener un proyecto |
| `PUT` | `/api/proyectos/<id>` | Actualizar proyecto |
| `DELETE` | `/api/proyectos/<id>` | Eliminar proyecto |
| `GET` | `/api/proyectos/estadisticas` | Estadísticas globales de proyectos |
| `GET` | `/api/proyectos/<id>/config` | Obtener configuración del proyecto |
| `PUT` | `/api/proyectos/<id>/config` | Actualizar configuración |
| `PUT` | `/api/proyectos/<id>/tipo` | Cambiar tipo del proyecto (ej: convertir a colaborativo) |

---

#### Tareas — `/api/tareas`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/tareas` | Listar tareas (filtro por proyecto, mes, año) |
| `POST` | `/api/tareas` | Crear nueva tarea |
| `GET` | `/api/tareas/<id>` | Obtener una tarea |
| `PUT` | `/api/tareas/<id>` | Actualizar tarea (recalcula horas con contexto de colaborador) |
| `DELETE` | `/api/tareas/<id>` | Eliminar tarea |
| `PATCH` | `/api/tareas/<id>/estado` | Cambiar estado de la tarea |
| `GET` | `/api/tareas/<id>/horas` | Obtener horas calculadas de la tarea |

---

#### Días — `/api/dias`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/dias` | Listar días del mes (filtro por proyecto, mes, año) |
| `GET` | `/api/dias/<id>` | Obtener un día |
| `PUT` | `/api/dias/<id>` | Actualizar día |
| `PUT` | `/api/dias/<id>/horas` | Registrar horas trabajadas. En proyectos colaborativos retorna horas del colaborador actual |
| `PUT` | `/api/dias/<id>/config` | Actualizar configuración del día |

---

#### Colaboradores — `/api/proyectos/<id>/colaboradores`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/proyectos/<id>/colaboradores/convertir` | Convertir proyecto personal a colaborativo |
| `GET` | `/api/proyectos/<id>/colaboradores` | Listar colaboradores del proyecto |
| `POST` | `/api/proyectos/<id>/colaboradores/invitar` | Invitar colaborador por email/username |
| `DELETE` | `/api/proyectos/<id>/colaboradores/<usuario_id>` | Eliminar colaborador |
| `PUT` | `/api/proyectos/<id>/colaboradores/<usuario_id>/config` | Actualizar configuración del colaborador |
| `GET` | `/api/proyectos/<id>/colaboradores/estadisticas` | Estadísticas de horas por colaborador |

---

#### Exportación de Proyectos Colaborativos

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/proyectos/<id>/export-colaboradores` | Exportar datos de todos los colaboradores (para PDF/CSV) |

---

#### Usuarios — `/api/usuarios`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/usuarios/buscar` | Buscar usuarios (para invitar a proyectos) |

---

#### Empleados — `/api`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/empleados` | Listar empleados del proyecto |
| `POST` | `/api/empleados` | Crear empleado |
| `GET` | `/api/empleados/<id>` | Obtener empleado |
| `PUT` | `/api/empleados/<id>` | Actualizar empleado |
| `DELETE` | `/api/empleados/<id>` | Eliminar empleado |

---

#### Asistencia — `/api`

| Método | Ruta | Descripción |
|---|---|---|
| `POST` | `/api/marcar-entrada` | Registrar entrada de empleado |
| `POST` | `/api/marcar-salida` | Registrar salida de empleado |
| `GET` | `/api/marcados` | Listar marcados de asistencia |
| `POST` | `/api/detectar-ausencias` | Detectar y registrar ausencias automáticamente |
| `GET` | `/api/asistencia/<empleado_id>` | Historial de asistencia de un empleado |
| `PUT` | `/api/marcados/<id>/editar` | Editar registro de asistencia |
| `PUT` | `/api/marcados/<id>/confirmar-horas-extras` | Confirmar horas extras |

---

#### Deudas de Horas — `/api/deudas`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/deudas/<empleado_id>` | Obtener deudas de un empleado |
| `GET` | `/api/deudas` | Listar todas las deudas |
| `POST` | `/api/deudas` | Registrar deuda de horas |
| `PUT` | `/api/deudas/justificaciones/<id>/aprobar` | Aprobar justificación |
| `PUT` | `/api/deudas/justificaciones/<id>/rechazar` | Rechazar justificación |
| `GET` | `/api/deudas/justificaciones` | Listar justificaciones |
| `GET` | `/api/deudas/resumen` | Resumen de deudas |

---

#### Organizaciones — `/api/organizations`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/organizations` | Listar organizaciones del usuario |
| `POST` | `/api/organizations` | Crear organización |
| `GET` | `/api/organizations/<id>` | Obtener organización |
| `PUT` | `/api/organizations/<id>` | Actualizar organización |
| `DELETE` | `/api/organizations/<id>` | Eliminar organización |
| `GET` | `/api/organizations/<id>/stats` | Estadísticas de la organización |
| `GET` | `/api/organizations/<id>/members` | Listar miembros |
| `POST` | `/api/organizations/<id>/members/invite` | Invitar miembro |
| `DELETE` | `/api/organizations/<id>/members/<user_id>` | Eliminar miembro |
| `PUT` | `/api/organizations/<id>/members/<user_id>/role` | Cambiar rol del miembro |
| `POST` | `/api/organizations/invitations/accept/<token>` | Aceptar invitación |

---

#### Invitaciones a Proyectos — `/api/invitaciones`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/invitaciones/buscar-usuarios` | Buscar usuarios para invitar |
| `POST` | `/api/invitaciones` | Crear invitación |
| `POST` | `/api/invitaciones/enviar` | Enviar invitación por email |
| `GET` | `/api/invitaciones/mis-invitaciones` | Obtener invitaciones del usuario |
| `POST` | `/api/invitaciones/<id>/aceptar` | Aceptar invitación |
| `POST` | `/api/invitaciones/<id>/rechazar` | Rechazar invitación |
| `POST` | `/api/invitaciones/<id>/cancelar` | Cancelar invitación |
| `GET` | `/api/invitaciones/proyecto/<id>` | Invitaciones de un proyecto |
| `GET` | `/api/invitaciones/<id>` | Obtener invitación |

---

#### Notificaciones — `/api/notificaciones`

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/notificaciones/` | Listar notificaciones |
| `GET` | `/api/notificaciones/contador` | Contador de no leídas |
| `PUT` | `/api/notificaciones/<id>/marcar-leida` | Marcar como leída |
| `PUT` | `/api/notificaciones/marcar-todas-leidas` | Marcar todas como leídas |
| `PUT` | `/api/notificaciones/<id>/archivar` | Archivar notificación |
| `DELETE` | `/api/notificaciones/<id>` | Eliminar notificación |

---

#### Motor Financiero

**Tarifas — `/api/rates`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/rates` | Listar tarifas |
| `GET` | `/api/rates/<id>` | Obtener tarifa |
| `POST` | `/api/rates` | Crear tarifa (por usuario, proyecto u organización) |
| `PUT` | `/api/rates/<id>` | Actualizar tarifa |
| `DELETE` | `/api/rates/<id>` | Eliminar tarifa |
| `GET` | `/api/rates/effective` | Tarifa efectiva (resuelve jerarquía: usuario > proyecto > org) |
| `GET` | `/api/rates/project/<id>/hierarchy` | Jerarquía de tarifas del proyecto |

**Presupuestos — `/api/budgets`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/budgets/project/<id>` | Presupuesto del proyecto |
| `POST` | `/api/budgets` | Crear presupuesto |
| `PUT` | `/api/budgets/<id>` | Actualizar presupuesto |
| `GET` | `/api/budgets/<id>/summary` | Resumen del presupuesto |
| `POST` | `/api/budgets/<id>/alert` | Configurar alerta |
| `POST` | `/api/budgets/<id>/snapshot` | Crear snapshot del presupuesto |
| `POST` | `/api/budgets/<id>/recalculate` | Recalcular presupuesto |
| `GET` | `/api/budgets/<id>/history` | Historial del presupuesto |
| `GET` | `/api/budgets/<id>/alerts` | Alertas del presupuesto |

**Gastos — `/api/expenses`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/expenses/project/<id>` | Gastos del proyecto |
| `GET` | `/api/expenses/<id>` | Obtener gasto |
| `POST` | `/api/expenses` | Registrar gasto |
| `PUT` | `/api/expenses/<id>` | Actualizar gasto |
| `POST` | `/api/expenses/<id>/approve` | Aprobar gasto |
| `POST` | `/api/expenses/<id>/reject` | Rechazar gasto |
| `DELETE` | `/api/expenses/<id>` | Eliminar gasto |
| `GET` | `/api/expenses/project/<id>/total` | Total de gastos |
| `GET` | `/api/expenses/project/<id>/summary` | Resumen de gastos |
| `GET` | `/api/expenses/project/<id>/pending` | Gastos pendientes de aprobación |

**Rentabilidad — `/api/profitability`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/profitability/project/<id>` | Rentabilidad del proyecto |
| `GET` | `/api/profitability/<id>` | Detalle de rentabilidad |
| `GET` | `/api/profitability/monthly/<year>/<month>` | Rentabilidad mensual |
| `GET` | `/api/profitability/project/<id>/budget-health` | Estado del presupuesto |
| `GET` | `/api/profitability/projects-at-risk` | Proyectos en riesgo financiero |
| `GET` | `/api/profitability/employee/<user_id>/cost` | Costo de empleado |
| `GET` | `/api/profitability/project/<id>/expense-summary` | Resumen de gastos vs presupuesto |
| `GET` | `/api/profitability/dashboard` | Dashboard financiero global |

**Add-ons de Presupuesto — `/api/projects`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/projects/<id>/budget-addons` | Listar add-ons |
| `POST` | `/api/projects/<id>/budget-addons` | Crear add-on |
| `PUT` | `/api/projects/<id>/budget-addons/<addon_id>` | Actualizar add-on |
| `DELETE` | `/api/projects/<id>/budget-addons/<addon_id>` | Eliminar add-on |
| `GET` | `/api/projects/<id>/budget-addons/summary` | Resumen de add-ons |

---

#### Aprobaciones y Auditoría

**Períodos de aprobación — `/api/approvals`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/approvals/periods` | Listar períodos |
| `GET` | `/api/approvals/pending` | Períodos pendientes de aprobación |
| `GET` | `/api/approvals/periods/<id>` | Obtener período |
| `POST` | `/api/approvals/periods/<id>/submit` | Enviar para aprobación |
| `POST` | `/api/approvals/periods/<id>/approve` | Aprobar período |
| `POST` | `/api/approvals/periods/<id>/reject` | Rechazar período |
| `POST` | `/api/approvals/periods/<id>/reopen` | Reabrir período |
| `POST` | `/api/approvals/periods/<id>/lock` | Bloquear período |

**Auditoría — `/api/audit`**

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/audit/logs` | Listar logs de auditoría |
| `GET` | `/api/audit/recent` | Logs recientes |
| `GET` | `/api/audit/<id>` | Obtener log |
| `GET` | `/api/audit/resources/<type>/<id>` | Logs de un recurso específico |
| `GET` | `/api/audit/statistics` | Estadísticas de auditoría |
| `GET` | `/api/audit/export` | Exportar logs |

---

### Servicios (Backend)

Los servicios encapsulan la lógica de negocio y son llamados desde los blueprints:

| Servicio | Archivo | Responsabilidad |
|---|---|---|
| `ProyectoService` | `proyecto_service.py` | CRUD de proyectos, validaciones |
| `TareaService` | `tarea_service.py` | CRUD de tareas, cálculo de horas por tarea |
| `DiaService` | `dia_service.py` | CRUD de días, cálculo de horas mensuales |
| `ColaboradoresService` | `colaboradores_service.py` | Gestión de proyectos colaborativos, estadísticas |
| `EmpleadoService` | `empleado_service.py` | Gestión de empleados |
| `AsistenciaService` | `asistencia_service.py` | Control de asistencia, detección de ausencias |
| `MarcadoAutomaticoService` | `marcado_automatico_service.py` | Marcado automático de entrada/salida |
| `InvitacionService` | `invitacion_service.py` | Envío y gestión de invitaciones |
| `NotificacionService` | `notificacion_service.py` | Sistema de notificaciones |
| `OrganizationService` | `organization_service.py` | Gestión de organizaciones y membresías |
| `AuditService` | `audit_service.py` | Registro de eventos de auditoría |
| `ProfitabilityService` | `profitability_service.py` | Cálculos financieros y de rentabilidad |
| `TimePeriodService` | `time_period_service.py` | Gestión de períodos de aprobación |
| `EmailService` | `email_service.py` | Envío de emails (invitaciones, notificaciones) |

---

## Frontend

### Estructura de Archivos (Frontend)

```
frontend/
├── astro.config.mjs           # Configuración de Astro
├── tailwind.config.mjs        # Configuración de Tailwind CSS
├── tsconfig.json
├── package.json
├── public/                    # Archivos estáticos
└── src/
    ├── env.d.ts               # Tipado de variables de entorno Astro
    ├── alpinejs.d.ts          # Tipos de Alpine.js
    ├── middleware.ts          # Middleware de Astro (auth guard)
    ├── components/            # Componentes Astro reutilizables
    ├── handlers/              # Lógica de interacción por página
    ├── layouts/               # Layouts Astro
    ├── middleware/            # Middleware adicional
    ├── pages/                 # Rutas de la aplicación
    ├── services/              # Clientes HTTP hacia el backend
    ├── stores/                # Estado global (Nanostores)
    ├── styles/                # Estilos globales
    ├── types/                 # Tipos TypeScript
    └── utils/                 # Funciones utilitarias
```

---

### Páginas

| Archivo | Ruta URL | Descripción |
|---|---|---|
| `index.astro` | `/` | Página de bienvenida o redirección |
| `login.astro` | `/login` | Inicio de sesión |
| `register.astro` | `/register` | Registro de usuario |
| `dashboard.astro` | `/dashboard` | Panel principal con resumen de proyectos |
| `proyectos.astro` | `/proyectos` | Lista de todos los proyectos |
| `nuevo-proyecto.astro` | `/nuevo-proyecto` | Wizard de creación de proyecto |
| `perfil.astro` | `/perfil` | Perfil y configuración del usuario |
| `proyecto/[id].astro` | `/proyecto/:id` | Vista principal de un proyecto (días, tareas, horas) |
| `tablero-empleados/[id].astro` | `/tablero-empleados/:id` | Tablero de control de empleados |
| `empleado-vista/[id].astro` | `/empleado-vista/:id` | Vista de un empleado individual |
| `tablero-empleado-vista/` | `/tablero-empleado-vista/:id` | Vista del tablero desde perspectiva del empleado |
| `organizaciones.astro` | `/organizaciones` | Gestión de organizaciones del usuario |
| `organizations.astro` | `/organizations` | Lista de organizaciones (alternativa) |
| `invitations.astro` | `/invitations` | Gestión de invitaciones recibidas |

---

### Servicios (Frontend)

Los servicios en `src/services/` son wrappers sobre `fetch` que comunican con la API del backend. Todos incluyen automáticamente los headers `Authorization` y `X-Organization-ID`.

| Archivo | Descripción |
|---|---|
| `api.ts` | Cliente HTTP base (fetch wrapper con interceptores de auth) |
| `auth.ts` | Login, register, perfil, logout |
| `proyectos.ts` | CRUD de proyectos |
| `tarea.ts` | CRUD de tareas |
| `dia.ts` | CRUD de días y registro de horas |
| `colaboradores.ts` | Gestión de colaboradores en proyectos |
| `empleados.ts` | CRUD de empleados |
| `asistencia.ts` | Marcado de asistencia y consultas |
| `invitaciones.ts` | Gestión de invitaciones |
| `notificaciones.ts` | Notificaciones del sistema |
| `organization.ts` / `organizationService.ts` | Gestión de organizaciones |
| `usuarios.ts` | Búsqueda de usuarios |
| `budgetAddonService.ts` | Add-ons de presupuesto |
| `approvalService.ts` | Períodos de aprobación |
| `auditService.ts` | Logs de auditoría |
| `deudas.ts` | Deudas de horas de empleados |
| `configuracion-asistencia.ts` | Configuración del sistema de asistencia |

---

### Handlers

Los handlers en `src/handlers/` contienen toda la lógica de interacción (eventos, estado local, llamadas a servicios) para cada página. Las páginas `.astro` los importan y delegan en ellos el comportamiento dinámico.

| Archivo | Página asociada | Descripción |
|---|---|---|
| `auth.ts` | `login.astro`, `register.astro` | Manejo de formularios de auth |
| `login.ts` | `login.astro` | Lógica específica de login |
| `register.ts` | `register.astro` | Lógica específica de registro |
| `dashboard.ts` | `dashboard.astro` | Carga y render del dashboard |
| `proyectos.ts` | `proyectos.astro` | Lista y acciones sobre proyectos |
| `nuevo-proyecto.ts` | `nuevo-proyecto.astro` | Wizard de creación de proyecto |
| `proyecto.ts` | `proyecto/[id].astro` | Vista completa del proyecto: días, tareas, horas, config |
| `project-view.ts` | `proyecto/[id].astro` | Renderizado de la tabla de días/tareas |
| `tarea.ts` | `proyecto/[id].astro` | CRUD de tareas en la vista del proyecto |
| `tablero-empleados.ts` | `tablero-empleados/[id].astro` | Control del tablero de empleados |
| `gestion-empleados.ts` | `tablero-empleados/[id].astro` | Alta/baja/edición de empleados |
| `asistencia.ts` | `tablero-empleados/[id].astro` | Registro y visualización de asistencia |
| `turnos-modal.ts` | Componente modal | Gestión de turnos de empleados |
| `vista-empleado.ts` | `empleado-vista/[id].astro` | Vista del empleado individual |
| `colaboradores.ts` | `proyecto/[id].astro` | Panel de colaboradores del proyecto |
| `config-drawer.ts` | Componente drawer | Configuración del proyecto |
| `config-horarios.ts` | Componente drawer | Configuración de horarios |
| `configuracion-asistencia.ts` | Tablero de empleados | Configuración del sistema de asistencia |
| `deudas.ts` | Tablero de empleados | Gestión de deudas de horas |
| `justificativos-handler.ts` | Tablero de empleados | Gestión de justificativos |
| `meses.ts` | Varias páginas | Navegación entre meses |
| `perfil.ts` | `perfil.astro` | Edición del perfil de usuario |

---

### Utilidades

Las utilidades en `src/utils/` son funciones puras reutilizables:

| Archivo | Descripción |
|---|---|
| `api.ts` | Wrapper HTTP con headers de auth automáticos |
| `auth.ts` | Helpers de autenticación (leer/guardar token) |
| `jwt.ts` | Decodificación del token JWT en el cliente |
| `cookies.ts` | Lectura y escritura de cookies |
| `storage.ts` | Abstracción sobre `localStorage` |
| `date.ts` | Formateo y manipulación de fechas |
| `formatters.ts` | Formateo de números, horas, monedas |
| `hours.ts` | Cálculos relacionados con horas trabajadas |
| `dom.ts` | Helpers para manipulación del DOM |
| `events.ts` | Sistema de eventos personalizado |
| `modals.ts` | Helpers para SweetAlert2 |
| `swal.ts` | Configuración base de SweetAlert2 |
| `validation.ts` | Validaciones de formularios |
| `multiselect.ts` | Componente multiselect personalizado |
| `render.ts` | Helpers de renderizado de listas y tablas |
| `helpers.ts` | Funciones de utilidad general |
| `styles.ts` | Helpers de clases CSS dinámicas |
| `hamburger.ts` | Control del menú hamburguesa |
| `env.ts` | Acceso a variables de entorno en el cliente |
| `organizationContext.ts` | Leer y actualizar el contexto de organización activo |
| `permissions.ts` | Verificación de permisos del usuario actual |
| `personalMode.ts` | Lógica del modo de proyecto personal |
| `brandingLoader.ts` | Carga de configuración de branding de la organización |
| **`pdf.ts`** | **Generación de PDF** (ver sección dedicada) |

---

### Stores

| Archivo | Descripción |
|---|---|
| `organizationStore.ts` | Store global con Nanostores que mantiene la organización activa del usuario. Persiste en `localStorage`. |

---

### Componentes

Los componentes en `src/components/` son fragmentos de UI reutilizables:

| Componente | Descripción |
|---|---|
| `Header.astro` | Barra de navegación superior con selector de organización |
| `OrganizationSelector.astro` | Dropdown para cambiar la organización activa |
| `ProtectedRoute.astro` | Wrapper que redirige al login si no hay token |
| `SuperWizard.astro` | Wizard multi-paso para la creación de proyectos |
| `ProjectSidebar.astro` | Barra lateral de la vista del proyecto |
| `ProjectSettingsDrawer.astro` | Panel deslizante de configuración del proyecto |
| `ConfigDrawer.astro` | Drawer de configuración general |
| `TurnosModal.astro` | Modal de gestión de turnos de empleados |
| `InvitacionesModal.astro` | Modal para invitar colaboradores |
| `Notificaciones.astro` | Panel de notificaciones |
| `PDFTemplate.astro` | Template HTML usado como base para PDFs (legacy) |
| `BurnBar.astro` | Barra visual de consumo de presupuesto (burn rate) |
| `ProfitabilityMeter.astro` | Indicador visual de rentabilidad del proyecto |
| `TimeInput.astro` | Input especializado para entrada de tiempo (HH:MM) |

---

## Tipos de Proyectos

El sistema soporta tres tipos de proyectos, controlados por el campo `tipo_proyecto` en la tabla `proyectos`:

### `personal`
- Un solo usuario registra sus propias horas.
- Los días (`Dia`) pertenecen al usuario propietario.
- Las horas se almacenan directamente en `Dia.horas_trabajadas`.

### `colaborativo`
- Múltiples usuarios trabajan en el mismo proyecto.
- Los días son **compartidos** (un único conjunto de `Dia` por mes).
- Las horas de **cada colaborador** se almacenan en `DiaColaborador` (tabla separada).
- El propietario (`rol='owner'`) creó el proyecto; los colaboradores (`rol='colaborador'`) fueron invitados.
- Cada colaborador puede tener su propia configuración de `horas_reales_activas`.
- Ver [Sistema de Colaboradores](#sistema-de-colaboradores) para más detalle.

### `empleados`
- El propietario gestiona un equipo de empleados (no usuarios del sistema, sino registros de `Empleado`).
- Incluye módulo de asistencia: marcado de entrada/salida, deudas de horas, justificaciones.
- Los empleados pueden o no tener un `usuario_id` asociado (cuenta en el sistema).

---

## Sistema de Colaboradores

### Flujo de incorporación

```
1. Usuario A crea un proyecto como 'colaborativo'
   └── Backend: ColaboradoresService.convertir_a_colaborativo()
       └── Registra al creador en proyecto_colaboradores (rol='owner')

2. Usuario A invita a Usuario B
   └── POST /api/proyectos/<id>/colaboradores/invitar
   └── Se crea InvitacionProyecto y se notifica a B

3. Usuario B acepta la invitación
   └── POST /api/invitaciones/<id>/aceptar
   └── Se crea ProyectoColaborador (rol='colaborador', estado='aceptado')

4. Usuario B accede al proyecto
   └── GET /api/proyectos/<id> con header X-Organization-ID
   └── Backend retorna proyecto + días con horas_colaborador del usuario B
```

### Aislamiento de horas

El principio fundamental es: **los días son compartidos, las horas son individuales**.

- `Dia` representa un día del mes en el proyecto. Es el mismo objeto para todos.
- Cuando el colaborador B registra horas un día:
  - `PUT /api/dias/<dia_id>/horas` con sus horas
  - Backend guarda/actualiza `DiaColaborador(dia_id, usuario_id=B, horas_trabajadas=X)`
  - La respuesta retorna las horas de B (no las del owner A)
- Cuando el collaborator B lee sus días:
  - El backend hace JOIN de `Dia` con `DiaColaborador` filtrando por `usuario_id=B`
  - El campo `horas_trabajadas` en la respuesta refleja las horas de B

### Estadísticas por colaborador

`GET /api/proyectos/<id>/colaboradores/estadisticas` retorna:

```json
{
  "colaboradores": [
    {
      "usuario_id": 1,
      "nombre": "Ezequiel",
      "rol": "owner",
      "total_horas": 42.5,
      "dias_trabajados": 12
    }
  ],
  "total_horas_proyecto": 85.0
}
```

---

## Motor Financiero

El motor financiero (Fase 3) permite controlar la rentabilidad de los proyectos:

### Tipos de facturación (`billing_type`)

| Tipo | Descripción |
|---|---|
| `fixed_price` | Precio fijo acordado al inicio del proyecto |
| `hourly_retainer` | Tarifa por hora × horas trabajadas |
| `time_and_materials` | Tiempo + materiales (gastos variables) |
| `none` | Sin seguimiento financiero |

### Jerarquía de tarifas

Las tarifas (`Rate`) se pueden definir a tres niveles (de mayor a menor prioridad):
1. **Por usuario** en un proyecto específico
2. **Por proyecto**
3. **Por organización** (tarifa base)

El endpoint `GET /api/rates/effective` resuelve la tarifa aplicable en cada contexto.

### Presupuesto

- `Budget`: presupuesto total del proyecto
- `ProjectBudgetAddon`: ajustes incrementales al presupuesto
- Alertas automáticas cuando se supera un umbral de consumo
- Snapshots históricos del estado del presupuesto

### Análisis de rentabilidad

`GET /api/profitability/dashboard` proporciona:
- Rentabilidad por proyecto
- Proyectos en riesgo financiero
- Costo real de empleados
- Comparación gasto real vs presupuesto

---

## Sistema de Asistencia

Para proyectos de tipo `empleados`, el sistema provee control de asistencia:

### Flujo de marcado

```
Empleado entra  → POST /api/marcar-entrada  → MarcadoAsistencia(tipo='entrada')
Empleado sale   → POST /api/marcar-salida   → MarcadoAsistencia(tipo='salida')
                                              → Calcula horas trabajadas automáticamente
```

### Detección automática de ausencias

APScheduler ejecuta `MarcadoAutomaticoService` de forma programada para:
- Detectar empleados que no marcaron entrada/salida
- Generar registros de ausencia
- Crear deudas de horas automáticamente

### Deudas de horas

Cuando un empleado trabaja menos horas de las requeridas:
1. Se genera un registro en `DeudaHoras`
2. El empleado puede presentar una `Justificacion`
3. El administrador aprueba o rechaza la justificación

### Configuración de asistencia

Cada proyecto tipo `empleados` tiene una `ConfiguracionAsistencia` que define:
- Horas requeridas por día
- Tolerancia de llegada tarde
- Si se permiten horas extras

---

## Generación de PDF

La generación de PDF se realiza **completamente en el cliente** usando `jsPDF`, sin dependencia del servidor.

### Archivo: `src/utils/pdf.ts`

#### Función principal

```typescript
generatePDFFromTemplate(data, tipo): void
```

Actúa como dispatcher según el `tipo_proyecto`:
- `'personal'` / `'empleados'` → `generateEmpleadoPDF()`
- `'colaborativo'` → `generateColaborativoPDF()`

#### PDF de proyecto colaborativo

`generateColaborativoPDF()` genera una página por colaborador:
- Primera página: encabezado del proyecto + datos del primer colaborador
- Páginas siguientes: cada colaborador en su propia página (`pdf.addPage()`)
- Tabla con columnas: Día, Horas, Tareas, Estado
- Paginación automática cuando la tabla supera el alto de la página

#### `drawTableWithPagination()`

Función compartida que renderiza tablas con:
- Encabezado de columnas con fondo oscuro
- Filas alternadas (zebra striping)
- Salto automático de página cuando no hay espacio
- Colores y tipografía consistentes

#### Consideraciones importantes

| Problema | Causa | Solución implementada |
|---|---|---|
| Emojis se renderizan como `Ø=Üd` | jsPDF no soporta Unicode fuera de Latin-1 | No usar emojis en el texto del PDF |
| Día incorrecto (off-by-one) | `new Date(fecha).getDate()` interpreta ISO 8601 UTC en zona horaria local (UTC-3 → día anterior) | Parsear directamente: `parseInt(fecha.split('-')[2], 10)` |
| Primera página vacía | `pdf.addPage()` llamado también para el primer colaborador | Guardia `if (i > 0)` antes de `addPage()` |

---

## Multi-tenant

El sistema está diseñado para soportar múltiples organizaciones (**multi-tenant**):

### Principios

- Cada usuario puede pertenecer a múltiples organizaciones
- Todos los datos (proyectos, tareas, días) están asociados a una organización
- La organización activa se selecciona en el frontend y se envía en cada request

### Flujo del contexto organizacional

```
1. Usuario inicia sesión → obtiene JWT
2. Frontend carga sus organizaciones → GET /api/organizations
3. Usuario selecciona organización → se guarda en organizationStore
4. Cada request incluye:
   Authorization: Bearer <jwt>
   X-Organization-ID: <org_id>
5. @organization_required en el backend:
   - Valida JWT → extrae user_id
   - Valida X-Organization-ID → extrae org_id
   - Verifica que user_id sea miembro activo de org_id
   - Inyecta context = { user_id, organization_id, role, membership }
```

### RBAC (Control de acceso basado en roles)

Los roles dentro de una organización determinan qué operaciones puede realizar cada miembro. Los permisos se verifican con `@requires_permission('nombre_permiso')` aplicado después de `@organization_required`.

---

## Migraciones de Base de Datos

Las migraciones se encuentran en `backend/migrations/` como scripts SQL. No hay un sistema de migración automático; se aplican manualmente conectándose a la base de datos:

```bash
# Conectarse al contenedor de la base de datos
make bash-db

# Dentro de MySQL, ejecutar la migración
source /migrations/nombre_migracion.sql;
```

| Archivo | Descripción |
|---|---|
| `add_multi_tenant_organizations.sql` | Estructura multi-tenant: organizaciones y membresías |
| `add_rbac_phase2.sql` | Sistema de roles y permisos |
| `add_financial_engine_phase3.sql` | Motor financiero: tarifas, presupuestos, gastos |
| `add_fase4_ux_financial_config.sql` | Configuración UX y financiera (Fase 4) |
| `add_proyecto_colaboradores.sql` | Tabla de colaboradores de proyectos |
| `add_dias_colaboradores.sql` | Tabla de horas por colaborador |
| `add_sistema_asistencia_empleados.sql` | Sistema de asistencia y deudas de horas |
| `add_sistema_turnos.sql` | Sistema de turnos de empleados |
| `add_horarios_empleados.sql` | Horarios de empleados |
| `add_usuario_colaborador_tareas.sql` | Asignación de tareas a colaboradores |
| `add_mes_anio_tareas.sql` | Campos mes/año en tareas |
| `complete_multi_tenant_migration.sql` | Migración completa a multi-tenant |
| `fix_cascade_delete.sql` | Corrección de eliminaciones en cascada |

---

## Notas de Desarrollo

### Acceso a los contenedores

```bash
# Logs en tiempo real
make logs-backend
make logs-frontend

# Shell interactiva
make bash-backend    # bash en el contenedor Flask
make bash-frontend   # sh en el contenedor Astro
make bash-db         # MySQL CLI
```

### Regenerar SECRET_KEY

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Reinicio limpio (⚠️ borra todos los datos)

```bash
make clean   # Elimina contenedores y volúmenes
make start   # Reconstruye desde cero
```

### Live Reload en desarrollo

En modo `development` (por defecto en `.env.example`), Docker monta los directorios del código como volúmenes. Los cambios en archivos del backend o frontend se reflejan automáticamente sin necesidad de reconstruir las imágenes.
