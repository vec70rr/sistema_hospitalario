import React from 'react';

function SuperAdminPanel() {
    return (
        <div style={{ maxWidth: '800px', margin: 'auto', padding: '20px', border: '3px solid #f0ad4e' }}>
            <h2>⚙️ Panel de Súper Administrador</h2>
            <p>Este es el panel central de gestión de la Clínica.</p>
            
            <h4>Funciones Principales:</h4>
            <ul>
                <li>Gestión de Usuarios (Médicos y Admins) </li>
                <li>Visualizar Reportes de Errores del Sistema </li>
                <li>Configuración de Agendas y Consultorios</li>
            </ul>
            <p style={{ marginTop: '20px', color: '#f0ad4e' }}>
                Nota: La gestión real de usuarios y errores se realiza a través del Admin Site de Django (ruta: /admin/).
            </p>
        </div>
    );
}

export default SuperAdminPanel;