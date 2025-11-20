# 🚀 Guía de Despliegue en Producción - TimeFlow

## 📋 Requisitos Previos

- VPS con Ubuntu 20.04+ o similar
- Docker y Docker Compose instalados
- Dominio (opcional, puede usar IP pública)
- SSL/HTTPS recomendado (Let's Encrypt con Nginx)

## 🔧 Pasos para Desplegar

### 1. Clonar el repositorio en el VPS

```bash
git clone <tu-repositorio>
cd MisHoras
```

### 2. Configurar Variables de Entorno

Editar el archivo `.env` con los valores de producción:

```bash
nano .env
```

**Variables CRÍTICAS a cambiar:**

```bash
# IMPORTANTE: Cambiar a production
NODE_ENV=production
FLASK_ENV=production
FLASK_DEBUG=False

# Base de Datos - CAMBIAR CONTRASEÑAS
DB_USER=timeflow_user
DB_PASSWORD=TU_PASSWORD_MYSQL_SUPER_SEGURA_AQUI
DB_NAME=timeflow_db
DB_ROOT_PASSWORD=TU_ROOT_PASSWORD_SUPER_SEGURA_AQUI

# Seguridad - GENERAR NUEVA CLAVE
# Generar con: openssl rand -hex 32
SECRET_KEY=tu_clave_jwt_super_segura_generada_con_openssl

# CORS - Cambiar por tu dominio o IP
CORS_ORIGINS=https://tudominio.com

# Frontend - URL del backend para el cliente
# Si tienes dominio: https://api.tudominio.com
# Si solo IP: http://TU_IP_VPS:21050
VITE_API_URL=http://TU_IP_VPS:21050

# Backend interno (mantener si usas Docker Compose)
VITE_API_URL_SERVER=http://backend:5000
```

### 3. Nota sobre docker-compose.yml

**NO es necesario modificar docker-compose.yml** - Los contenedores se ejecutan en modo desarrollo con hot reload, lo que te permite hacer cambios en tiempo real incluso en producción.

- ✅ Backend: Flask con auto-reload detecta cambios en Python
- ✅ Frontend: Astro dev server con hot module replacement
- ✅ Volúmenes montados para cambios en vivo

**Ventaja**: Puedes implementar cambios rápidos en producción sin reconstruir contenedores.

### 4. Construir y Levantar Contenedores

```bash
# Reconstruir imágenes con nuevo código
docker compose build --no-cache

# Levantar servicios
docker compose up -d

# Ver logs
docker compose logs -f
```

### 5. (Opcional) Configurar Nginx Reverse Proxy

Si quieres usar puerto 80/443 con SSL:

```nginx
# /etc/nginx/sites-available/timeflow
server {
    listen 80;
    server_name tudominio.com;

    # Frontend
    location / {
        proxy_pass http://localhost:21000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:21050;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Habilitar y reiniciar Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/timeflow /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 6. Configurar SSL con Let's Encrypt (Recomendado)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d tudominio.com
```

### 7. Configurar Firewall

```bash
# Permitir puertos necesarios
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable
```

## 🔐 Seguridad Post-Despliegue

1. **Cambiar puertos expuestos** (opcional):
   - Puedes cambiar `BACKEND_PUBLIC_PORT` y `FRONTEND_PUBLIC_PORT` a valores menos predecibles
   - O usar solo Nginx y no exponer los puertos de Docker directamente

2. **Backups de Base de Datos**:
   ```bash
   # Crear backup
   docker compose exec db mysqldump -u root -p timeflow_db > backup_$(date +%Y%m%d).sql
   
   # Restaurar backup
   docker compose exec -T db mysql -u root -p timeflow_db < backup.sql
   ```

3. **Monitoreo de Logs**:
   ```bash
   docker compose logs backend --tail=100 -f
   docker compose logs frontend --tail=100 -f
   ```

4. **Actualizaciones** (con hot reload, solo reinicia si cambias dependencias):
   ```bash
   git pull
   # Los cambios se aplican automáticamente gracias al hot reload
   
   # Solo si actualizaste dependencias (package.json o requirements.txt):
   docker compose down
   docker compose build --no-cache
   docker compose up -d
   ```

## 📊 Verificación

1. Verificar que todos los contenedores estén corriendo:
   ```bash
   docker compose ps
   ```

2. Verificar conectividad:
   ```bash
   curl http://TU_IP_VPS:21050/api/auth/login
   ```

3. Acceder desde navegador:
   ```
   http://TU_IP_VPS:21000
   ```

## 🐛 Troubleshooting

### Contenedores no inician
```bash
docker compose logs
docker compose down -v  # CUIDADO: elimina volúmenes
docker compose up -d
```

### Error de conexión a base de datos
```bash
# Verificar que MySQL está corriendo
docker compose exec db mysql -u root -p

# Verificar variables de entorno
docker compose exec backend env | grep DB_
```

### Error CORS
- Verificar que `CORS_ORIGINS` en `.env` incluye la URL del frontend
- Reiniciar backend después de cambiar CORS

## 📝 Notas Importantes

- **Backups regulares**: Programa backups automáticos de la base de datos
- **Monitoreo**: Considera usar herramientas como Portainer para gestionar Docker
- **Logs**: Los logs se guardan en Docker, usa `docker compose logs` para verlos
- **Recursos**: Ajusta `--workers` de Gunicorn según los recursos de tu VPS
- **HTTPS**: Altamente recomendado para producción, especialmente si maneja datos sensibles

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs: `docker compose logs`
2. Verifica las variables de entorno: `cat .env`
3. Confirma que los puertos estén abiertos: `netstat -tulpn | grep LISTEN`
