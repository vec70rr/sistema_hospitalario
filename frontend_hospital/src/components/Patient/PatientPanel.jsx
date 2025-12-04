import React, { useState } from 'react';
import RequestAppointmentForm from './RequestAppointmentForm';
import AppointmentList from './AppointmentList';

function PatientPanel({ patient }) {
    const [refreshAppointments, setRefreshAppointments] = useState(0); // Estado para forzar recarga

    const handleAppointmentChange = () => {
        // Incrementa el estado para forzar la recarga de la lista de citas
        setRefreshAppointments(prev => prev + 1); 
    };

    return (
        <div style={{ maxWidth: '800px', margin: 'auto', padding: '20px' }}>
            <h2>Bienvenido(a), {patient.nombre} {patient.apellidos}</h2>
            <p><strong>CURP:</strong> {patient.CURP}</p>
            <p>Aquí puede gestionar sus citas de Medicina General.</p>
            
            {/* 1. SECCIÓN DE SOLICITUD DE CITA */}
            <div style={{ marginBottom: '30px' }}>
                <RequestAppointmentForm 
                    patientId={patient.id} 
                    onAppointmentChange={handleAppointmentChange}
                />
            </div>
            
            {/* 2. SECCIÓN DE CITAS ASIGNADAS */}
            <h4 style={{ marginTop: '30px' }}>Sus Citas Programadas</h4>
            <AppointmentList 
                patientId={patient.id} 
                key={refreshAppointments} // Usar key para forzar la recarga al solicitar/cancelar
            />
            
        </div>
    );
}

export default PatientPanel;