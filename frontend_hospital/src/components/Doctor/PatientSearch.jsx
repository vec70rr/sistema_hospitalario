import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000/api/expediente/pacientes/';

function PatientSearch({ onPatientSelect }) {
    const [searchTerm, setSearchTerm] = useState('');
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const token = localStorage.getItem('authToken');

    const handleSearch = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setResults([]);

        try {
            const response = await axios.get(`${API_BASE_URL}?search=${searchTerm}`, {
                headers: {
                    Authorization: `Token ${token}` // Autenticación con el token del Médico
                }
            });

            setResults(response.data);
            if (response.data.length === 0) {
                setError('No se encontraron pacientes.');
            }

        } catch (err) {
            console.error("Error buscando paciente:", err);
            setError('Error al conectar o no autorizado. Intente iniciar sesión de nuevo.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ padding: '20px', border: '1px solid #ccc', borderRadius: '5px' }}>
            <h3>🔍 Búsqueda de Pacientes (CURP, Nombre, Expediente)</h3>
            <form onSubmit={handleSearch} style={{ display: 'flex', marginBottom: '20px' }}>
                <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    placeholder="Buscar por CURP o Nombre..."
                    required
                    style={{ flexGrow: 1, padding: '10px' }}
                />
                <button type="submit" disabled={loading} style={{ padding: '10px', marginLeft: '10px' }}>
                    {loading ? 'Buscando...' : 'Buscar'}
                </button>
            </form>

            {error && <p style={{ color: 'red' }}>{error}</p>}

            {results.length > 0 && (
                <ul style={{ listStyleType: 'none', padding: 0 }}>
                    {results.map(patient => (
                        <li key={patient.id} style={{ borderBottom: '1px dotted #eee', padding: '10px 0' }}>
                            <strong>Expediente {patient.id}:</strong> {patient.nombre} {patient.apellidos} ({patient.CURP})
                            <button 
                                onClick={() => onPatientSelect(patient)}
                                style={{ float: 'right', padding: '5px 10px' }}
                            >
                                Ver Historial
                            </button>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}

export default PatientSearch;