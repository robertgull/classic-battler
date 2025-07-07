import { useState } from 'react'

const petTypes = [
  "Aquatic", "Beast", "Critter", "Dragonkin", "Elemental",
  "Flying", "Humanoid", "Magic", "Mechanical", "Undead"
];

function App() {
  const [petId, setPetId] = useState("");
  const [pet, setPet] = useState<any>(null);

  const [petType, setPetType] = useState(petTypes[0]);
  const [results, setResults] = useState<any[]>([]);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Fetch single pet by ID
  async function fetchPetById() {
    setLoading(true);
    setError("");
    setPet(null);
    try {
      const response = await fetch(`http://127.0.0.1:8000/battle_pets/get_by_id?_id=${encodeURIComponent(petId)}`);
      if (!response.ok) throw new Error(`Status ${response.status}`);
      const data = await response.json();
      setPet(data);
    } catch (e: any) {
      setError(e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  // Fetch double counter pets
  async function fetchDoubleCounters() {
    setLoading(true);
    setError("");
    setResults([]);
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/battle_pets/list_double_counters?_type=${encodeURIComponent(petType)}`
      );
      if (!response.ok) throw new Error(`Status ${response.status}`);
      const data = await response.json();
      setResults(data);
    } catch (e: any) {
      setError(e.message || "Unknown error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ padding: 32 }}>
      <h1>Battle Pet Lookup</h1>

      {/* Lookup by ID */}
      <div style={{ marginBottom: 24 }}>
        <input
          type="number"
          value={petId}
          onChange={e => setPetId(e.target.value)}
          placeholder="Enter pet ID"
        />
        <button onClick={fetchPetById} disabled={loading || !petId}>
          {loading ? "Loading..." : "Get Pet By ID"}
        </button>
      </div>
      {pet && (
        <div style={{ marginTop: 16 }}>
          <h2>Pet Details</h2>
          <pre>{JSON.stringify(pet, null, 2)}</pre>
        </div>
      )}

      <hr style={{ margin: "32px 0" }} />

      {/* Double Counter Search */}
      <div style={{ marginBottom: 24 }}>
        <label>
          Pet Type:{" "}
          <select value={petType} onChange={e => setPetType(e.target.value)}>
            {petTypes.map(pt => (
              <option key={pt} value={pt}>{pt}</option>
            ))}
          </select>
        </label>
        <button onClick={fetchDoubleCounters} disabled={loading}>
          {loading ? "Loading..." : "Find Double Counters"}
        </button>
      </div>
      {results.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <h2>Double Counter Pets</h2>
          <ul>
            {results.map(pet => (
                  <li key={pet.id}>
                     <a
                         href={`https://www.wowhead.com/mop-classic/npc=${pet.id}`}
                         target="_blank"
                         rel="noopener noreferrer"
                     >
                      <strong>{pet.name}</strong> ({pet.type})
                     </a>
                  </li>
            ))}
          </ul>
        </div>
      )}

      {error && <div style={{ color: "red", marginTop: 16 }}>Error: {error}</div>}
    </div>
  );
}

export default App;
