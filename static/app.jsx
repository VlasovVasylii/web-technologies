const { useState, useEffect, useCallback, useMemo } = React;

const API = "/api/cars";

// ==================================================================
// Утилиты
// ==================================================================

function escapeXml(s) {
  return String(s ?? "").replace(/[<>&'"]/g, (c) =>
    ({ "<": "&lt;", ">": "&gt;", "&": "&amp;", "'": "&apos;", '"': "&quot;" }[c])
  );
}

function makeCarImageDataUrl(car) {
  const COLOR_HEX = {
    red: "#ef4444", black: "#1f2937", white: "#f3f4f6",
    gray: "#9ca3af", grey: "#9ca3af", silver: "#d1d5db",
    blue: "#3b82f6", yellow: "#eab308", orange: "#f97316",
    brown: "#92400e", green: "#22c55e",
  };
  const key = (car.color || "").toLowerCase();
  const bg = COLOR_HEX[key] || "#6b7280";
  const isLight = ["white", "silver", "yellow"].includes(key);
  const fg = isLight ? "#1f2937" : "#ffffff";

  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="320" height="140">` +
      `<rect width="320" height="140" fill="${bg}"/>` +
      `<text x="160" y="66" font-family="Arial,sans-serif" font-size="20" ` +
        `fill="${fg}" text-anchor="middle" font-weight="bold">${escapeXml(car.firm)}</text>` +
      `<text x="160" y="92" font-family="Arial,sans-serif" font-size="14" ` +
        `fill="${fg}" text-anchor="middle">${escapeXml(car.model)}</text>` +
      `<text x="160" y="116" font-family="Arial,sans-serif" font-size="12" ` +
        `fill="${fg}" text-anchor="middle" opacity="0.8">${escapeXml(car.year)}</text>` +
    `</svg>`;

  return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

async function apiFetch(url, options = {}) {
  const response = await fetch(url, options);
  if (!response.ok) {
    let detail = null;
    try { detail = (await response.json()).detail; } catch {}
    const err = new Error(detail || `HTTP ${response.status}`);
    err.status = response.status;
    throw err;
  }
  if (response.status === 204) return null;
  return await response.json();
}

// ==================================================================
// Компоненты
// ==================================================================

function Message({ text, kind }) {
  if (!text) return null;
  const cls = kind === "error" ? "danger" : kind === "warn" ? "warning" : "success";
  return <div className={`alert alert-${cls} mb-3`} role="alert">{text}</div>;
}

function Toolbar({ onRefresh, searchId, setSearchId, onSearch }) {
  return (
    <div className="d-flex flex-column flex-sm-row gap-2 mb-3">
      <button className="btn btn-outline-primary" onClick={onRefresh}>Показать все</button>
      <form
        className="d-flex gap-2 flex-grow-1"
        onSubmit={(e) => { e.preventDefault(); onSearch(searchId); }}
      >
        <input
          type="number" min="1" className="form-control"
          placeholder="ID автомобиля"
          value={searchId}
          onChange={(e) => setSearchId(e.target.value)}
        />
        <button type="submit" className="btn btn-primary">Найти</button>
      </form>
    </div>
  );
}

function CarCard({ car, onEdit, onDelete }) {
  const imgSrc = useMemo(() => makeCarImageDataUrl(car), [car]);
  return (
    <div className="col-12 col-sm-6 col-lg-4">
      <div className="card h-100 shadow-sm">
        <img src={imgSrc} className="card-img-top car-image"
             alt={`${car.firm} ${car.model}`} />
        <div className="card-body d-flex flex-column">
          <h5 className="card-title">{car.firm} {car.model} ({car.year})</h5>
          <ul className="list-unstyled small mb-2">
            <li><span className="text-muted">Мощность:</span> {car.power} л.с.</li>
            <li><span className="text-muted">Цвет:</span> {car.color}</li>
            <li><span className="text-muted">Цена:</span> ${car.price.toLocaleString("ru-RU")}</li>
            <li><span className="text-muted">ID дилера:</span> {car.dealer_id ?? "не привязан"}</li>
          </ul>
          <div className="mt-auto d-flex gap-2">
            <button className="btn btn-sm btn-outline-primary flex-fill"
                    onClick={() => onEdit(car)}>Изменить</button>
            <button className="btn btn-sm btn-outline-danger flex-fill"
                    onClick={() => onDelete(car)}>Удалить</button>
          </div>
        </div>
      </div>
    </div>
  );
}

function EditModal({ car, onClose, onSave }) {
  const [form, setForm] = useState(car);
  useEffect(() => { setForm(car); }, [car]);
  const change = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const submit = (e) => {
    e.preventDefault();
    onSave({
      ...form,
      year: Number(form.year),
      power: Number(form.power),
      price: Number(form.price),
      dealer_id: form.dealer_id === "" || form.dealer_id === null || form.dealer_id === undefined
        ? null : Number(form.dealer_id),
    });
  };

  const fields = [
    ["firm", "Марка", "text", true],
    ["model", "Модель", "text", true],
    ["year", "Год", "number", true],
    ["power", "Мощность, л.с.", "number", true],
    ["color", "Цвет", "text", true],
    ["price", "Цена, $", "number", true],
    ["dealer_id", "ID дилера (пусто — не привязан)", "number", false],
  ];

  return (
    <>
      <div className="modal fade show d-block" tabIndex="-1" onClick={onClose}>
        <div className="modal-dialog modal-dialog-scrollable"
             onClick={(e) => e.stopPropagation()}>
          <div className="modal-content">
            <form onSubmit={submit}>
              <div className="modal-header">
                <h5 className="modal-title">Редактировать автомобиль</h5>
                <button type="button" className="btn-close" onClick={onClose}></button>
              </div>
              <div className="modal-body">
                {fields.map(([field, label, type, required]) => (
                  <div className="mb-2" key={field}>
                    <label className="form-label small text-muted">{label}</label>
                    <input
                      type={type} className="form-control"
                      value={form[field] ?? ""}
                      onChange={change(field)}
                      required={required}
                    />
                  </div>
                ))}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={onClose}>Отмена</button>
                <button type="submit" className="btn btn-primary">Сохранить</button>
              </div>
            </form>
          </div>
        </div>
      </div>
      <div className="modal-backdrop fade show"></div>
    </>
  );
}

function App() {
  const [cars, setCars] = useState([]);
  const [message, setMessage] = useState({ text: "", kind: "info" });
  const [searchId, setSearchId] = useState("");
  const [editing, setEditing] = useState(null);
  const [listMode, setListMode] = useState("all");

  const showMessage = useCallback((text, kind = "info") => {
    setMessage({ text, kind });
    if (text) {
      setTimeout(() => {
        setMessage((m) => (m.text === text ? { text: "", kind: "info" } : m));
      }, 4000);
    }
  }, []);

  const loadAllCars = useCallback(async () => {
    try {
      const data = await apiFetch(API);
      setCars(data);
      setListMode("all");
      showMessage(`Загружено автомобилей: ${data.length}`, "info");
    } catch (e) {
      setCars([]);
      showMessage("Ошибка загрузки: " + e.message, "error");
    }
  }, [showMessage]);

  useEffect(() => { loadAllCars(); }, [loadAllCars]);

  const handleSearch = async (value) => {
    const id = Number(value);
    if (!id) return;
    try {
      const car = await apiFetch(`${API}/${id}`);
      setCars([car]);
      setListMode("search");
      showMessage(`Найден автомобиль с ID = ${id}`, "info");
    } catch (e) {
      if (e.status === 404) {
        setCars([]);
        setListMode("search");
        showMessage(`Автомобиль с ID = ${id} не найден.`, "warn");
      } else {
        showMessage("Ошибка поиска: " + e.message, "error");
      }
    }
  };

  const handleDelete = async (car) => {
    if (!window.confirm(`Удалить ${car.firm} ${car.model}?`)) return;
    try {
      await apiFetch(`${API}/${car.id}`, { method: "DELETE" });
      showMessage(`Автомобиль ID=${car.id} удалён.`, "info");
      await loadAllCars();
    } catch (e) {
      if (e.status === 404) showMessage("Автомобиль уже удалён.", "warn");
      else showMessage("Ошибка удаления: " + e.message, "error");
    }
  };

  const handleSave = async (car) => {
    try {
      await apiFetch(`${API}/${car.id}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          firm: car.firm, model: car.model, year: car.year,
          power: car.power, color: car.color, price: car.price,
          dealer_id: car.dealer_id,
        }),
      });
      setEditing(null);
      showMessage(`Автомобиль ID=${car.id} обновлён.`, "info");
      await loadAllCars();
    } catch (e) {
      if (e.status === 400) showMessage("Некорректный dealer_id.", "error");
      else if (e.status === 404) showMessage("Автомобиль не найден.", "error");
      else showMessage("Ошибка обновления: " + e.message, "error");
    }
  };

  return (
    <div>
      <nav className="navbar navbar-dark bg-primary mb-4">
        <div className="container">
          <span className="navbar-brand mb-0 h1">Каталог автомобилей</span>
        </div>
      </nav>

      <main className="container pb-5">
        <Toolbar
          onRefresh={loadAllCars}
          searchId={searchId}
          setSearchId={setSearchId}
          onSearch={handleSearch}
        />
        <Message text={message.text} kind={message.kind} />

        {cars.length === 0 ? (
          <div className="text-center text-muted py-5">
            {listMode === "search"
              ? "По вашему запросу ничего не найдено."
              : "В каталоге пока нет автомобилей."}
          </div>
        ) : (
          <div className="row g-3">
            {cars.map((car) => (
              <CarCard key={car.id} car={car}
                       onEdit={setEditing} onDelete={handleDelete} />
            ))}
          </div>
        )}
      </main>

      {editing && (
        <EditModal car={editing} onClose={() => setEditing(null)} onSave={handleSave} />
      )}
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);