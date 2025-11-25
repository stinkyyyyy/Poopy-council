import { useState, useEffect } from 'react';
import './SettingsModal.css';
import { api } from '../api';

export default function SettingsModal({ isOpen, onClose }) {
  const [personas, setPersonas] = useState([]);
  const [baseModel, setBaseModel] = useState('');
  const [importUrl, setImportUrl] = useState('');

  useEffect(() => {
    if (isOpen) {
      api.getSettings().then((data) => {
        setPersonas(data.personas);
        setBaseModel(data.base_model);
      });
    }
  }, [isOpen]);

  if (!isOpen) {
    return null;
  }

  const handlePersonaChange = (index, field, value) => {
    const newPersonas = [...personas];
    newPersonas[index][field] = value;
    setPersonas(newPersonas);
  };

  const addPersona = () => {
    setPersonas([...personas, { name: 'New Persona', prompt: '' }]);
  };

  const removePersona = (index) => {
    const newPersonas = personas.filter((_, i) => i !== index);
    setPersonas(newPersonas);
  };

  const handleSave = () => {
    api.updateSettings({ personas }).then(() => {
      onClose();
    });
  };

  const handleImport = () => {
    api.fetchSettings(importUrl).then((data) => {
      setPersonas(data.personas);
      setImportUrl('');
    });
  };

  return (
    <div className="modal-overlay">
      <div className="modal">
        <div className="modal-header">
          <h2>Settings</h2>
          <button onClick={onClose} className="close-btn">&times;</button>
        </div>
        <div className="modal-content">
          <div className="setting">
            <label>Base Model:</label>
            <span>{baseModel}</span>
          </div>
          <hr />
          <h3>Personas</h3>
          {personas.map((persona, index) => (
            <div key={index} className="persona-editor">
              <input
                type="text"
                value={persona.name}
                onChange={(e) => handlePersonaChange(index, 'name', e.target.value)}
                placeholder="Persona Name"
              />
              <textarea
                value={persona.prompt}
                onChange={(e) => handlePersonaChange(index, 'prompt', e.target.value)}
                placeholder="System Prompt"
              />
              <button onClick={() => removePersona(index)} className="remove-persona-btn">Remove</button>
            </div>
          ))}
          <button onClick={addPersona} className="add-persona-btn">Add Persona</button>
          <hr />
          <h3>Import Personas</h3>
          <div className="import-section">
            <input
              type="text"
              value={importUrl}
              onChange={(e) => setImportUrl(e.target.value)}
              placeholder="Enter URL to a personas.json file"
            />
            <button onClick={handleImport}>Import</button>
          </div>
        </div>
        <div className="modal-footer">
          <button onClick={onClose}>Cancel</button>
          <button onClick={handleSave} className="save-btn">Save</button>
        </div>
      </div>
    </div>
  );
}
