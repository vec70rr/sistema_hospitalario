import React, { useState } from 'react';
import PatientSearch from './PatientSearch';
import ClinicalNoteForm from './ClinicalNoteForm';
import RecipeForm from './RecipeForm';
import OrderForm from './OrderForm';
import PatientHistory from './PatientHistory';
// Importaremos componentes para la Nota Clínica y Receta en el siguiente paso

function DoctorPanel() {
    const [selectedPatient, setSelectedPatient] = useState(null);
    const userRole = localStorage.getItem('userRole'); // Ejemplo: MEDICO, ADMIN_SUPER

    // Función que se pasa al componente de búsqueda para seleccionar un paciente
    const handlePatientSelect = (patient) => {
        setSelectedPatient(patient);
    };

    return (
        <div style={{ maxWidth: '1200px', margin: 'auto', padding: '20px' }}>
            <h2>Panel Médico 👨‍⚕️</h2>
            <p>Bienvenido, {userRole}. Funcionalidad clave: Gestión de Expedientes.</p>
            
            <PatientSearch onPatientSelect={handlePatientSelect} />

            {selectedPatient && (
                <div style={{ marginTop: '30px', borderTop: '2px solid #007bff', paddingTop: '20px' }}>
                    <h3>Expediente de {selectedPatient.nombre} {selectedPatient.apellidos}</h3>
                    <p><strong>CURP:</strong> {selectedPatient.CURP} | <strong>Tipo:</strong> {selectedPatient.tipo === 'A' ? 'Asegurado' : 'No Asegurado'}</p>
                    
                    {/* 2. MOSTRAR EL HISTORIAL DEBAJO DE LA INFORMACIÓN DE REGISTRO */}
                    <div style={{ display: 'flex', gap: '20px', marginBottom: '30px' }}>
                        <div style={{ flex: 1 }}>
                            <ClinicalNoteForm patientId={selectedPatient.id} />
                        </div>
                        <div style={{ flex: 1 }}>
                            <RecipeForm patientId={selectedPatient.id} />
                            <div style={{ marginTop: '20px' }}><OrderForm patientId={selectedPatient.id} /></div>
                        </div>
                    </div>

                    {/* 3. AGREGAR EL COMPONENTE DE HISTORIAL EN LA PARTE INFERIOR */}
                    <PatientHistory patientId={selectedPatient.id} />
                </div>
            )}
        </div>
    );
}

export default DoctorPanel;