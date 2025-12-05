import React, { useState, useEffect } from 'react';
import axios from 'axios';

//const API_ORDER_URL = 'http://127.0.0.1:8000/api/expediente/ordenes/';
//const API_SPECIALTY_URL = 'http://127.0.0.1:8000/api/personal/especialidades/'; 
const API_ORDER_URL = 'https://sistemahospitalario-production.up.railway.app/api/expediente/ordenes/';
const API_SPECIALTY_URL = 'https://sistemahospitalario-production.up.railway.app/api/personal/especialidades/';

function OrderForm({ patientId }) {
    const [specialties, setSpecialties] = useState([]);
    const [formData, setFormData] = useState({
        paciente: patientId,
        especialidad_solicitada: '', // Campo obligatorio
        motivo_referencia: '',      
    });
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const token = localStorage.getItem('authToken');

    // Cargar el catálogo de especialidades al inicio
    useEffect(() => {
        const fetchSpecialties = async () => {
            try {
                const response = await axios.get(API_SPECIALTY_URL, {
                    headers: { Authorization: `Token ${token}` }
                });
                setSpecialties(response.data);
            } catch (err) {
                console.error("Error cargando especialidades:", err);
                setError("No se pudieron cargar las especialidades.");
            }
        };
        fetchSpecialties();
    }, [token]);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        setError('');

        try {
            await axios.post(API_ORDER_URL, formData, {
                headers: {
                    Authorization: `Token ${token}`
                }
            });

            setMessage(`✅ Orden de referencia emitida exitosamente para ${formData.especialidad_solicitada}.`);
            setError('');
            setFormData({ ...formData, especialidad_solicitada: '', motivo_referencia: '' }); // Limpiar formulario
            
        } catch (err) {
            console.error("Error emitiendo orden:", err.response?.data);
            setError('❌ Error al emitir la orden. Verifique que haya seleccionado una especialidad y llenado el motivo.');
        } finally {
            setLoading(false);
        }
    };
    
    // Si no hay especialidades cargadas, no mostrar el formulario
    if (specialties.length === 0 && !error) {
        return <p>Cargando especialidades...</p>;
    }
    
    return (
        <form onSubmit={handleSubmit} style={{ marginTop: '20px', padding: '15px', border: '1px solid #7777ff33' }}>
            <h4>📜 Emitir Orden de Referencia (MG)</h4>
            
            {/* Especialidad Solicitada (Catálogo) */}
            <div style={{ marginBottom: '15px' }}>
                <label>Especialidad Requerida:*</label>
                <select 
                    name="especialidad_solicitada" 
                    value={formData.especialidad_solicitada} 
                    onChange={handleChange} 
                    required 
                    style={{ width: '100%', padding: '8px' }}
                >
                    <option value="">-- Seleccione Especialidad --</option>
                    {specialties.map(spec => (
                        <option key={spec.id} value={spec.nombre}>{spec.nombre}</option>
                    ))}
                </select>
            </div>
            
            {/* Motivo de Referencia */}
            <div style={{ marginBottom: '15px' }}>
                <label>Motivo de la Referencia:*</label>
                <textarea 
                    name="motivo_referencia" 
                    value={formData.motivo_referencia} 
                    onChange={handleChange} 
                    required 
                    style={{ width: '100%', minHeight: '80px' }}
                />
            </div>
            
            {message && <p style={{ color: 'green', marginTop: '10px' }}>{message}</p>}
            {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}

            <button type="submit" disabled={loading} style={{ padding: '10px', width: '100%', backgroundColor: '#5cb85c', color: 'white' }}>
                {loading ? 'Emitiendo Orden...' : 'Emitir Orden'}
            </button>
        </form>
    );
}

export default OrderForm;