import React from "react";

export default function Header({ events }) {
  const total = events.length;
  const criticalToday = events.filter(
    (e) =>
      e.severity === "critical" &&
      new Date(e.created_at).toDateString() === new Date().toDateString()
  ).length;
  const lastEvent = events[events.length - 1];

  return (
    <div className="cards">
      <div className="card">
        <h3>Всего событий</h3>
        <span>{total}</span>
      </div>
      <div className="card">
        <h3>Critical за сегодня</h3>
        <span>{criticalToday}</span>
      </div>
      <div className="card">
        <h3>Последнее событие</h3>
        <span>{lastEvent ? `${lastEvent.sensor_id} (${lastEvent.severity})` : "-"}</span>
      </div>
    </div>
  );
}