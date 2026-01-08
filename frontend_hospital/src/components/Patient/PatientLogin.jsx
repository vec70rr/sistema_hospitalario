import React, { useState } from 'react';
import axios from 'axios';

// La autenticación del paciente es implícita en la solicitud de cita o búsqueda.
// Usaremos un endpoint simple de validación si existiera, pero dado que solo 
// implementamos la solicitud de cita, simularemos la autenticación 
// al obtener el ID del paciente a partir del CURP.
const API_LOOKUP_URL = 'http://127.0.0.1:8000/api/expediente/lookup/'; // <-- RUTA PÚBLICA
//const API_LOOKUP_URL = 'https://sistemahospitalario-production.up.railway.app/api/expediente/lookup/'; // <-- RUTA PÚBLICA

function PatientLogin({ onLoginSuccess }) {
    const [curp, setCurp] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            // NOTA: Usamos el endpoint de búsqueda del Médico por simplicidad, 
            // ya que se necesita obtener el ID del paciente a partir del CURP.
            // En un sistema real, existiría un endpoint de /api/paciente/auth/
            
            const response = await axios.get(`${API_LOOKUP_URL}?curp=${curp}`);

            if (response.data.length === 1) {
                const patient = response.data[0];
                // Almacenar CURP e ID del paciente
                localStorage.setItem('patientCURP', patient.CURP);
                localStorage.setItem('patientId', patient.id);
                
                onLoginSuccess(patient);
            } else {
                [cite_start]// E-P01: CURP no válido o no encontrado [cite: 517]
                setError("CURP no válido o no encontrado (E-P01). Asegúrese de estar registrado.");
            }

        } catch (err) {
            console.error("Error de autenticación paciente:", err);
            setError('Error de conexión. Intente más tarde.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: 'auto', border: '1px solid #ddd' }}>
            <h2>🗓️ Portal de Citas</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label>Ingrese su CURP:</label>
                    <input
                        type="text"
                        value={curp}
                        onChange={(e) => setCurp(e.target.value.toUpperCase())}
                        required
                        maxLength={18}
                        style={{ width: '100%', padding: '8px' }}
                    />
                </div>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <button type="submit" disabled={loading} style={{ padding: '10px', width: '100%', backgroundColor: '#28a745', color: 'white' }}>
                    {loading ? 'Validando...' : 'Acceder a mi Agenda'}
                </button>
            </form>
        </div>
    );
}

export default PatientLogin;