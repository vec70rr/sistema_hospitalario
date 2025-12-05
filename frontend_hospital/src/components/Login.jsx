import React, { useState } from 'react';
import axios from 'axios';

//const API_BASE_URL = 'http://127.0.0.1:8000/api/personal/login/'; // URL para desarrollo local
const API_BASE_URL = 'https://sistemahospitalario-production.up.railway.app/api/personal/login/'; // URL para producción

function LoginComponent({ onLoginSuccess }) {
    const [empleado, setEmpleado] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        try {
            const response = await axios.post(API_BASE_URL, {
                numero_empleado: empleado,
                password: password,
            });

            // Si el login es exitoso, DRF devuelve el token y el rol
            const { token, rol } = response.data;
            
            // Almacenar el token para futuras peticiones autenticadas
            localStorage.setItem('authToken', token);
            localStorage.setItem('userRole', rol);

            // Llamar a una función de manejo de éxito para redirigir
            onLoginSuccess(rol);

        } catch (err) {
            // Manejo de errores de credenciales (E-ME-01) o bloqueo (E-SA-02)
            const errorMessage = err.response?.data?.non_field_errors?.[0] || 
                                 err.response?.data?.message || 
                                 'Error de conexión o credenciales inválidas.';
            setError(errorMessage);
        }
    };

    return (
        <div style={{ padding: '20px', maxWidth: '400px', margin: 'auto' }}>
            <h2>🩺 Acceso de Personal</h2>
            <form onSubmit={handleSubmit}>
                <div style={{ marginBottom: '15px' }}>
                    <label>Número de Empleado:</label>
                    <input
                        type="text"
                        value={empleado}
                        onChange={(e) => setEmpleado(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px' }}
                    />
                </div>
                <div style={{ marginBottom: '15px' }}>
                    <label>Contraseña:</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        style={{ width: '100%', padding: '8px' }}
                    />
                </div>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                <button type="submit" style={{ padding: '10px', width: '100%' }}>
                    Iniciar Sesión
                </button>
            </form>
        </div>
    );
}

export default LoginComponent;