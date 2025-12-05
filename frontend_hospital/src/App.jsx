import React, { useState } from 'react';
import LoginComponent from './components/Login';
import DoctorPanel from './components/Doctor/DoctorPanel';
import PatientLogin from './components/Patient/PatientLogin'; 
import PatientPanel from './components/Patient/PatientPanel';
import RescheduleSelect from './components/Patient/RescheduleSelect';
import SuperAdminPanel from './components/Admin/SuperAdminPanel';

const getInitialView = () => {
    if (localStorage.getItem('authToken')) return 'doctor';
    return 'login'; // Mostrará la vista de inicio (podríamos crear una landing, pero por ahora login)
};

function App() {
    const [view, setView] = useState(getInitialView());
    const [patientData, setPatientData] = useState(null);

    const userRole = localStorage.getItem('userRole');

    const handleDoctorLoginSuccess = (rol) => {
        if (rol === 'ADMIN_SUPER') {
            // CORRECCIÓN CRÍTICA: Redirigir al sitio real de administración de Django
            // Nota: El Súper Admin tendrá que hacer login una segunda vez en la
            // página de Django Admin porque React usa Token Auth y Django Admin usa Session Auth.
            //window.location.href = 'http://127.0.0.1:8000/admin/';
            window.location.href = 'https://sistemahospitalario-production.up.railway.app/admin/';
        } else {
            // Médicos y otros roles (si existieran) van al panel React
            setView('doctor');
        }
    };

    const handlePatientLoginSuccess = (patient) => {
        alert(`Bienvenido, ${patient.nombre}. Accediendo a su agenda.`);
        setPatientData(patient);
        setView('patient_panel');
    };
    
    // Función de Logout (para Médico)
    const handleLogout = () => {
        localStorage.removeItem('authToken');
        localStorage.removeItem('userRole');
        setView('login');
    };
    
    // Función de Salida (para Paciente)
    const handlePatientLogout = () => {
        localStorage.removeItem('patientCURP');
        localStorage.removeItem('patientId');
        setView('patient_login');
    };

    const currentPath = window.location.pathname;

    // Si la ruta es para selección de reagendación
    if (currentPath === '/reagendar-select') {
        return (
            <div className="App">
                <button onClick={handlePatientLogout} style={{ position: 'absolute', top: '10px', right: '10px', backgroundColor: '#ffc107', color: 'black' }}>
                    Cerrar Sesión (Paciente)
                </button>
                <RescheduleSelect onRescheduleComplete={handlePatientLogout} />
            </div>
        );
    }

    // --- LÓGICA DE VISTAS ---
    if (view === 'doctor') {
        return (
            <div className="App">
                <button onClick={handleLogout} style={{ position: 'absolute', top: '10px', right: '10px', backgroundColor: '#dc3545', color: 'white' }}>
                    Cerrar Sesión (Médico)
                </button>
                <DoctorPanel />
            </div>
        );
    }
    
    if (view === 'patient_panel') {
        return (
            <div className="App">
                <button onClick={handlePatientLogout} style={{ position: 'absolute', top: '10px', right: '10px', backgroundColor: '#ffc107', color: 'black' }}>
                    Cerrar Sesión (Paciente)
                </button>
                <PatientPanel patient={patientData} onLogout={handlePatientLogout} />
            </div>
        );
    }

    // Pantalla de selección inicial (simulando una landing page simple)
    if (view === 'login' || view === 'patient_login') {
        return (
            <div className="App" style={{ display: 'flex', justifyContent: 'center', gap: '50px', padding: '50px' }}>
                <LoginComponent onLoginSuccess={handleDoctorLoginSuccess} />
                <PatientLogin onLoginSuccess={handlePatientLoginSuccess} />
            </div>
        );
    }
}

export default App;