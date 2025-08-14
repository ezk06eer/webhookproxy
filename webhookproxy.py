#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import threading
import time
import select
from collections import deque

# Configuración
LISTEN_PORT = 8080  # Puerto para recibir webhooks
TARGET_HOST = "127.0.0.1"  # Host destino
TARGET_PORT = 8081  # Puerto destino
BUFFER_SIZE = 65536  # Tamaño de buffer (64KB)
MAX_CONNECTIONS = 100000  # Conexiones concurrentes máximas
QUEUE_MAX = 1000000  # Tamaño máximo de la cola

# Estadísticas
stats = {
    'total_requests': 0,
    'start_time': time.time(),
    'errors': 0,
    'queue_size': 0
}

# Cola compartida para procesamiento asíncrono
request_queue = deque(maxlen=QUEUE_MAX)

# Pool de sockets pre-conectados
socket_pool = []


def init_socket_pool():
    """Pre-conecta sockets para ahorrar tiempo"""
    print(f"[!] Inicializando pool de sockets a {TARGET_HOST}:{TARGET_PORT}...")
    for _ in range(100):  # 100 conexiones persistentes
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((TARGET_HOST, TARGET_PORT))
            socket_pool.append(s)
        except Exception as e:
            print(f"[X] Error conectando socket: {e}")
    print(f"[+] Pool listo con {len(socket_pool)} sockets")


def get_socket():
    """Obtiene un socket del pool o crea uno nuevo"""
    while socket_pool:
        s = socket_pool.pop()
        try:
            # Verificar si el socket sigue vivo
            s.send(b'')
            return s
        except:
            continue

    # Si no hay sockets disponibles, crear uno nuevo
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((TARGET_HOST, TARGET_PORT))
    return s


def release_socket(s):
    """Devuelve un socket al pool"""
    socket_pool.append(s)


def worker():
    """Procesa requests de la cola"""
    while True:
        if request_queue:
            client_socket, data = request_queue.popleft()
            stats['queue_size'] = len(request_queue)

            try:
                target_socket = get_socket()
                target_socket.sendall(data)

                # Leer respuesta (opcional, puede omitirse para más velocidad)
                response = target_socket.recv(BUFFER_SIZE)
                client_socket.sendall(response)

                release_socket(target_socket)
                client_socket.close()
            except Exception as e:
                stats['errors'] += 1
                print(f"[X] Error: {e}")
                try:
                    client_socket.close()
                except:
                    pass
        else:
            time.sleep(0.001)  # Pequeño sleep para evitar CPU al 100%


def handle_connection(client_socket):
    """Maneja una conexión entrante"""
    try:
        data = client_socket.recv(BUFFER_SIZE)
        if data:
            stats['total_requests'] += 1
            request_queue.append((client_socket, data))
            stats['queue_size'] = len(request_queue)
    except Exception as e:
        stats['errors'] += 1
        client_socket.close()


def stats_monitor():
    """Muestra estadísticas cada segundo"""
    while True:
        elapsed = time.time() - stats['start_time']
        rps = stats['total_requests'] / elapsed if elapsed > 0 else 0
        print(
            f"\r[STATS] Requests: {stats['total_requests']} | RPS: {rps:.2f} | Errors: {stats['errors']} | Queue: {stats['queue_size']}",
            end='')
        time.sleep(1)


def main():
    """Inicia el proxy"""
    print(f"[+] Iniciando proxy en puerto {LISTEN_PORT} -> {TARGET_HOST}:{TARGET_PORT}")

    # Inicializar pool de sockets
    init_socket_pool()

    # Iniciar workers
    for _ in range(100):  # 100 threads workers
        t = threading.Thread(target=worker, daemon=True)
        t.start()

    # Iniciar monitor de estadísticas
    stats_thread = threading.Thread(target=stats_monitor, daemon=True)
    stats_thread.start()

    # Configurar socket servidor
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind(('0.0.0.0', LISTEN_PORT))
    server_socket.listen(MAX_CONNECTIONS)

    print(f"[+] Escuchando en puerto {LISTEN_PORT}...")

    # Usar select para manejar múltiples conexiones
    inputs = [server_socket]

    while True:
        readable, _, _ = select.select(inputs, [], [], 1)
        for s in readable:
            if s is server_socket:
                client_socket, addr = s.accept()
                t = threading.Thread(target=handle_connection, args=(client_socket,), daemon=True)
                t.start()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Cerrando proxy...")
    except Exception as e:
        print(f"[X] Error fatal: {e}")
