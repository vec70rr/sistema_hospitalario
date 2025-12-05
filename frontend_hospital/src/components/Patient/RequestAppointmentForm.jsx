import React, { useState } from 'react';
import axios from 'axios';

//const API_REQUEST_URL = 'http://127.0.0.1:8000/api/agenda/solicitar/';
const API_REQUEST_URL = 'https://sistemahospitalario-production.up.railway.app/api/agenda/solicitar/';

function RequestAppointmentForm({ patientId, onAppointmentChange }) {
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const handleRequest = async () => {
        setLoading(true);
        setMessage('');
        setError('');

        try {
            const response = await axios.post(API_REQUEST_URL, { paciente_id: patientId });

            // Cita asignada con éxito (RB-003)
            setMessage(`✅ Cita Autoasignada: ${response.data.fecha_hora} con Dr. ${response.data.medico} en consultorio ${response.data.consultorio}`);
            
            // Llama a la función para recargar la lista de citas
            if (onAppointmentChange) onAppointmentChange(); 

        } catch (err) {
            console.error("Error solicitando cita:", err.response?.data);
            const errorMessage = err.response?.data?.message || "No se encontraron slots disponibles (E-P02).";
            setError(`❌ Error: ${errorMessage}`);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', border: '1px solid #28a745', borderRadius: '5px' }}>
            <h4>Solicitar Cita de Medicina General</h4>
            <p>El sistema asignará automáticamente el primer slot disponible a partir de mañana (30 min).</p>
            
            {message && <p style={{ color: 'green', fontWeight: 'bold' }}>{message}</p>}
            {error && <p style={{ color: 'red', fontWeight: 'bold' }}>{error}</p>}

            <button 
                onClick={handleRequest} 
                disabled={loading}
                style={{ padding: '10px', width: '100%', backgroundColor: '#28a745', color: 'white', border: 'none' }}
            >
                {loading ? 'Buscando Slot...' : 'Solicitar Autoasignación'}
            </button>
        </div>
    );
}

export default RequestAppointmentForm;