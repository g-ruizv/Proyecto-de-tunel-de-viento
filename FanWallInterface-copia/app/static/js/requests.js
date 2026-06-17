function addController(id, controllerName) {
    const postData = {
        name: controllerName
    };

    fetch(`/api/v1/fanWall/controllers/${id}`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function updateController() {
    const controllerSelect = document.getElementById('controllerSelect');
    const controllerValue = document.getElementById('controllerValue').value;
    const selectedControllerId = controllerSelect.value;

    fetch(`/api/v1/fanWall/controllers/${selectedControllerId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: controllerValue }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Success:', data);
        $('#controllerModal').modal('hide');
        document.getElementById('updateForm').reset();
    })
    .catch(error => {
        console.error('There was a problem with the PUT operation:', error);
    });
}
function getControllers() {
    fetch('/api/v1/fanWall/controllers')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error){
                showAlert(data.error, "warning");
                return;
            }
            const controllerSelect = document.getElementById('controllerSelect');
            controllerSelect.innerHTML = ''; // Clear previous options
            data.controllers.forEach(controller => {
                const option = document.createElement('option');
                option.value = controller.id;
                option.textContent = controller.name;
                controllerSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

async function getController(id) {
    let controllerData;
    try {
        const response = await fetch(`/api/v1/fanWall/controllers/${id}`);
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        const data = await response.json();
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        console.log('Controller:', data);
        controllerData = data;
        console.log(controllerData);
    } catch (error) {
        console.error('There was a problem with the fetch operation:', error);
    }
    console.log(controllerData);
    return controllerData;
}


function addMultipleControllers() {
    controllerList = getControllerNamesAndIds();
    console.log(controllerList);
    const postData = { "controllers": [] }
    controllerList.forEach(element => {
        let newController = {"name": element.name, "id": element.id};
        postData.controllers.push(newController);
    });
    fetch(`/api/v1/fanWall/addMultipleControllers`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json(); // PRIMERO CONVIERTE A JSON
    })
    .then(data => {
        // AHORA SÍ PUEDES USAR 'data'
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log("Controladores añadidos:", data);
    })
    .catch(error => {
        console.error("Error en addMultipleControllers:", error);
    });
}

function getConfigurations() {
    fetch('/api/v1/fanWall/configurations')
        .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
        })
        .then(data => {
            if (data.error){
                showAlert(data.error, "warning");
                return;
            }
            const dropdown = document.getElementById('configDropdown');
            dropdown.innerHTML = ''; // Clear existing options
            console.log(data);
            data.configurations.forEach(configuration => {
                const option = document.createElement('a');
                option.classList.add('dropdown-item');
                option.href = '#'; // Add link behavior if needed
                console.log(configuration);
                option.id = `${configuration.id}`;
                option.textContent = `Configuration ${configuration.name}`;
                dropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });
}

function getPresets() {
    fetch('/api/v1/fanWall/presets')
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        const dropdown = document.getElementById('presetDropdown');
        dropdown.innerHTML = '';
        data.presets.forEach(preset => {
            const option = document.createElement('a');
            option.classList.add('dropdown-item');
            option.href = '#';
            option.id = `${preset.id}`;
            option.textContent = `Preset ${preset.name}`;
            // 👇 AÑADE ESTE MANEJADOR
            option.addEventListener('click', (e) => {
                e.preventDefault();
                importPreset(preset.id);
            });
            dropdown.appendChild(option);
        });
    })
    .catch(error => console.error('Error getPresets:', error));
}

function getSameSizePresets(){
    gridSize = getGridSize();
    isRectangular = areGridItemsRectangular();
    if (isRectangular == false){
        console.log('Grid items are not rectangular');
        return;
    }
    fetch(`/api/v1/fanWall/presets/same_size/${gridSize[0]}/${gridSize[1]}`)
        .then(response => {
            if (!response.ok) {
            throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.error){
                showAlert(data.error, "warning");
                return;
            }
            const dropdown = document.getElementById('presetDropdown');
            dropdown.innerHTML = ''; // Clear existing options
            console.log(data);
            data.presets.forEach(preset => {
                const option = document.createElement('a');
                option.classList.add('dropdown-item');
                option.href = '#'; // Add link behavior if needed
                console.log(preset);
                option.id = `${preset.id}`;
                option.textContent = `Preset ${preset.name}`;
                dropdown.appendChild(option);
            });
        })
        .catch(error => {
            console.error('There was a problem with the fetch operation:', error);
        });

}

function createConfiguration(id, configurationName){
    const postData = {
        name: configurationName
    };
    fetch(`/api/v1/fanWall/configurations/${id}`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify({name: configurationName})
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function saveConfiguration(){
    console.log('Saving configuration...');
    configurationName= document.getElementById('newConfigurationNameInputBox').value;
    id = null;
    const configurationMatrix = exportGridAsMatrix();
    const postData = {
        name: configurationName,
        controllers: configurationMatrix
    };

    fetch(`/api/v1/fanWall/configurations/create_with_controllers`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
        currentConfiguration.id = data.id;
        currentConfiguration.name = configurationName;
        document.getElementById('currentConfiguration').textContent = data.name;
        getConfigurations();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function savePreset(){
    console.log('Saving preset...');
    const presetName = document.getElementById('newPresetNameInputBox').value;
    const presetJSON = JSON.parse(document.getElementById('newPresetJsonInputBox').value);
    const postData = {
        name: presetName,
        data: presetJSON
    };

    fetch(`/api/v1/fanWall/presets`, {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Response from server:', data);
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        
        getConfigurations();
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function updateConfiguration(configurationId){
    console.log('Updating configuration...');
    const configurationMatrix = exportGridAsMatrix();
    const postData = {
        controllers: configurationMatrix
    };
    console.log(postData);

    fetch(`/api/v1/fanWall/configurations/${configurationId}/controllers`, {
        method: 'PATCH',
        headers: {
        'Content-Type': 'application/json',
        },
        body: JSON.stringify(postData)
    })
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Response from server:', data);
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

function importConfiguration(configurationId) {
    console.log('Importing configuration:', configurationId);
    fetch(`/api/v1/fanWall/configurations/${configurationId}/controllers`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, "warning");
                return;
            }
            console.log('Configuration matrix:', data.controllers);
            
            // Actualizar ambas variables
            currentConfiguration = { id: configurationId, name: data.name };
            window.currentConfiguration = currentConfiguration;
            
            const span = document.getElementById('currentConfiguration');
            if (span) span.textContent = data.name;
            
            if (typeof importGridFromJSON === 'function') {
                importGridFromJSON(data.controllers);
            }
            showAlert(`Configuración "${data.name}" cargada`, "success");
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar configuración', "danger");
        });
}

function importPreset(presetId) {
    console.log('Importing preset...', presetId);
    fetch(`/api/v1/fanWall/presets/${presetId}`)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        window.currentPreset = { id: presetId, name: data.name };
        let span = document.getElementById('currentPreset');
        if (span) span.textContent = data.name;
        console.log('Preset cargado:', window.currentPreset);
        showAlert(`Preset "${data.name}" cargado`, "success");

        // ========== APLICAR MATRIZ DEL PRESET AL GRID ==========
        if (data.data && data.data.frames && data.data.frames.length > 0) {
            var matrix = data.data.frames[0].matrix; // Ej: [[0,3],[1,2]]
            var config = {};
            for (var y = 0; y < matrix.length; y++) {
                for (var x = 0; x < matrix[y].length; x++) {
                    var id = matrix[y][x];
                    if (id !== 0) {
                        var moduleId = "modulo-" + id;
                        config[moduleId] = { x: x, y: y, name: moduleId };
                    }
                }
            }
            if (typeof importGridFromJSON === 'function') {
                importGridFromJSON(config);
            }
        }
        // ========================================================
    })
    .catch(error => console.error('Error importPreset:', error));
}

function runPreset(){
    // Verificar que haya un preset cargado
    if (!window.currentPreset || !window.currentPreset.id) {
        console.error("No preset loaded. Please load a preset first.");
        showAlert("No preset loaded", "warning");
        return;
    }
    // Verificar que haya una configuración cargada
    if (!window.currentConfiguration || !window.currentConfiguration.id) {
        console.error("No configuration loaded. Please load a configuration first.");
        showAlert("No configuration loaded", "warning");
        return;
    }
    startProcedure();
    const url = `/api/v1/fanWall/presets/${window.currentPreset.id}/configuration/${window.currentConfiguration.id}`;
    console.log('Running preset with URL:', url);
    fetch(url)
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, "warning");
            return;
        }
        console.log('Preset running response:', data);
    })
    .catch(error => console.error('Error runPreset:', error));
}

function stopPreset(){
    console.log('Stopping preset...');
    fetch(`/api/v1/fanWall/presets/${currentPreset.id}/configuration/${currentConfiguration.id}/stop`)
    .then(response => {
        if (!response.ok) {
        throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.error){
            showAlert(data.error, "warning");
            return;
        }
        console.log('Response from server:', data);
        stopProcedure()
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

// ==========================================
// GESTIÓN DE PRESETS (editar/eliminar)
// ==========================================

function loadPresetsList() {
    const container = document.getElementById('presetsList');
    if (!container) return;
    container.innerHTML = '<p class="text-muted">Cargando presets...</p>';

    fetch('/api/v1/fanWall/presets')
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                container.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                return;
            }
            if (!data.presets || data.presets.length === 0) {
                container.innerHTML = '<p class="text-muted">No hay presets guardados.</p>';
                return;
            }
            let html = '<ul class="list-group">';
            data.presets.forEach(preset => {
                html += `
                    <li class="list-group-item d-flex justify-content-between align-items-center">
                        <span><strong>${preset.name}</strong> (ID: ${preset.id})</span>
                        <div>
                            <button class="btn btn-sm btn-primary me-1" onclick="openEditPresetModal(${preset.id})">Editar</button>
                            <button class="btn btn-sm btn-danger" onclick="deletePreset(${preset.id})">Eliminar</button>
                        </div>
                    </li>
                `;
            });
            html += '</ul>';
            container.innerHTML = html;
        })
        .catch(error => {
            container.innerHTML = `<div class="alert alert-danger">Error al cargar presets: ${error.message}</div>`;
        });
}

function openEditPresetModal(presetId) {
    fetch(`/api/v1/fanWall/presets/${presetId}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showAlert(data.error, 'warning');
                return;
            }
            document.getElementById('editPresetId').value = presetId;
            document.getElementById('editPresetName').value = data.name;
            document.getElementById('editPresetJson').value = JSON.stringify(data.data, null, 2);
            const modal = new bootstrap.Modal(document.getElementById('editPresetModal'));
            modal.show();
        })
        .catch(error => {
            console.error('Error:', error);
            showAlert('Error al cargar los datos del preset', 'danger');
        });
}

