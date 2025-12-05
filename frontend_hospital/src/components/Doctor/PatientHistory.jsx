import React, { useState, useEffect } from 'react';
import axios from 'axios';

//const API_BASE_URL = 'http://127.0.0.1:8000/api/expediente/historial/';
const API_BASE_URL = 'https://sistemahospitalario-production.up.railway.app/api/expediente/historial/';

function PatientHistory({ patientId }) {
    const [history, setHistory] = useState({ notes: [], recipes: [] });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const token = localStorage.getItem('authToken');

    useEffect(() => {
        const token = localStorage.getItem('authToken');
        if (!patientId || !token) {
            setLoading(false);
            setError('Error de sesión o paciente no seleccionado.');
            return;
        }

        const fetchHistory = async () => {
            setLoading(true);
            setError('');
            
            try {
                // Petición para Notas de Consulta
                const notesResponse = await axios.get(`${API_BASE_URL}notas/${patientId}/`, {
                    headers: { Authorization: `Token ${token}` }
                });
                
                // Petición para Recetas Digitales
                const recipesResponse = await axios.get(`${API_BASE_URL}recetas/${patientId}/`, {
                    headers: { Authorization: `Token ${token}` }
                });

                setHistory({ 
                    notes: notesResponse.data, 
                    recipes: recipesResponse.data 
                });

            } catch (err) {
                console.error("Error cargando historial:", err);
                setError('No se pudo cargar el historial del paciente. Verifique su conexión o permisos.');
            } finally {
                setLoading(false);
            }
        };

        fetchHistory();
    }, [patientId]);


    if (loading) return <p>Cargando historial clínico...</p>;
    if (error) return <p style={{ color: 'red' }}>{error}</p>;

    return (
        <div style={{ marginTop: '30px' }}>
            <h3>📖 Historial Clínico ({history.notes.length + history.recipes.length} Entradas)</h3>
            
            {/* --- LISTA DE NOTAS DE CONSULTA --- */}
            <h4>Notas de Consulta (Últimas primero)</h4>
            {history.notes.length === 0 ? (
                <p>No hay notas de consulta registradas.</p>
            ) : (
                history.notes.map((note) => (
                    <div key={note.id} style={{ border: '1px solid #ccc', padding: '15px', marginBottom: '15px', borderRadius: '5px' }}>
                        <p><strong>Fecha:</strong> {new Date(note.fecha_registro).toLocaleString()} | <strong>Médico:</strong> {note.medico_nombre}</p>
                        <p><strong>Diagnóstico:</strong> {note.diagnostico}</p>
                        <p><strong>Evolución:</strong> {note.evolucion.substring(0, 150)}...</p>
                        <p><strong>Tratamiento:</strong> {note.tratamiento}</p>
                    </div>
                ))
            )}

            {/* --- LISTA DE RECETAS --- */}
            <h4>Recetas Digitales</h4>
            {history.recipes.length === 0 ? (
                <p>No hay recetas registradas.</p>
            ) : (
                history.recipes.map((recipe) => (
                    <div key={recipe.id} style={{ border: '1px solid #007bff', padding: '15px', marginBottom: '15px', borderRadius: '5px' }}>
                        <p><strong>Fecha Emisión:</strong> {new Date(recipe.fecha_emision).toLocaleDateString()} | <strong>Dr(a):</strong> {recipe.medico_nombre}</p>
                        <p><strong>Diagnóstico:</strong> {recipe.diagnostico} | <strong>Peso:</strong> {recipe.peso} kg | <strong>Talla:</strong> {recipe.talla} m</p>
                        <p><strong>Medicamentos ({recipe.detalles.length}):</strong></p>
                        <ul>
                            {recipe.detalles.map(detail => (
                                <li key={detail.medicamento}>
                                    {detail.medicamento} ({detail.presentacion}) - **Dosis:** {detail.dosificacion}
                                </li>
                            ))}
                        </ul>
                    </div>
                ))
            )}
        </div>
    );
}

export default PatientHistory;