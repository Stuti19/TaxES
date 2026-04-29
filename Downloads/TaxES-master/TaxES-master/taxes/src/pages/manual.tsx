import React, { useState, useEffect } from "react";

interface Field {
  id: string;
  label: string;
  type: string;
  options?: string[];
  required?: boolean;
}

const idGen = () => "f_" + Math.random().toString(36).slice(2, 9);

const defaultFields: Field[] = [
  { id: idGen(), label: "Assessment Year (AY)", type: "select", options: ["2024-25", "2025-26", "2026-27"], required: true },
  { id: idGen(), label: "Filing Section & Type", type: "select", options: ["Original - 139(1)", "Revised - 139(5)"], required: true },
  { id: idGen(), label: "Residential Status", type: "select", options: ["Resident", "Non-Resident", "RNOR"], required: false },
  { id: idGen(), label: "Tax Regime", type: "select", options: ["Old Regime", "New Regime"], required: false },
  { id: idGen(), label: "Email ID", type: "email", required: true },
  { id: idGen(), label: "Mobile Number", type: "tel", required: true },
  { id: idGen(), label: "Father's Name", type: "text", required: false },
  { id: idGen(), label: "Employment Category", type: "select", options: ["Government Employee", "Private Employee", "Self Employed", "Freelancer", "Others"], required: false },
  { id: idGen(), label: "Income from Other Sources", type: "number", required: false },
  { id: idGen(), label: "House Property Income or Loss", type: "number", required: false },
  { id: idGen(), label: "Section 80 Deductions", type: "number", required: false },
  { id: idGen(), label: "Relief u/s 89", type: "number", required: false },
];

