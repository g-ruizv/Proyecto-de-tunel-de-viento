var options = {
    cellHeight: '70px',
    cellWidth: '70px',
    column: 12,
    verticalMargin: 10,
    minHeight: 0,
    float: true,
};

var smallGridOptions = {
    staticGrid: true,
    cellHeight: '50px',
    float: true,
    column: 12,
};

const MessageType = {
    STATUS_UPDATE: 'status_update',
    COMMAND: 'command',
    ACTIVATE: 'activate',
    CONFIG_UPDATE: 'config_update',
    CONTROLLER_INFORMATION: 'controller_information',
};

function createMessage(type, data) {
    return { type: type, data: data };
}

var grid = GridStack.init(options);
var smallGrid = GridStack.init(smallGridOptions, '.grid-stack-sm');
var controllerIds = [];
getConfigurations();
getSameSizePresets();
updateSliders();
var loadPresetButton = document.getElementById('loadPresetButton');
loadPresetButton.classList.add('disabled');
loadPresetButton.setAttribute('aria-disabled', 'true');

grid.on('dragstop', function(event, element) {
    loadPresetButton.classList.add('disabled');
    loadPresetButton.setAttribute('aria-disabled', 'true');
});

function getValue(id) {
    console.log(id);
    var slider = document.getElementById(id);
    var value = slider.value;
    console.log('Slider value: ' + value);
    setControllerSpeed(value, id);
}

function copyGridData() {
    var mainGridData = grid.save(false);
    smallGrid.removeAll();
    mainGridData.forEach(function(widget) {
        smallGrid.addWidget({
            x: Math.floor(widget.x / 2),
            y: Math.floor(widget.y / 2),
            w: 1,
            h: 1,
            id: widget.id + "-small",
        });
    });
}

function updateSliders() {
    // Filtrar IDs vacíos
    var validIds = controllerIds.filter(function(id) {
        return id && id.trim() !== '';
    });
    validIds.forEach(function(id) {
        addSlider(id);
    });
    if (validIds.length > 0) {
        updateControllerAvailability(validIds[0], true);
    }
}

function addSlider(id) {
    // No crear si el ID es vacío
    if (!id || id.trim() === '') {
        console.warn('Intento de crear slider con ID vacío. Ignorado.');
        return;
    }

    if (document.querySelector(`[gs-id="${id}"]`)) {
        console.log("Slider ya existe:", id);
        return;
    }

    if (!controllerIds.includes(id)) {
        controllerIds.push(id);
    }

    var index = controllerIds.indexOf(id);
    var colsPorFila = 6;
    var x = (index % colsPorFila) * 2;
    var y = Math.floor(index / colsPorFila) * 2;

    var controllerName = id;
    var itemHtml = `
        <div class="unavailable grid-stack-item-content">
            <button class="delete-button" onclick="deleteWidget('${id}')">&times;</button>
            <br><br>
            <label class="slider-label" for="${id}">${controllerName}</label>
            <input type="range" min="0" max="100" value="50" class="slider" id="${id}">
        </div>`;

    grid.addWidget(itemHtml, { w: 2, h: 2, x: x, y: y, id: id, noResize: true });

    if (typeof addController === 'function') {
        addController(id, controllerName);
    }
}

function deleteWidget(id) {
    console.log('Deleting widget:', id);
    // Buscar el nodo del widget en el grid
    var node = grid.engine.nodes.find(function(n) { return n.id === id; });
    if (node) {
        grid.removeWidget(node.el);
        // Actualizar lista de IDs
        controllerIds = controllerIds.filter(function(value) {
            return value !== id;
        });
        loadPresetButton.classList.add('disabled');
        loadPresetButton.setAttribute('aria-disabled', 'true');
    } else {
        console.warn('Widget not found:', id);
    }
}

function updateControllerAvailability(sliderId, isAvailable) {
    var sliderElement = document.getElementById(sliderId);
    if (sliderElement) {
        var itemElement = sliderElement.closest('.grid-stack-item');
        if (itemElement) {
            if (isAvailable) {
                itemElement.classList.add('available');
                itemElement.classList.remove('unavailable');
            } else {
                itemElement.classList.add('unavailable');
                itemElement.classList.remove('available');
            }
        }
    }
}

$(document).on('mouseup', '.slider', function() {
    var id = $(this).attr('id');
    getValue(id);
});

$('#loadPresetModal').on('show.bs.modal', function () {
    copyGridData();
});

$('#editControllerModal').on('show.bs.modal', getControllers);

$(document).on('click', '#configDropdown .dropdown-item', function() {
    var id = $(this).attr('id');
    console.log('Configuration selected:', id);
    loadPresetButton.classList.remove('disabled');
    loadPresetButton.setAttribute('aria-disabled', 'false');
    importConfiguration(id);
});

$(document).on('click', '#presetDropdown .dropdown-item', function() {
    var id = $(this).attr('id');
    console.log('Configuration selected:', id);
    importPreset(id);
});

