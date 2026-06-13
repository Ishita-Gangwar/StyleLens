import { useMemo, useState } from "react";
import "./index.css";

type SearchResult = {
  rank: number;
  id: number;
  image_path: string;
  image_url: string;
  distance: number;
  product_name: string;
  gender: string;
  master_category: string;
  sub_category: string;
  article_type: string;
  base_colour: string;
  season: string;
  usage: string;
};

const API_BASE = "http://127.0.0.1:8000";
const FALLBACK_IMAGE = "https://via.placeholder.com/400x500?text=Image+Unavailable";

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [k, setK] = useState(5);
  const [isDragging, setIsDragging] = useState(false);

  const previewUrl = useMemo(() => {
    if (!file) return "";
    return URL.createObjectURL(file);
  }, [file]);

  const clearSearch = () => {
    setFile(null);
    setResults([]);
    setError("");
    setK(5);
    setIsDragging(false);
  };

  const setSelectedFile = (selected: File | null) => {
    if (!selected) return;

    if (!selected.type.startsWith("image/")) {
      setError("Please select a valid image file.");
      setFile(null);
      setResults([]);
      return;
    }

    setError("");
    setFile(selected);
    setResults([]);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selected = e.target.files?.[0] || null;
    setSelectedFile(selected);
  };

  const handleSearch = async () => {
    if (!file) {
      setError("Please choose an image first.");
      return;
    }

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/search?k=${k}`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Search failed.");
      }

      setResults(data.results || []);
    } catch (err) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLLabelElement>) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files?.[0] || null;
    setSelectedFile(droppedFile);
  };

  const handleImageError = (e: React.SyntheticEvent<HTMLImageElement, Event>) => {
    e.currentTarget.onerror = null;
    e.currentTarget.src = FALLBACK_IMAGE;
  };

  return (
    <div className="page">
      <div className="container">
        <header className="hero">
          <p className="eyebrow">StyleLens</p>
          <h1>Find similar fashion items from one image.</h1>
          <p className="subtitle">
            Upload or drop an image, choose how many matches you want, and explore similar products from your indexed fashion dataset.
          </p>
        </header>

        <section className="panel upload-panel">
          <div className="left">
            <label
              className={`upload-box ${isDragging ? "dragging" : ""}`}
              onDragOver={handleDragOver}
              onDragEnter={handleDragOver}
              onDragLeave={handleDragLeave}
              onDrop={handleDrop}
            >
              <input type="file" accept="image/*" onChange={handleFileChange} />
              <span>{file ? "Change image" : "Select or drop image"}</span>
            </label>

            <div className="control-group">
              <label htmlFor="k-select" className="control-label">
                Number of results
              </label>
              <select
                id="k-select"
                className="select-box"
                value={k}
                onChange={(e) => setK(Number(e.target.value))}
              >
                <option value={3}>3</option>
                <option value={5}>5</option>
                <option value={8}>8</option>
                <option value={10}>10</option>
              </select>
            </div>

            <div className="button-row">
              <button className="search-btn" onClick={handleSearch} disabled={loading}>
                {loading ? "Searching..." : "Search similar items"}
              </button>

              <button className="clear-btn" onClick={clearSearch} type="button">
                Clear
              </button>
            </div>

            {file && <p className="file-name">Selected: {file.name}</p>}
            {error && <p className="error">{error}</p>}
          </div>

          <div className="right">
            {previewUrl ? (
              <img
                className="preview"
                src={previewUrl}
                alt="Selected preview"
                onError={handleImageError}
              />
            ) : (
              <div className="preview placeholder">
                Drag and drop an image here or use the file picker
              </div>
            )}
          </div>
        </section>

        <section className="panel">
          <div className="results-head">
            <h2>Results</h2>
            <span>{results.length} items</span>
          </div>

          {results.length === 0 ? (
            <div className="empty-state">
              No results yet. Upload an image and run a search.
            </div>
          ) : (
            <div className="results-grid">
              {results.map((item) => (
                <article className="card" key={`${item.id}-${item.rank}`}>
                  <img
                    className="result-image"
                    src={item.image_url}
                    alt={item.product_name || `Match ${item.rank}`}
                    onError={handleImageError}
                  />

                  <div className="card-body">
                    <h3 className="product-title">
                      {item.product_name || `Item ${item.id}`}
                    </h3>

                    <p className="meta">
                      {item.article_type || "Unknown type"}
                      {item.base_colour ? ` · ${item.base_colour}` : ""}
                    </p>

                    <p className="meta">
                      {item.gender || "Unknown"}
                      {item.usage ? ` · ${item.usage}` : ""}
                    </p>

                    <p className="meta">
                      {item.master_category || ""}
                      {item.sub_category ? ` · ${item.sub_category}` : ""}
                    </p>

                    <p className="meta">
                      {item.season ? `Season: ${item.season}` : "Season: N/A"}
                    </p>

                    <p className="score">Similarity score: {item.distance.toFixed(4)}</p>
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}

export default App;