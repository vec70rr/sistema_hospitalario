import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/agenda/';
const API_LIST_URL = 'http://127.0.0.1:8000/api/agenda/citas/paciente/'; // <-- Crearemos este endpoint

function AppointmentList({ patientId }) {
    const [appointments, setAppointments] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [message, setMessage] = useState('');

    const fetchAppointments = async () => {
        setLoading(true);
        setError('');
        setMessage('');

        try {
            // NOTA: Para obtener esta lista, necesitamos crear el endpoint de lectura en el backend.
            const response = await axios.get(`${API_LIST_URL}${patientId}/`); 
            setAppointments(response.data);
        } catch (err) {
            console.error("Error listando citas:", err);
            setError('No se pudieron cargar sus citas.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (patientId) {
            fetchAppointments();
        }
    }, [patientId]);

    const handleCancel = async (citaId) => {
        try {
            // Llama al endpoint de Cancelación (RB-004: valida las 2 horas y MG)
            await axios.post(`${API_BASE_URL}cancelar/`, { cita_id: citaId });
            setMessage(`Cita ${citaId} cancelada exitosamente.`);
            fetchAppointments(); // Recargar lista
        } catch (err) {
            const errorMessage = err.response?.data?.non_field_errors?.[0] || 'Error al cancelar. (Fuera de tiempo o Especialidad)';
            setError(`❌ Fallo: ${errorMessage}`);
        }
    };

    const handleReschedule = (citaId) => {
    // Almacena el ID de la cita a reagendar y fuerza la navegación a la vista de opciones
    localStorage.setItem('rescheduleCitaId', citaId);
    // Nota: En una app real, aquí usarías React Router: navigate('/reagendar-select');
    window.location.href = '/reagendar-select'; 
    };

    if (loading) return <p>Cargando citas...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;

    return (
        <div>
            {message && <p style={{ color: 'blue' }}>{message}</p>}
            {appointments.length === 0 ? (
                <p>No tiene citas programadas.</p>
            ) : (
                <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {appointments.map(cita => (
                        <li key={cita.id} style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '10px' }}>
                            <p><strong>Cita ID: {cita.id}</strong></p>
                            <p><strong>Fecha/Hora:</strong> {new Date(cita.fecha_hora).toLocaleString()}</p>
                            <p><strong>Tipo:</strong> {cita.tipo_cita === 'MG' ? 'Medicina General' : 'Especialidad'}</p>
                            <p><strong>Estado:</strong> {cita.estado}</p>
                            
                            {cita.estado === 'PENDIENTE' && cita.tipo_cita === 'MG' && (
                                <div style={{ marginTop: '10px' }}>
                                    <button onClick={() => handleCancel(cita.id)} style={{ padding: '8px', marginRight: '10px', backgroundColor: '#f44336', color: 'white' }}>
                                        Cancelar (≥2h)
                                    </button>
                                    <button onClick={() => handleReschedule(cita.id)} style={{ padding: '8px', backgroundColor: '#ff9800', color: 'white' }}>
                                        Reagendar
                                    </button>
                                </div>
                            )}
                            
                            {cita.estado === 'PENDIENTE' && cita.tipo_cita === 'ESP' && (
                                <p style={{ color: '#444' }}>* Las citas de Especialidad no pueden ser canceladas/reagendadas por este portal.</p>
                            )}
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default AppointmentList;