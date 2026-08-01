import { useRef, useState } from "react";
import { uploadFile } from "../api/client";

export default function FileUpload({ onUploaded, onError }) {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;
    setUploading(true);
    try {
      const result = await uploadFile(file);
      onUploaded(result);
    } catch (err) {
      onError(err.message);
    } finally {
      setUploading(false);
    }
  }

  return (
    <div
      className={`dropzone ${dragOver ? "dropzone--active" : ""}`}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFile(e.dataTransfer.files[0]);
      }}
      onClick={() => inputRef.current?.click()}
    >
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.tsv,.xlsx,.xls"
        hidden
        onChange={(e) => handleFile(e.target.files[0])}
      />
      {uploading ? (
        <p>Uploading & parsing dataset...</p>
      ) : (
        <>
          <p className="dropzone__title">Drop a CSV / TSV / XLSX file here</p>
          <p className="dropzone__hint">or click to browse</p>
        </>
      )}
    </div>
  );
}
