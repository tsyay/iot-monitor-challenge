import React from "react";

export default function Header({ events }) {
  const total = events.length;

  // Все события за сегодня
  const todayEvents = events.filter(
    (e) => new Date(e.created_at).toDateString() === new Date().toDateString(),
  );
  const totalToday = todayEvents.length;

  // Critical за сегодня
  const criticalToday = todayEvents.filter((e) =>
    e.severity
      .split(",")
      .map((s) => s.trim())
      .includes("critical"),
  ).length;
  // Последнее событие
  const lastEvent = events[events.length - 1];

  return (
    <div className="cards">
      <div className="card">
        <h3>Всего событий</h3>
        <span>{total}</span>
      </div>
      <div className="card">
        <h3>Событий за сегодня</h3>
        <span>{totalToday}</span>
      </div>
      <div className="card">
        <h3>Critical за сегодня</h3>
        <span>{criticalToday}</span>
      </div>
      <div className="card">
        <h3>Последнее событие</h3>
        <span>
          {lastEvent
            ? `${lastEvent.sensor_id} — ${lastEvent.severity}`
            : "Нет данных"}
        </span>
      </div>
    </div>
  );
}
