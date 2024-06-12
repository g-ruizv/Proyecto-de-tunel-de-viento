var mqttClient = new Paho.MQTT.Client('broker.hivemq.com', 8000, '5a0d6a66b35b476a8653e7edb84528df');

mqttClient.onConnectionLost = function (responseObject) {
    if (responseObject.errorCode !== 0) {
        console.log('Connection lost: ' + responseObject.errorMessage);
    }
};

mqttClient.onMessageArrived = function (message) {
    // Update status on message arrival
    document.getElementById('status').innerText = message.payloadString;
};

mqttClient.connect({
    onSuccess: function () {
        console.log('Connected to HiveMQ broker');
        mqttClient.subscribe('fanWall/wall/control');
        mqttClient.subscribe('fanWall/wall/status');
        mqttClient.subscribe('fanWall/wall/id');
    },
    onFailure: function (message) {
        console.log('Connection failed: ' + message.errorMessage);
    },
});

