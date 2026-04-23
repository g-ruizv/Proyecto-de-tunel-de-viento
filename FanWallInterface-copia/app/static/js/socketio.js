socket = io.connect('https://' + document.domain + ':' + location.port);
socket.on('connect', function() {
    console.log('Connected to server');
    socket.emit('my event', {data: 'I\'m connected!'});
});
socket.on('message', function(message) {
    // Handle incoming messages
    console.log('Received message:', message);
});

socket.on('fanId', function(data) {
    var id = data.id;
    console.log('Received ID:', id);

    // Handle ID received, similar to MQTT logic
    if (!controllerIds.includes(id)) {
        controllerIds.push(id);
        console.log(controllerIds);
        addSlider(id);
        updateControllerAvailability(id, true);
        addController(id, id);
    }
    else {
        console.log('ID already exists');
        updateControllerAvailability(id, true);
    }
});

socket.on('fanSpeed', function(data) {
    var id = data.id;
    var speed = data.speed;
    console.log('Received speed:', speed, 'for ID:', id);
    var colorA = '#ff0000'; // Red
    var colorB = '#00ff00'; // Green
    //updateSmallGridItemColor(id+"-small", speed, colorA, colorB);
    smallGrid.engine.nodes.forEach(function(item) {
        if (item.id === id+"-small") {
            console.log('Updating speed for ID:', id);
            var gradientColor = calculateGradientColor(speed, colorA, colorB);
            console.log(item);
            item.el.style.backgroundColor = gradientColor;
        }
    });
});

socket.emit('controllerReset', "reset");