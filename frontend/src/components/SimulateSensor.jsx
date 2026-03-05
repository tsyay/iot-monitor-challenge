import React, { useState } from "react";

async function simulateSensor(payload) {
  const res = await fetch("/webhooks/sensor", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error("Ошибка симуляции датчика");
  return res.json();
}

export default function SimulateSensor() {
  const [open, setOpen] = useState(false); // состояние коллапса
  const [sensorId, setSensorId] = useState("");
  const [location, setLocation] = useState("");
  const [temperature, setTemperature] = useState("");
  const [humidity, setHumidity] = useState("");
  const [severity, setSeverity] = useState("normal");
  const [message, setMessage] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await simulateSensor({
        sensor_id: sensorId,
        location,
        temperature: parseFloat(temperature),
        humidity: parseFloat(humidity),
        severity,
      });
      setMessage("Симуляция отправлена!");
      setSensorId("");
      setLocation("");
      setTemperature("");
      setHumidity("");
      setSeverity("normal");
    } catch {
      setMessage("Ошибка при отправке");
    }
  };

  return (
    <div className="sensor-collapsible">
      <button
        className="toggle-button"
        onClick={() => setOpen(!open)}
      >
        {open ? "Скрыть форму симуляции" : "Симулировать датчик"}
      </button>

      <div className={`sensor-form-wrapper ${open ? "open" : ""}`}>
        {open && (
          <form onSubmit={handleSubmit} className="sensor-form">
            <h2>Симулировать датчик</h2>
            <input
              type="text"
              placeholder="Sensor ID"
              value={sensorId}
              onChange={(e) => setSensorId(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="Location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              required
            />
            <input
              type="number"
              placeholder="Temperature"
              value={temperature}
              onChange={(e) => setTemperature(e.target.value)}
              required
            />
            <input
              type="number"
              placeholder="Humidity"
              value={humidity}
              onChange={(e) => setHumidity(e.target.value)}
              required
            />
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value)}
            >
              <option value="normal">Normal</option>
              <option value="warning">Warning</option>
              <option value="critical">Critical</option>
            </select>
            <button type="submit">Отправить</button>
            {message && <div className="message">{message}</div>}
          </form>
        )}
      </div>
    </div>
  );
}