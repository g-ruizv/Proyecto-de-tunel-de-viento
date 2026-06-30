socket = io({
  transports: ['websocket','polling'],
  reconnection: true,
  reconnectionAttempts: Infinity,
  reconnectionDelay: 1000
});

socket.on('connect', function() {
    console.log('Connected to server');
    socket.emit('my event', {data: 'I\'m connected!'});
});

socket.on('message', function(message) {
    console.log('Received message:', message);
});

socket.on('fanId', function(data) {
    var id = data.id;
    console.log('Received ID from server:', id);

    // 🛑 Filtrar IDs vacíos o solo espacios
    if (!id || id.trim() === '') {
        console.warn('ID vacío recibido, ignorando.');
        return;
    }

    if (!controllerIds.includes(id)) {
        controllerIds.push(id);
        addSlider(id);
        updateControllerAvailability(id, true);
        addController(id, id);
    } else {
        console.log('ID already exists, updating availability');
        updateControllerAvailability(id, true);
    }
});

socket.on('fanSpeed', function(data) {
    var id = data.id;
    var speed = data.speed;
    console.log('Received speed:', speed, 'for ID:', id);
    var colorA = '#ff0000';
    var colorB = '#00ff00';
    smallGrid.engine.nodes.forEach(function(item) {
        if (item.id === id + "-small") {
            console.log('Updating speed for ID:', id);
            var gradientColor = calculateGradientColor(speed, colorA, colorB);
            console.log(item);
            item.el.style.backgroundColor = gradientColor;
        }
    });
});

socket.emit('controllerReset', "reset");