#!/usr/bin/env python3
"""Test WebSocket connection to the Flask-SocketIO server."""

import socketio

# Create a SocketIO client
sio = socketio.Client()

@sio.event
def connect():
    print("Connected to server!")
    print("Testing Chaturbate namespace...")
    sio.emit('start_chaturbate', namespace='/chaturbate')

@sio.event
def disconnect():
    print("Disconnected from server!")

@sio.on('connection_status', namespace='/chaturbate')
def on_connection_status(data):
    print(f"Connection status: {data}")

@sio.on('chaturbate_status', namespace='/chaturbate')
def on_chaturbate_status(data):
    print(f"Chaturbate status: {data}")

@sio.on('chaturbate_event', namespace='/chaturbate')
def on_chaturbate_event(data):
    print(f"Chaturbate event: {data}")

@sio.on('chaturbate_error', namespace='/chaturbate')
def on_chaturbate_error(data):
    print(f"Chaturbate error: {data}")

if __name__ == '__main__':
    try:
        print("Connecting to WebSocket server...")
        sio.connect('http://localhost:5000', namespaces=['/chaturbate'])
        
        # Keep the connection alive for 10 seconds to receive events
        import time
        time.sleep(10)
        
        print("Stopping Chaturbate client...")
        sio.emit('stop_chaturbate', namespace='/chaturbate')
        time.sleep(2)
        
        sio.disconnect()
    except Exception as e:
        print(f"Error: {e}")