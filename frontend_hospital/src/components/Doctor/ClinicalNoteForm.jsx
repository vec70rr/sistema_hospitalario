import React, { useState } from 'react';
import axios from 'axios';

const API_NOTE_URL = 'http://127.0.0.1:8000/api/expediente/notas/';

function ClinicalNoteForm({ patientId, onNoteSubmit }) {
    const [formData, setFormData] = useState({
        paciente: patientId, // ID del paciente (clave foránea)
        diagnostico: '',     // Obligatorio: NOM-004
        tratamiento: '',     // Obligatorio: NOM-004
        evolucion: '',       // Obligatorio: NOM-004
        procedimientos: '',
        observaciones: '',
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const token = localStorage.getItem('authToken');

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        setError('');

        try {
            const response = await axios.post(API_NOTE_URL, formData, {
                headers: {
                    Authorization: `Token ${token}`
                }
            });

            setMessage(`✅ Nota de consulta registrada exitosamente. ID: ${response.data.id}`);
            setError('');
            
            // Limpiar el formulario después del éxito
            setFormData({
                paciente: patientId,
                diagnostico: '',
                tratamiento: '',
                evolucion: '',
                procedimientos: '',
                observaciones: '',
            });
            
            // Llamar al callback para actualizar la lista de notas (si existiera)
            if (onNoteSubmit) {
                onNoteSubmit(response.data);
            }

        } catch (err) {
            console.error("Error registrando nota:", err.response?.data);
            setError('❌ Error al guardar la nota. Verifique que los campos obligatorios estén completos.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ marginTop: '20px', padding: '15px', border: '1px solid #ddd' }}>
            <h4>📝 Registrar Nueva Consulta (NOM-004)</h4>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px' }}>
                
                {/* Diagnóstico (Obligatorio) */}
                <div>
                    <label>Diagnóstico:*</label>
                    <textarea name="diagnostico" value={formData.diagnostico} onChange={handleChange} required style={{ width: '100%', minHeight: '80px' }} />
                </div>

                {/* Tratamiento (Obligatorio) */}
                <div>
                    <label>Tratamiento:*</label>
                    <textarea name="tratamiento" value={formData.tratamiento} onChange={handleChange} required style={{ width: '100%', minHeight: '80px' }} />
                </div>
                
                {/* Evolución (Obligatorio) */}
                <div style={{ gridColumn: '1 / span 2' }}>
                    <label>Evolución y Notas:*</label>
                    <textarea name="evolucion" value={formData.evolucion} onChange={handleChange} required style={{ width: '100%', minHeight: '120px' }} />
                </div>

                {/* Procedimientos (Opcional) */}
                <div>
                    <label>Procedimientos:</label>
                    <input type="text" name="procedimientos" value={formData.procedimientos} onChange={handleChange} style={{ width: '100%', padding: '8px' }} />
                </div>

                {/* Observaciones (Opcional) */}
                <div>
                    <label>Observaciones:</label>
                    <input type="text" name="observaciones" value={formData.observaciones} onChange={handleChange} style={{ width: '100%', padding: '8px' }} />
                </div>
            </div>

            {message && <p style={{ color: 'green', marginTop: '10px' }}>{message}</p>}
            {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}
            
            <button type="submit" disabled={loading} style={{ padding: '10px', marginTop: '15px', backgroundColor: '#007bff', color: 'white' }}>
                {loading ? 'Guardando...' : 'Guardar Nota Clínica'}
            </button>
        </form>
    );
}

export default ClinicalNoteForm;