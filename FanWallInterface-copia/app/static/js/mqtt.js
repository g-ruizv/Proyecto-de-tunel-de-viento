var clientId = 'web-client-' + Math.random().toString(16).substr(2, 8);

// Opción A: HiveMQ (WS en puerto 8000) — útil para pruebas rápidas
const mqttClient = new Paho.MQTT.Client('broker.emqx.io', 8084, clientId);

mqttClient.onConnectionLost = function (responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log('Connection lost: ' + responseObject.errorMessage);
    }
};

mqttClient.onMessageArrived = function (message) {
    var topic = message.destinationName;
    var payload = message.payloadString;
    
    // Actualizar el texto del status en la pantalla
    document.getElementById('status').innerText = payload;

    // EL ESLABÓN PERDIDO: Si el mensaje viene del tópico de IDs y es una MAC (no es "get")
    if (topic === 'fanWall/wall/id' && payload !== 'get') {
        console.log("¡ID detectado directamente desde la placa! Dibujando slider para:", payload);
        
        // Llamamos a la función que dibuja el slider (que arreglamos antes en ui.js)
        if (typeof addSlider === "function") {
            addSlider(payload);
        } else {
            console.error("No se encuentra la función addSlider.");
        }
    }
};

var options = {
    useSSL: true,
    timeout: 3,
    onSuccess: onConnect,
    onFailure: onConnectionLost,
}

mqttClient.connect(options);

function onConnect() {
    console.log('Connected to HiveMQ broker');
    mqttClient.subscribe('fanWall/wall/control');
    mqttClient.subscribe('fanWall/wall/status');
    mqttClient.subscribe('fanWall/wall/id');
}

function onConnectionLost(responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log('Connection lost: ' + responseObject.errorMessage);
    }
}

