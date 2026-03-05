import React, { useState, useEffect } from "react";
import Header from "./components/Header";
import Filters from "./components/Filters";
import EventsTable from "./components/EventsTable";
import SimulateSensor from "./components/SimulateSensor";
import "./App.css";

// API
async function fetchEvents() {
  const res = await fetch("/api/events");
  if (!res.ok) throw new Error("Ошибка загрузки событий");
  return res.json();
}

export default function App() {
  const [events, setEvents] = useState([]);
  const [filters, setFilters] = useState({
    severity: "all",
    sensor_id: "",
    dateFrom: "",
    dateTo: "",
  });

  // Функция для загрузки данных
  const loadData = async () => {
    try {
      const data = await fetchEvents();
      setEvents(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    // Принудительная загрузка при монтировании
    loadData();

    //const interval = setInterval(loadData, 120000); // 120000 мс = 2 минуты

    const interval = setInterval(loadData, 3000); // 3000 = 3 секунды

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="app-container">
      <h1>IoT Monitor</h1>
      <Header events={events} />
      <Filters filters={filters} setFilters={setFilters} />
      <EventsTable events={events} filters={filters} />
      <SimulateSensor />
    </div>
  );
}