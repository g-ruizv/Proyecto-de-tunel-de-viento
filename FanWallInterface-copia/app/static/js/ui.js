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
    // Add more message types as needed
};

function createMessage(type, data) {
    return {
        type: type,
        data: data
    };
}

var grid = GridStack.init(options);
var smallGrid = GridStack.init(smallGridOptions, '.grid-stack-sm');
var controllerIds = [];
getConfigurations();
//getPresets();
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
    //setSpeed(value,id);
    setControllerSpeed(value,id);
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
            id: widget.id+"-small",
        });
    });
}

function updateSliders(){
    controllerIds.forEach(function(id){
        addSlider(id);
    });
    updateControllerAvailability("id1", true);
}

function addSlider(id) {
    // Evitar duplicados
    if (document.querySelector(`[gs-id="${id}"]`)) {
        console.log("Slider ya existe:", id);
        return;
    }

    // Añadir ID a la lista antes de crear el widget (para que el siguiente calcule bien)
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
    grid.removeWidget(document.getElementById(id).closest('.grid-stack-item'));
    controllerIds = controllerIds.filter(function(value, index, arr) {
        return value !== id;
    });
    loadPresetButton.classList.add('disabled');
    loadPresetButton.setAttribute('aria-disabled', 'true');
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

// Function to update the color of a small grid widget
function updateSmallGridItemColor(widgetId, value, colorA, colorB) {
    var itemElement = document.getElementById(widgetId);
    if (itemElement) {
        var gradientColor = calculateGradientColor(value, colorA, colorB);
        itemElement.style.backgroundColor = gradientColor;
    }
}

function addFanToGrid(id) {
    // Evitar duplicados si el slider ya existe
    if (document.getElementById(`slider-${id}`)) return;

    // El HTML que define el controlador (slider)
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

    // Añadir el widget a la cuadrícula Gridstack
    grid.addWidget({w: 3, h: 2, content: itemHtml, id: id});
    
    // Registrar el ID en tu lista global si no existe
    if (!controllerIds.includes(id)) {
        controllerIds.push(id);
    }
}

// ✅ NUEVA FUNCIÓN: Actualizar el display del slider en tiempo real
function updateSliderDisplay(value, id) {
    var label = document.getElementById(`val-${id}`);
    if (label) {
        label.innerText = value;
    }
}

function addSlider(id) {
    // Verificamos si ya existe en el grid para no duplicarlo
    if (document.getElementById(id)) return;

    getController(id).then(function(controller) {
        // SOLUCIÓN: Si controller es null/undefined, usamos el id como nombre por defecto
        var controllerName = (controller && controller.name) ? controller.name : id;
        
        var itemHtml = `
            <div class="unavailable grid-stack-item-content">
                <button class="delete-button" onclick="deleteWidget('${id}')">&times;</button>
                <br><br>
                <label class="slider-label" for="${id}">${controllerName}</label>
                <input type="range" min="0" max="100" value="50" class="slider" id="${id}">
            </div>`;
            
        // Insertamos en el grid
        grid.addWidget({w: 2, h: 2, id: id, noResize: true, content: itemHtml});
    }).catch(function(error) {
        console.error("Error al cargar controlador. Creando slider por defecto:", error);
    });
}

// Función para eliminar si haces clic en la X
function deleteWidget(id) {
    var el = document.querySelector(`[gs-id="${id}"]`);
    if (el) grid.removeWidget(el);
}
