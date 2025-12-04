import React, { useState } from 'react';
import axios from 'axios';

const API_RECIPE_URL = 'http://127.0.0.1:8000/api/expediente/recetas/';

const initialRecipeState = {
    diagnostico: '',
    talla: '',
    peso: '',
    detalles: [{ medicamento: '', presentacion: '', dosificacion: '', cantidad: 1 }]
};

function RecipeForm({ patientId }) {
    const [recipeData, setRecipeData] = useState(initialRecipeState);
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const token = localStorage.getItem('authToken');

    const handleRecipeChange = (e) => {
        setRecipeData({ ...recipeData, [e.target.name]: e.target.value });
    };

    const handleDetailChange = (index, e) => {
        const newDetails = recipeData.detalles.map((detail, i) => {
            if (i === index) {
                return { ...detail, [e.target.name]: e.target.value };
            }
            return detail;
        });
        setRecipeData({ ...recipeData, detalles: newDetails });
    };

    const addDetail = () => {
        setRecipeData({
            ...recipeData,
            detalles: [...recipeData.detalles, { medicamento: '', presentacion: '', dosificacion: '', cantidad: 1 }]
        });
    };

    const removeDetail = (index) => {
        const newDetails = recipeData.detalles.filter((_, i) => i !== index);
        setRecipeData({ ...recipeData, detalles: newDetails });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setMessage('');
        setError('');

        const dataToSend = {
            ...recipeData,
            paciente: patientId,
            // Asegurar que talla y peso sean números para el backend
            talla: recipeData.talla ? parseFloat(recipeData.talla) : null,
            peso: recipeData.peso ? parseFloat(recipeData.peso) : null,
        };

        try {
            await axios.post(API_RECIPE_URL, dataToSend, {
                headers: {
                    Authorization: `Token ${token}`
                }
            });

            setMessage(`✅ Receta Digital emitida exitosamente (NOM-024).`);
            setRecipeData(initialRecipeState); // Limpiar formulario
            
        } catch (err) {
            console.error("Error emitiendo receta:", err.response?.data);
            setError('❌ Error al emitir la receta. Verifique los campos de diagnóstico y dosificación.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} style={{ marginTop: '20px', padding: '15px', border: '1px solid #007bff33' }}>
            <h4>💊 Generar Receta Digital (NOM-024)</h4>
            
            {/* Datos Demográficos (Parte Obligatoria: RB-012) */}
            <div style={{ display: 'flex', gap: '15px', marginBottom: '15px' }}>
                <div style={{ flex: 1 }}>
                    <label>Diagnóstico:*</label>
                    <input type="text" name="diagnostico" value={recipeData.diagnostico} onChange={handleRecipeChange} required style={{ width: '100%', padding: '8px' }} />
                </div>
                <div style={{ width: '100px' }}>
                    <label>Talla (m):</label>
                    <input type="number" step="0.01" name="talla" value={recipeData.talla} onChange={handleRecipeChange} style={{ width: '100%', padding: '8px' }} />
                </div>
                <div style={{ width: '100px' }}>
                    <label>Peso (kg):</label>
                    <input type="number" step="0.01" name="peso" value={recipeData.peso} onChange={handleRecipeChange} style={{ width: '100%', padding: '8px' }} />
                </div>
            </div>

            {/* Detalles de Medicamentos (Sección Crítica: RB-012) */}
            <h5>Medicamentos y Dosificación:*</h5>
            {recipeData.detalles.map((detail, index) => (
                <div key={index} style={{ border: '1px dotted #ccc', padding: '10px', marginBottom: '10px' }}>
                    <div style={{ display: 'flex', gap: '10px' }}>
                        <div style={{ flex: 2 }}>
                            <label>Medicamento:</label>
                            <input type="text" name="medicamento" value={detail.medicamento} onChange={(e) => handleDetailChange(index, e)} required style={{ width: '100%' }} />
                        </div>
                        <div style={{ flex: 1 }}>
                            <label>Presentación:</label>
                            <input type="text" name="presentacion" value={detail.presentacion} onChange={(e) => handleDetailChange(index, e)} style={{ width: '100%' }} />
                        </div>
                        <div style={{ width: '60px' }}>
                            <label>Cant:</label>
                            <input type="number" name="cantidad" value={detail.cantidad} onChange={(e) => handleDetailChange(index, e)} style={{ width: '100%' }} />
                        </div>
                        <button type="button" onClick={() => removeDetail(index)} disabled={recipeData.detalles.length === 1} style={{ alignSelf: 'flex-end' }}>
                            -
                        </button>
                    </div>
                    <div style={{ marginTop: '5px' }}>
                        <label>Dosificación/Indicaciones:*</label>
                        <textarea name="dosificacion" value={detail.dosificacion} onChange={(e) => handleDetailChange(index, e)} required style={{ width: '100%', minHeight: '50px' }} />
                    </div>
                </div>
            ))}
            
            <button type="button" onClick={addDetail} style={{ padding: '5px 10px', marginBottom: '15px' }}>
                + Agregar Medicamento
            </button>
            
            {message && <p style={{ color: 'green', marginTop: '10px' }}>{message}</p>}
            {error && <p style={{ color: 'red', marginTop: '10px' }}>{error}</p>}

            <button type="submit" disabled={loading} style={{ padding: '10px', width: '100%', backgroundColor: '#007bff', color: 'white' }}>
                {loading ? 'Emitiendo...' : 'Emitir Receta Digital (Firmar)'}
            </button>
        </form>
    );
}

export default RecipeForm;