function saveEditedPreset() {
    const presetId = document.getElementById('editPresetId').value;
    const newName = document.getElementById('editPresetName').value.trim();
    const jsonText = document.getElementById('editPresetJson').value.trim();

    if (!newName) {
        showAlert('El nombre no puede estar vacío', 'warning');
        return;
    }

    let newData;
    try {
        newData = JSON.parse(jsonText);
    } catch (e) {
        showAlert('El JSON no es válido. Revisa el formato.', 'danger');
        return;
    }

    const postData = { name: newName, data: newData };

    fetch(`/api/v1/fanWall/presets/${presetId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(postData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'warning');
            return;
        }
        const modal = bootstrap.Modal.getInstance(document.getElementById('editPresetModal'));
        if (modal) modal.hide();
        showAlert('Preset actualizado correctamente', 'success');
        loadPresetsList();        // recargar lista
        getPresets();            // actualizar dropdown
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al actualizar el preset', 'danger');
    });
}

function deletePreset(presetId) {
    if (!confirm('¿Estás seguro de que deseas eliminar este preset? Esta acción no se puede deshacer.')) {
        return;
    }

    fetch(`/api/v1/fanWall/presets/${presetId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' }
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            showAlert(data.error, 'warning');
            return;
        }
        showAlert('Preset eliminado correctamente', 'success');
        loadPresetsList();
        getPresets();
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('Error al eliminar el preset', 'danger');
    });
}