function calculateGradientColor(value, colorA, colorB) {
    var rA = parseInt(colorA.slice(1, 3), 16);
    var gA = parseInt(colorA.slice(3, 5), 16);
    var bA = parseInt(colorA.slice(5, 7), 16);

    var rB = parseInt(colorB.slice(1, 3), 16);
    var gB = parseInt(colorB.slice(3, 5), 16);
    var bB = parseInt(colorB.slice(5, 7), 16);

    var r = Math.round(rA + (rB - rA) * (value / 100));
    var g = Math.round(gA + (gB - gA) * (value / 100));
    var b = Math.round(bA + (bB - bA) * (value / 100));

    return `rgb(${r}, ${g}, ${b})`;
}

function updateSmallGridItemColor(widgetId, value, colorA, colorB) {
    var itemElement = document.getElementById(widgetId);
    if (itemElement) {
        var gradientColor = calculateGradientColor(value, colorA, colorB);
        itemElement.style.backgroundColor = gradientColor;
    }
}

function addFanToGrid(id) {
    if (document.getElementById(`slider-${id}`)) return;

    var itemHtml = `
    <div class="grid-stack-item-content card bg-dark text-white shadow-sm">
        <div class="card-body text-center p-2">
            <button class="delete-button btn btn-sm btn-danger" style="position:absolute; top:5px; right:5px;" onclick="deleteWidget('${id}')">&times;</button>
            <strong style="font-size: 0.8rem;">ID: ${id}</strong>
            <br>
            <input type="range" min="0" max="255" value="0" class="form-range slider" id="slider-${id}" 
                   oninput="updateSliderDisplay(this.value, '${id}'); setControllerSpeed(this.value, '${id}')">
            <div class="mt-2">
                <small style="color: #aaa;">Potencia: <strong id="val-${id}">0</strong>/255</small>
            </div>
        </div>
    </div>`;

    grid.addWidget({w: 3, h: 2, content: itemHtml, id: id});
    
    if (!controllerIds.includes(id)) {
        controllerIds.push(id);
    }
}

function updateSliderDisplay(value, id) {
    var label = document.getElementById(`val-${id}`);
    if (label) {
        label.innerText = value;
    }
}

// ==========================================
// MOSTRAR DISTRIBUCIÓN DE LA CONFIGURACIÓN
// ==========================================

function showDistribution() {
    const container = document.getElementById('distributionContent');
    if (!container) return;

    const configId = window.currentConfiguration ? window.currentConfiguration.id : null;
    const configName = window.currentConfiguration ? window.currentConfiguration.name : 'Sin nombre';

    if (!configId) {
        container.innerHTML = `<div class="alert alert-warning">No hay configuración cargada.</div>`;
        return;
    }

    fetch(`/api/v1/fanWall/configurations/${configId}/controllers`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }

            const controllers = data.controllers;
            const controllerKeys = Object.keys(controllers);
            if (controllerKeys.length === 0) {
                container.innerHTML = `<div class="alert alert-info">Esta configuración no tiene controladores.</div>`;
                return;
            }

            // TABLA
            let html = `<h5>Configuración: ${configName} (ID: ${configId})</h5>`;
            html += `<div class="table-responsive"><table class="table table-striped table-bordered">
                        <thead><tr><th>Controlador</th><th>Coordenada X</th><th>Coordenada Y</th></tr></thead><tbody>`;
            controllerKeys.forEach(key => {
                const c = controllers[key];
                html += `<tr><td>${c.name || key}</td><td>${c.x}</td><td>${c.y}</td></tr>`;
            });
            html += `</tbody></table></div>`;

            // GRID VISUAL
            let maxX = 0, maxY = 0;
            controllerKeys.forEach(key => {
                const c = controllers[key];
                if (c.x > maxX) maxX = c.x;
                if (c.y > maxY) maxY = c.y;
            });
            const matrix = [];
            for (let y = 0; y <= maxY; y++) {
                matrix[y] = [];
                for (let x = 0; x <= maxX; x++) {
                    matrix[y][x] = null;
                }
            }
            controllerKeys.forEach(key => {
                const c = controllers[key];
                matrix[c.y][c.x] = c.name || key;
            });

            html += `<h6>Vista en cuadrícula:</h6><div style="display:inline-block; border:1px solid #ccc; padding:5px;">`;
            for (let y = 0; y < matrix.length; y++) {
                html += `<div style="display:flex;">`;
                for (let x = 0; x < matrix[y].length; x++) {
                    const cell = matrix[y][x];
                    const color = cell ? '#28a745' : '#f8f9fa';
                    const text = cell || '';
                    html += `<div style="width:60px; height:60px; border:1px solid #ddd; background:${color}; 
                                display:flex; align-items:center; justify-content:center; font-size:10px; 
                                color:${cell ? 'white' : '#aaa'}; margin:1px;">
                                ${text}
                            </div>`;
                }
                html += `</div>`;
            }
            html += `</div>`;

            // JSON
            html += `<hr><h6>JSON de la configuración:</h6>`;
            html += `<pre style="background:#f5f5f5; padding:10px; border-radius:5px; max-height:200px; overflow:auto;">${JSON.stringify(data, null, 2)}</pre>`;

            container.innerHTML = html;
        })
        .catch(error => {
            container.innerHTML = `<div class="alert alert-danger">Error al cargar la distribución: ${error.message}</div>`;
        });
}