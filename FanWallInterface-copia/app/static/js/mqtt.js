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
    document.getElementById('status').innerText = payload;

    if (topic === 'fanWall/wall/id' && payload !== 'get') {
        console.log("¡ID detectado desde MQTT! Dibujando slider para:", payload);
        if (typeof addSlider === "function") {
            addSlider(payload);
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