const Manual: React.FC = () => {
  const [fields, setFields] = useState<Field[]>([]);
  const [previewVisible, setPreviewVisible] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newField, setNewField] = useState<{ label: string; type: string; options: string }>({
    label: "",
    type: "text",
    options: "",
  });
  const [formData, setFormData] = useState<Record<string, string>>({});

  useEffect(() => {
    setFields(defaultFields);
  }, []);

  const handleInputChange = (id: string, value: string) => {
    setFormData((prev) => ({ ...prev, [id]: value }));
  };

  const addField = () => {
    const label = newField.label.trim();
    if (!label) return alert("Please enter a label");

    const options = newField.options
      .split(",")
      .map((s) => s.trim())
      .filter(Boolean);

    const newF: Field = {
      id: idGen(),
      label,
      type: newField.type,
      options: options.length ? options : undefined,
      required: false,
    };

    setFields((prev) => [...prev, newF]);
    setShowModal(false);
    setNewField({ label: "", type: "text", options: "" });
  };

  const removeField = (id: string) => {
    if (!confirm("Delete this field?")) return;
    setFields((prev) => prev.filter((f) => f.id !== id));
  };

  const editLabel = (id: string) => {
    const newLabel = prompt("Enter new label:");
    if (!newLabel) return;
    setFields((prev) => prev.map((f) => (f.id === id ? { ...f, label: newLabel } : f)));
  };

  const resetForm = () => {
    if (!confirm("Reset form and restore defaults?")) return;
    setFields(defaultFields);
    setFormData({});
  };

  const submitForm = () => {
    const requiredFields = fields.filter((f) => f.required);
    for (let rf of requiredFields) {
      if (!formData[rf.id]) {
        alert(`Please fill required field: ${rf.label}`);
        return;
      }
    }

    const summary = fields
      .map((f) => `• ${f.label}: ${formData[f.id] || "<empty>"}`)
      .join("\n");

    alert("Form saved (demo):\n\n" + summary);
  };

  const exportHTML = () => {
    const formHTML = fields
      .map((f) => {
        if (f.type === "select") {
          const opts = (f.options || [])
            .map((o) => `<option>${o}</option>`)
            .join("");
          return `<div style="margin-bottom:12px"><label style="font-weight:600">${f.label}</label><select style="width:100%;padding:8px;border-radius:6px;border:1px solid #e6eefc">${opts}</select></div>`;
        } else if (f.type === "textarea") {
          return `<div style="margin-bottom:12px"><label style="font-weight:600">${f.label}</label><textarea rows="3" style="width:100%;padding:8px;border-radius:6px;border:1px solid #e6eefc"></textarea></div>`;
        } else {
          return `<div style="margin-bottom:12px"><label style="font-weight:600">${f.label}</label><input type="${f.type}" style="width:100%;padding:8px;border-radius:6px;border:1px solid #e6eefc"/></div>`;
        }
      })
      .join("");

    const exportHTML = `<!doctype html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>Exported TaxES Form</title></head><body style="font-family:Inter,system-ui,Arial;margin:20px"><h2>Exported TaxES Form</h2><form>${formHTML}<div style="margin-top:18px"><button type="button" onclick="alert('Submitted (demo)')">Submit</button></div></form></body></html>`;

    const blob = new Blob([exportHTML], { type: "text/html" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "taxes_exported_form.html";
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div style={{ fontFamily: "Inter, system-ui, Arial", background: "#f8fafc", color: "#0f172a", minHeight: "100vh" }}>
      {/* Header */}
      <header
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "18px 28px",
          background: "#fff",
          borderBottom: "1px solid #eef2f7",
          boxShadow: "0 3px 10px rgba(2,6,23,0.03)",
          position: "sticky",
          top: 0,
          zIndex: 10,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <div
            style={{
              width: "36px",
              height: "36px",
              background: "linear-gradient(135deg,#2563eb,#06b6d4)",
              borderRadius: "8px",
              display: "grid",
              placeItems: "center",
              color: "white",
              fontWeight: 700,
            }}
          >
            TP
          </div>
          <div>
            <div style={{ fontSize: "1.1rem", color: "#1d4ed8", fontWeight: 700 }}>TaxES Pro</div>
            <div style={{ fontSize: "0.85rem", color: "#64748b" }}>Professional Dashboard</div>
          </div>
        </div>
        <nav>
          <button onClick={exportHTML} style={{ marginRight: "8px" }}>
            Export HTML
          </button>
          <button onClick={resetForm}>Reset</button>
        </nav>
      </header>

      {/* Main Layout */}
      <main style={{ maxWidth: "1100px", margin: "28px auto", padding: "22px", display: "grid", gridTemplateColumns: "1fr 360px", gap: "24px" }}>
        {/* Form Section */}
        <section style={{ background: "#fff", borderRadius: "12px", padding: "18px", boxShadow: "0 6px 24px rgba(15,23,42,0.04)" }}>
          <h2 style={{ color: "#1d4ed8" }}>Manual ITR Details — Dynamic Editor</h2>

          <div style={{ display: "flex", alignItems: "center", gap: "10px", flexWrap: "wrap", marginBottom: "12px" }}>
            <button onClick={() => setShowModal(true)} style={{ background: "linear-gradient(90deg,#10b981,#059669)", color: "white", border: 0, padding: "8px 12px", borderRadius: "10px" }}>
              + Add Field
            </button>
            <button onClick={() => setPreviewVisible(!previewVisible)}>Toggle Preview</button>
            <div style={{ flex: 1 }}></div>
            <span style={{ color: "#64748b", fontSize: "0.9rem" }}>
              Tip: click ✏️ icon to edit label. Add field to create custom inputs.
            </span>
          </div>

          <form onSubmit={(e) => e.preventDefault()}>
            {fields.map((field) => (
              <div key={field.id} style={{ marginBottom: "12px", position: "relative" }}>
                <label style={{ fontWeight: 600 }}>{field.label}</label>
                <div style={{ position: "absolute", right: 10, top: 5, display: "flex", gap: 6 }}>
                  <button type="button" onClick={() => editLabel(field.id)}>
                    ✏️
                  </button>
                  <button type="button" onClick={() => removeField(field.id)}>
                    🗑️
                  </button>
                </div>

                {field.type === "select" ? (
                  <select
                    style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #e2e8f0" }}
                    onChange={(e) => handleInputChange(field.id, e.target.value)}
                  >
                    {field.options?.map((opt) => (
                      <option key={opt}>{opt}</option>
                    ))}
                  </select>
                ) : field.type === "textarea" ? (
                  <textarea
                    rows={3}
                    style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #e2e8f0" }}
                    onChange={(e) => handleInputChange(field.id, e.target.value)}
                  ></textarea>
                ) : (
                  <input
                    type={field.type}
                    style={{ width: "100%", padding: "10px", borderRadius: "8px", border: "1px solid #e2e8f0" }}
                    onChange={(e) => handleInputChange(field.id, e.target.value)}
                  />
                )}
              </div>
            ))}
          </form>

          <div style={{ marginTop: "14px", textAlign: "right" }}>
            <button
              onClick={submitForm}
              style={{ background: "linear-gradient(90deg,#10b981,#059669)", color: "white", border: 0, padding: "8px 12px", borderRadius: "10px" }}
            >
              Save Details
            </button>
          </div>
        </section>

        {/* Sidebar Preview */}
        <aside>
          <div style={{ background: "#fff", borderRadius: "12px", padding: "16px", border: "1px solid #eef2f7" }}>
            <h3 style={{ color: "#064e3b" }}>Form Preview / Editor</h3>
            {previewVisible && (
              <div style={{ background: "#f7fbff", padding: "12px", borderRadius: "8px", minHeight: "220px", border: "1px dashed #e6eefc" }}>
                {fields.length === 0 ? (
                  <div style={{ color: "#64748b", textAlign: "center" }}>No fields yet — add a field to begin.</div>
                ) : (
                  fields.map((f) => (
                    <div
                      key={f.id}
                      style={{ display: "flex", justifyContent: "space-between", padding: "6px 4px", borderBottom: "1px dashed #eef2f7" }}
                    >
                      <strong>{f.label}</strong>
                      <span style={{ opacity: 0.8 }}>{formData[f.id] || "<empty>"}</span>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
        </aside>
      </main>

      {/* Modal */}
      {showModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(3,7,18,0.45)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 60,
          }}
        >
          <div style={{ background: "#fff", padding: "18px", borderRadius: "12px", width: "520px", maxWidth: "92%" }}>
            <h3>Add New Field</h3>
            <p style={{ color: "#64748b", marginBottom: "12px" }}>Create a new field manually. Changes affect the DOM immediately.</p>

            <label>Field Label</label>
            <input
              type="text"
              placeholder="e.g. Assessment Year (AY)"
              value={newField.label}
              onChange={(e) => setNewField({ ...newField, label: e.target.value })}
              style={{ width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "10px" }}
            />

            <label>Type</label>
            <select
              value={newField.type}
              onChange={(e) => setNewField({ ...newField, type: e.target.value })}
              style={{ width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "10px" }}
            >
              <option value="text">Text</option>
              <option value="number">Number</option>
              <option value="email">Email</option>
              <option value="tel">Phone</option>
              <option value="select">Select</option>
              <option value="textarea">Textarea</option>
            </select>

            {newField.type === "select" && (
              <>
                <label>Options (comma separated)</label>
                <input
                  type="text"
                  placeholder="Option1,Option2,Option3"
                  value={newField.options}
                  onChange={(e) => setNewField({ ...newField, options: e.target.value })}
                  style={{ width: "100%", padding: "8px", borderRadius: "8px", border: "1px solid #e2e8f0", marginBottom: "10px" }}
                />
              </>
            )}

            <div style={{ display: "flex", justifyContent: "flex-end", gap: "8px" }}>
              <button onClick={() => setShowModal(false)}>Cancel</button>
              <button
                onClick={addField}
                style={{ background: "linear-gradient(90deg,#10b981,#059669)", color: "white", border: 0, padding: "8px 12px", borderRadius: "10px" }}
              >
                Create Field
              </button>
            </div>
          </div>
        </div>
      )}

      <footer style={{ textAlign: "center", margin: "20px", color: "#64748b", fontSize: "0.92rem" }}>
        © 2025 TaxES Pro — Professional & Editable Form
      </footer>
    </div>
  );
};

export default Manual;
