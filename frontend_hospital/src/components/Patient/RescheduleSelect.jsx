import React, { useState, useEffect } from 'react';
import axios from 'axios';

//const API_OPCIONES_URL = 'http://127.0.0.1:8000/api/agenda/opciones/';
//const API_CANCEL_URL = 'http://127.0.0.1:8000/api/agenda/cancelar/';
//const API_CREAR_ELEGIDO_URL = 'http://127.0.0.1:8000/api/agenda/crear_elegido/';
const API_OPCIONES_URL = 'https://sistemahospitalario-production.up.railway.app/api/agenda/opciones/';
const API_CANCEL_URL = 'https://sistemahospitalario-production.up.railway.app/api/agenda/cancelar/';
const API_CREAR_ELEGIDO_URL = 'https://sistemahospitalario-production.up.railway.app/api/agenda/crear_elegido/';

function RescheduleSelect() {
    const [options, setOptions] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const citaOriginalId = localStorage.getItem('rescheduleCitaId');

    // 1. Obtener opciones disponibles
    useEffect(() => {
        const fetchOptions = async () => {
            try {
                const response = await axios.get(API_OPCIONES_URL);
                setOptions(response.data);
            } catch (err) {
                setError('No se pudieron cargar opciones disponibles (E-P02).');
            } finally {
                setLoading(false);
            }
        };
        fetchOptions();
    }, []);

    // 2. Manejar la selección del slot (Cancelación + Creación de Nueva Cita)
    const handleSelectSlot = async (slot) => {
        if (!citaOriginalId) return;

        setLoading(true);
        setError('');
        
        try {
            // A. Cancelar la cita original (RB-005)
            await axios.post(API_CANCEL_URL, { cita_id: parseInt(citaOriginalId) });
            
            // B. Crear la nueva cita con el slot seleccionado por el usuario
            const patientId = localStorage.getItem('patientId');
            
            // Lógica final de reagendación:
            const newCitaResponse = await axios.post(API_CREAR_ELEGIDO_URL, { 
                paciente_id: parseInt(patientId),
                agenda_id: slot.agenda_id,
                fecha_hora: slot.fecha_hora 
            });

            alert(`✅ Reagendación exitosa. Cita original (${citaOriginalId}) cancelada. Nueva cita asignada: ${newCitaResponse.data.fecha_hora}`);
            // Redirigir al panel principal de citas
            localStorage.removeItem('rescheduleCitaId');
            window.location.href = '/'; 

        } catch (err) {
            alert(`Error al confirmar reagendación. La cita original (${citaOriginalId}) fue cancelada, pero no se pudo asignar la nueva. Por favor, solicite una nueva cita.`);
            window.location.href = '/'; // Redirigir de vuelta para ver el estado
        } finally {
            setLoading(false);
        }
    };
    
    // ... (rest of the component) ...
    if (loading) return <p>Cargando opciones...</p>;

    return (
        <div style={{ padding: '20px', maxWidth: '600px', margin: 'auto' }}>
            <h3>🕒 Seleccionar Nuevo Horario (Cita Original ID: {citaOriginalId})</h3>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            
            {options.length > 0 ? (
                options.map((slot, index) => (
                    <div key={index} style={{ border: '1px solid #ccc', padding: '10px', marginBottom: '10px' }}>
                        <p><strong>Fecha:</strong> {new Date(slot.fecha_hora).toLocaleDateString()} a las {new Date(slot.fecha_hora).toLocaleTimeString()} </p>
                        <p><strong>Dr(a):</strong> {slot.medico_nombre} | **Consultorio:** {slot.consultorio}</p>
                        <button 
                            onClick={() => handleSelectSlot(slot)} 
                            disabled={loading}
                            style={{ padding: '5px 10px', backgroundColor: '#007bff', color: 'white' }}
                        >
                            Seleccionar Slot
                        </button>
                    </div>
                ))
            ) : (
                <p>No se encontraron horarios disponibles para reagendar. Intente solicitar una nueva cita.</p>
            )}
        </div>
    );
}

export default RescheduleSelect;