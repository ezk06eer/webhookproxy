# Webhook Proxy Ultra-Rápido

![Python](https://img.shields.io/badge/python-3.6%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Performance](https://img.shields.io/badge/performance-100K%2Fsec-orange)

Un proxy de webhooks extremadamente rápido y ligero diseñado para manejar cargas masivas de hasta 100,000 mensajes por segundo.

## 🔥 Características Principales

- **Rendimiento extremo**: Diseñado para manejar 100K+ mensajes/segundo
- **Arquitectura multi-hilo**: Utiliza pools de conexiones y workers paralelos
- **Mínima sobrecarga**: Forwarding directo con procesamiento mínimo
- **Estadísticas en tiempo real**: Monitorización de throughput y errores
- **Configuración simple**: Solo especifica puertos y endpoints

## 🚀 Instalación Rápida

1. Clona el repositorio:
```bash
git clone https://github.com/ezk06eer/webhookproxy.git
cd webhookproxy
```

2. Ejecuta el proxy (requiere Python 3.6+):
```bash
python webhookproxy.py
```

## ⚙️ Configuración

Edita directamente las variables al inicio del archivo `webhookproxy.py`:

```python
# Configuración hardcodeada (EDITAR ESTO)
LISTEN_PORT = 8081          # Puerto para recibir webhooks
TARGET_HOST = "127.0.0.1"   # Host destino
TARGET_PORT = 8082          # Puerto destino
BUFFER_SIZE = 65536         # Tamaño de buffer (64KB)
MAX_CONNECTIONS = 100000    # Conexiones concurrentes máximas
```

## 📊 Métricas de Rendimiento

El proxy muestra estadísticas en tiempo real:
```
[STATS] Requests: 1245678 | RPS: 98234.21 | Errors: 12 | Queue: 234
```

## 🛠️ Tecnologías Clave

- **Socket raw**: Para mínimo overhead de red
- **Connection pooling**: Reutilización de conexiones TCP
- **Deque de alta velocidad**: Cola optimizada para mensajes
- **Select I/O multiplexing**: Manejo eficiente de conexiones

## 📌 Casos de Uso

✔️ Forwarding masivo de webhooks  
✔️ Balanceo de carga simple  
✔️ Pruebas de stress de sistemas  
✔️ Buffer para picos de tráfico  

## ⚠️ Limitaciones

- No soporta HTTPS (usa un reverse proxy como Nginx para eso)
- Sin autenticación integrada
- Manejo básico de errores
- Requiere ajuste para cargas específicas

## 📈 Optimizaciones Avanzadas

Para obtener el máximo rendimiento:

1. Usa Python 3.10+ (mejor optimizado)
2. Ejecuta en Linux con `taskset` para affinity de CPU
3. Ajusta `BUFFER_SIZE` según tu tamaño promedio de mensajes



## 📄 Licencia

MIT License - Usa bajo tu propio riesgo para cargas de producción.

---

**Nota**: Este proxy está optimizado para velocidad sobre características completas. Para entornos críticos, considera soluciones empresariales como NGINX o Envoy.
